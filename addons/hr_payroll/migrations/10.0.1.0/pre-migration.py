# -*- coding: utf-8 -*-
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # 10.0 drives the payslip with buttons instead of the workflow
    openupgrade.delete_model_workflow(env.cr, 'hr.payslip')
