# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def assign_check_out(env):
    """Move name value to check_out column in matching 'sign_in' record for
    records where action='sign_out'.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_attendance a
        SET check_out = (
            SELECT name
            FROM %s
            WHERE action = 'sign_out'
            AND name > a.check_in
            AND employee_id = a.employee_id
            ORDER BY name
            LIMIT 1
        )
        """ % openupgrade.get_legacy_name('hr_attendance')
    )
    # Recompute worked hours
    env['hr.attendance'].search([])._compute_worked_hours()


def assign_attendance_groups(env):
    """9.0 gave the rights on attendances to the HR officers and managers
    (base.group_hr_user / base.group_hr_manager, now hr.group_hr_user /
    hr.group_hr_manager). 10.0 gives them to groups of the application:
    the users who had the rights keep them.
    """
    for old_group, new_group in (
            ('hr.group_hr_user',
             'hr_attendance.group_hr_attendance_user'),
            ('hr.group_hr_manager',
             'hr_attendance.group_hr_attendance_manager'),
    ):
        users = env.ref(old_group).with_context(active_test=False).users
        users.write({'groups_id': [(4, env.ref(new_group).id)]})


@openupgrade.migrate()
def migrate(env, version):
    assign_check_out(env)
    assign_attendance_groups(env)
