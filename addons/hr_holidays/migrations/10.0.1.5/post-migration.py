# -*- coding: utf-8 -*-
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def assign_holidays_groups(env):
    """9.0 gave the rights on leaves to the HR officers and managers
    (base.group_hr_user / base.group_hr_manager, now hr.group_hr_user /
    hr.group_hr_manager). 10.0 gives them to groups of the application:
    the users who had the rights keep them.
    """
    for old_group, new_group in (
            ('hr.group_hr_user',
             'hr_holidays.group_hr_holidays_user'),
            ('hr.group_hr_manager',
             'hr_holidays.group_hr_holidays_manager'),
    ):
        users = env.ref(old_group).with_context(active_test=False).users
        users.write({'groups_id': [(4, env.ref(new_group).id)]})


@openupgrade.migrate()
def migrate(env, version):
    assign_holidays_groups(env)
