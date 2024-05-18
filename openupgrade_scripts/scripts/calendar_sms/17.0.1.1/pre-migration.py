# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_calendar_alarm_sms_notify_responsible(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE calendar_alarm
        ADD COLUMN sms_notify_responsible bool;
        """,
    )
    env.cr.execute(
        """UPDATE calendar_alarm
            SET sms_notify_responsible = TRUE
            WHERE alarm_type = 'sms'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_calendar_alarm_sms_notify_responsible(env)
