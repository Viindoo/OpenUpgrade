# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'ir_attachment': [
        ('priority', None),
    ],
    'stock_move': [
        ('quantity_done_store', None),
    ],
}


def precompute_stock_move_line_done_move(cr):
    """mrp 11.0 stores stock.move.line.done_move (related to the is_done of
    the move). Created by the ORM, the new column is computed line by line
    (makmur: 811,165 lines, 6 minutes); the same value is set here.
    """
    if not openupgrade.table_exists(cr, 'stock_move_line') or \
            openupgrade.column_exists(cr, 'stock_move_line', 'done_move'):
        return
    openupgrade.logged_query(
        cr, "ALTER TABLE stock_move_line ADD COLUMN done_move BOOLEAN")
    openupgrade.logged_query(
        cr, """UPDATE stock_move_line sml SET done_move = sm.is_done
        FROM stock_move sm WHERE sm.id = sml.move_id""")


def precreate_column(cr, table, column, sql_type, default):
    """Create a new column of a big table with the default value the ORM
    would fill in: the ORM adds the column then writes every existing row
    with one UPDATE, while PostgreSQL (11 and later) keeps the default of
    ADD COLUMN for the existing rows without writing them. default is the
    SQL literal of the value the ORM writes."""
    if not openupgrade.table_exists(cr, table) or \
            openupgrade.column_exists(cr, table, column):
        return False
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ADD COLUMN "%s" %s DEFAULT %s'
        % (table, column, sql_type, default))
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ALTER COLUMN "%s" DROP DEFAULT' % (table, column))
    return True


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
    precompute_stock_move_line_done_move(cr)
    # done_wo: the ORM writes its default on every move line (makmur: 811,165
    # lines, 1 minute)
    precreate_column(cr, 'stock_move_line', 'done_wo', 'boolean', 'true')
