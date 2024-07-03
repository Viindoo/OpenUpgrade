from openupgradelib import openupgrade


def _sml_update_batch_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_move_line
        ADD COLUMN IF NOT EXISTS batch_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET batch_id = sp.batch_id
        FROM stock_picking sp
        WHERE sml.picking_id = sp.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _sml_update_batch_id(env)
