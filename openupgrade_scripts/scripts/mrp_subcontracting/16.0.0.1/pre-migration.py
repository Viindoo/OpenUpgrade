from openupgradelib import openupgrade


def _stock_location_fill_is_subcontracting_location(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE stock_location
        ADD COLUMN IF NOT EXISTS is_subcontracting_location boolean;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_location t1
        SET is_subcontracting_location = true
        FROM res_company t2
        WHERE t2.subcontracting_location_id = t1.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _stock_location_fill_is_subcontracting_location(env)
