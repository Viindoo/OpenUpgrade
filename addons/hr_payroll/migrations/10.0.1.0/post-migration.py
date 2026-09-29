# -*- coding: utf-8 -*-
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def assign_payroll_groups(env):
    """9.0 gave the rights on payroll to the HR officers and managers
    (base.group_hr_user / base.group_hr_manager, now hr.group_hr_user /
    hr.group_hr_manager). 10.0 gives them to groups of the application:
    the users who had the rights keep them.
    """
    for old_group, new_group in (
            ('hr.group_hr_user',
             'hr_payroll.group_hr_payroll_user'),
            ('hr.group_hr_manager',
             'hr_payroll.group_hr_payroll_manager'),
    ):
        users = env.ref(old_group).with_context(active_test=False).users
        users.write({'groups_id': [(4, env.ref(new_group).id)]})


def delete_obsolete_payslip_rule(env):
    """The record rule that limits HR officers to their own payslips and the
    ones of their department is noupdate data of 9.0 that 10.0 no longer
    ships: the end of the update does not delete it. Left in place it would
    apply to every payroll officer and manager (their groups imply
    hr.group_hr_user), while a 10.0 database has no record rule on payslips.
    """
    openupgrade.delete_records_safely_by_xml_id(
        env, ['hr_payroll.property_rule_employee_payslip'])


@openupgrade.migrate()
def migrate(env, version):
    assign_payroll_groups(env)
    delete_obsolete_payslip_rule(env)
