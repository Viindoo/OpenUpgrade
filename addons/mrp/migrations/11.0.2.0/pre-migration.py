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


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
    precompute_stock_move_line_done_move(cr)
