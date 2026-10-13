# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo.exceptions import ValidationError
from openupgradelib import openupgrade, openupgrade_merge_records
from psycopg2 import sql

QUANT_MERGE_OPS = {
    # The rest of the values are good with default merge operation
    'in_date': 'min',
    'removal_date': 'max',
}


def _check_recurrence_once_per_model(foreign_keys):
    """openupgrade_merge_records._check_recurrence (same queries, same test),
    except that the foreign keys of the model, looked up in
    information_schema, are read once instead of once per merge: they do not
    change while records are merged (makmur: 11,304 groups of quants, 24
    minutes, that query alone 44% of the time).
    """
    logger = openupgrade_merge_records.logger

    def check_recurrence(env, model_name, record_ids, target_record_id,
                         model_table=None):
        if not model_table:
            try:
                model_table = env[model_name]._table
            except KeyError:
                model_table = openupgrade_merge_records.get_model2table(
                    model_name)
        key = (model_name, model_table)
        if key not in foreign_keys:
            env.cr.execute(
                """
                SELECT tc.table_name, kcu.column_name, COALESCE(imf.column1, 'id')
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                JOIN ir_model_fields AS imf
                    ON imf.model = %s AND imf.relation = imf.model AND ((
                        imf.name = kcu.column_name AND
                        tc.table_name = ccu.table_name) OR (
                        imf.column2 = kcu.column_name AND
                        tc.table_name = imf.relation_table))
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND ccu.table_name = %s and ccu.column_name = 'id'
                """,
                (model_name, model_table),
            )
            foreign_keys[key] = env.cr.fetchall()
        for table, column, origin in foreign_keys[key]:
            query = sql.SQL(
                """SELECT {column} FROM {table}
                WHERE {origin} = %(target_record_id)s"""
            ).format(
                table=sql.Identifier(table),
                column=sql.Identifier(column),
                origin=sql.Identifier(origin),
            )
            env.cr.execute(query, {"target_record_id": target_record_id})
            new_parent_row = env.cr.fetchall()
            if new_parent_row and new_parent_row[0] in record_ids:
                logger.info(
                    "Couldn't merge %s record(s) of model %s to record_id %s"
                    " to avoid recursion with field %s of table %s",
                    len(record_ids),
                    model_name,
                    target_record_id,
                    origin,
                    table,
                )
                return True
        return False

    return check_recurrence


def _memoize_field_searches(env):
    """Make ir.model.fields remember its searches while quants are merged.

    For every group of quants merge_records looks up the fields that point to
    stock.quant (many2one, many2many, reference: _change_*_refs_orm) and the
    unlink of the merged quants does it again (ir.default.discard_records,
    field_id.ttype / field_id.relation): the same searches of
    ir_model_fields, a quarter of the time of the merge (makmur: 15,167
    merges). No field is created or deleted while quants are merged: the
    results do not change. Returns the function to restore.
    """
    cls = type(env['ir.model.fields'])
    had_own = '_search' in cls.__dict__
    original = cls._search
    memo = {}

    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        key = (repr(args), offset, limit, order, count, access_rights_uid,
               self.env.uid, repr(sorted(self.env.context.items())))
        if key not in memo:
            memo[key] = original(
                self, args, offset=offset, limit=limit, order=order,
                count=count, access_rights_uid=access_rights_uid)
        result = memo[key]
        return list(result) if isinstance(result, list) else result

    cls._search = _search

    def restore():
        if had_own:
            cls._search = original
        else:
            del cls._search
    return restore


def merge_quants(env):
    logger = logging.getLogger('openupgrade.stock.end_migration')
    group_list = [
        'product_id', 'package_id', 'lot_id', 'location_id', 'owner_id',
    ]
    StockQuant = env['stock.quant']
    groups = StockQuant.read_group([], group_list, group_list, lazy=False)
    check_recurrence = openupgrade_merge_records._check_recurrence
    openupgrade_merge_records._check_recurrence = \
        _check_recurrence_once_per_model({})
    restore_field_search = _memoize_field_searches(env)
    try:
        for group in groups:
            quants = StockQuant.search(group['__domain'])
            if len(quants) == 1:
                continue
            try:
                with env.cr.savepoint():
                    openupgrade_merge_records.merge_records(
                        env, 'stock.quant', quants[1:].ids, quants[0].id,
                        QUANT_MERGE_OPS,
                    )
            except ValidationError as error:
                logger.error(
                    'Cannot merge quants %s for '
                    'product %s, package %s, lot %s, location %s, owner %s: %s',
                    quants.ids,
                    quants[0].product_id.default_code or quants[0].product_id.name,
                    quants[0].package_id.name or '-',
                    quants[0].lot_id.name or '-',
                    quants[0].location_id.complete_name,
                    quants[0].owner_id.name or '-',
                    error,
                )
    finally:
        openupgrade_merge_records._check_recurrence = check_recurrence
        restore_field_search()


def noupdate_obsolete_model_records(cr):
    """ Set noupdate = True for the obsolete model 'procurement.group' record,
    so when we upgrade 'stock' module later, this model record will not be deleted,
    which will raise error because this model is not declared in any python files.
    """
    models = [
        'procurement.order'
    ]
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET noupdate = TRUE
        WHERE model = 'ir.model' AND res_id IN (
            SELECT id FROM ir_model WHERE model IN %s
        )
        """,
        (tuple(models), )
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    merge_quants(env)
    noupdate_obsolete_model_records(env.cr)
