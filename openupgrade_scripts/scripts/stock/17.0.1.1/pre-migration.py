# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("stock.move", "stock_move", "quantity_done", "quantity"),
]

_column_copies = {
    "stock_move_line": [
        ("qty_done", "quantity", None),
    ]
}


def _pre_stock_picking_picking_properties(env):
    """Avoid triggering the computed method"""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_picking
            ADD COLUMN IF NOT EXISTS picking_properties jsonb
        """,
    )


def _pre_stock_move_line_quantity_product_uom(env):
    """Avoid triggering the computed method"""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move_line
            ADD COLUMN IF NOT EXISTS quantity_product_uom numeric;
        """,
    )


def _pre_stock_move_line_picked(env):
    """Avoid triggering the computed method"""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move_line
            ADD COLUMN IF NOT EXISTS picked boolean
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line
        SET picked = True
        WHERE state = 'done';
        """,
    )


def fix_move_line_quantity(env):
    """
    v17 combines what used to be reserved_qty and qty_done.
    We assume that we shouldn't touch an original qty_done on
    done moves, but that we can best reflect the v16 state of
    lines being worked on by adding reserved_qty to the new
    quantity column, which was qty_done in v16

    In post-migration, we'll recompute the quantity field of
    moves affected.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line
        SET quantity = quantity + reserved_qty
        WHERE
        state IN ('assigned', 'partially_available')
        AND reserved_qty <> 0
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    _pre_stock_picking_picking_properties(env)
    _pre_stock_move_line_picked(env)
    _pre_stock_move_line_quantity_product_uom(env)
    fix_move_line_quantity(env)
