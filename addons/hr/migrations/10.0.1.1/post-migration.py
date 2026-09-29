# -*- coding: utf-8 -*-
# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def archive_new_administrator_employee(env):
    """10.0 adds an employee for the administrator (hr.employee_root, new
    noupdate data). An upgrade must not add to the employees of a company:
    the employee this update has just created is archived (not deleted, it
    is the target of an xml id). create_date is the time of the transaction
    for the records created by the update of the module.
    """
    env.cr.execute(
        """
        SELECT e.id
        FROM hr_employee e
        JOIN ir_model_data d ON d.model = 'hr.employee' AND d.res_id = e.id
        WHERE d.module = 'hr' AND d.name = 'employee_root'
            AND e.create_date = (now() at time zone 'UTC')
        """)
    employee_ids = [row[0] for row in env.cr.fetchall()]
    if employee_ids:
        env['hr.employee'].browse(employee_ids).write({'active': False})


@openupgrade.migrate()
def migrate(env, version):
    archive_new_administrator_employee(env)
    openupgrade.load_data(
        env.cr, 'hr', 'migrations/10.0.1.1/noupdate_changes.xml',
    )
