# -*- coding: utf-8 -*-
# Copyright 2014 Microcom, Therp BV
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlids = [
    ('stock.view_partner_property_form', 'stock.view_partner_stock_form'),
]

column_renames = {
    'product_template': [
        ('loc_case', None),
        ('loc_rack', None),
        ('loc_row', None)
    ],
    'stock_pack_operation': [
        ('cost', None),
        ('currency', None),
        ('lot_id', None),
        ('processed', None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('stock.location', 'stock_location', 'loc_barcode', 'barcode'),
]


def fix_act_window(env):
    """Action window with XML-ID 'stock.action_procurement_compute' has
    set src_model='procurement.order' in v8, but in v9 it doesn't have
    src_model. So to avoid possible errors in future migrations, we empty
    that value before that happens, and remove the binding value.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_act_window iaw
        SET src_model = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = iaw.id
            AND imd.module = 'stock'
            AND imd.name = 'action_procurement_compute'""",
    )
    openupgrade.logged_query(
        env.cr, "DELETE FROM ir_values WHERE name='action_procurement_compute'",
    )


def precreate_column(cr, table, column, sql_type, default):
    """Create a new column of a big table with the default value the ORM
    would fill in: the ORM adds the column then writes every existing row
    with one UPDATE, while PostgreSQL (11 and later) keeps the default of
    ADD COLUMN for the existing rows without writing them. default is the
    SQL literal of the value the ORM writes (a float field with digits is
    written as text with its decimals: '1.00')."""
    if openupgrade.column_exists(cr, table, column):
        return
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ADD COLUMN "%s" %s DEFAULT %s'
        % (table, column, sql_type, default))
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ALTER COLUMN "%s" DROP DEFAULT' % (table, column))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlids)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    fix_act_window(env)
    # makmur: 1,676,359 moves, 2 minutes
    precreate_column(cr, 'stock_move', 'sequence', 'int4', 10)
