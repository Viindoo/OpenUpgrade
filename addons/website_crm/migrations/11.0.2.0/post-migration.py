# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID


def fill_website_crm_defaults(env):
    """Keep the team and salesperson of the leads of the contact form.

    Up to 10.0 the contact form creates its leads as the superuser: they get
    the superuser as salesperson and the superuser's sales team. 11.0 takes
    them from two new fields of the website, whose defaults are the first
    team by name and no salesperson: the leads of the website went to another
    team, with nobody assigned. Fill the fields as the leads were assigned.
    """
    team = env['crm.team'].with_context(default_type='lead')._get_default_team_id(
        user_id=SUPERUSER_ID)
    for website in env['website'].search([]):
        website.write({
            'crm_default_team_id': team.id or website.crm_default_team_id.id,
            'crm_default_user_id': SUPERUSER_ID,
        })


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_crm', 'migrations/11.0.2.0/noupdate_changes.xml',
    )
    fill_website_crm_defaults(env)
