# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _map_hr_leave_accrual_level_added_value_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_accrual_level
        SET added_value_type = CASE
            WHEN added_value_type = 'days' THEN 'day'
            ELSE 'hour'
            END
        WHERE added_value_type IN ('days', 'hours')
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_hr_leave_accrual_level_added_value_type(env)
