# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _fill_res_users_microsoft_calendar_account_id(env):
    env.cr.execute(
        """
        SELECT id, microsoft_calendar_sync_token, microsoft_synchronization_stopped
        FROM res_users
        WHERE microsoft_calendar_sync_token IS NOT NULL
        """
    )
    vals_list = []
    for row in env.cr.fetchall():
        vals_list.append(
            {
                'calendar_sync_token': row[1],
                'synchronization_stopped': row[2],
                'user_ids': [(6, 0, [row[0]])],
            }
        )
    if vals_list:
        env['microsoft.calendar.credentials'].create(vals_list)


@openupgrade.migrate()
def migrate(env, version):
    _fill_res_users_microsoft_calendar_account_id(env)
