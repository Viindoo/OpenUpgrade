# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # 9.0 website_project_issue overwrote the record rule
    # project_issue.issue_user_rule; 10.0 no longer does. The rule itself
    # belongs to project_issue, which still ships it in 10.0 and has just
    # updated it (noupdate_changes.xml of project_issue): it must stay, or
    # employees read the issues of every project, the ones restricted to
    # followers included.
    pass
