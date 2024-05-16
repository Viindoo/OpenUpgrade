# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _map_account_report_filter_account_type(env):
    openupgrade.rename_columns(
        env.cr,
        {
            "account_report": [("filter_account_type", None)],
        },
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_report
        ADD COLUMN filter_account_type character varying;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE account_report
        SET filter_account_type = CASE
            WHEN {openupgrade.get_legacy_name('filter_account_type')} = TRUE THEN 'both'
            ELSE 'disabled'
            END
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_account_report_filter_account_type(env)
