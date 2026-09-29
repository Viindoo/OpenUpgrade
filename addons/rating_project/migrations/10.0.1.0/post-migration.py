# -*- coding: utf-8 -*-
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_rating_status(env):
    """9.0 asked the customer for a rating whenever a task reached a stage
    that has a rating template, and showed the customer satisfaction of the
    projects flagged is_visible_happy_customer. 10.0 does both only for the
    projects whose rating_status is not 'no', the default: the projects that
    used ratings in 9.0 are set to 'stage', the way 9.0 worked.
    """
    cr = env.cr
    conditions = ["""EXISTS (
            SELECT 1
            FROM project_task_type_rel r
            JOIN project_task_type t ON t.id = r.type_id
            WHERE r.project_id = p.id AND t.rating_template_id IS NOT NULL)"""]
    if openupgrade.column_exists(
            cr, 'project_project', 'is_visible_happy_customer'):
        conditions.append("p.is_visible_happy_customer")
    openupgrade.logged_query(
        cr,
        """
        UPDATE project_project p
        SET rating_status = 'stage'
        WHERE p.rating_status = 'no' AND (%s)
        """ % " OR ".join(conditions))


@openupgrade.migrate()
def migrate(env, version):
    fill_rating_status(env)
