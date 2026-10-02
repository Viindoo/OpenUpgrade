# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from openupgradelib import openupgrade

from odoo import tools


def fill_favicon(env):
    """10.0 gives the default website a favicon in website_data.xml, but that
    record is noupdate in a 9.0 database: it keeps none, and from then on the
    pages show the placeholder of a missing picture as their favicon. Give the
    websites without one the favicon 9.0 showed them."""
    websites = env['website'].search([('favicon', '=', False)])
    if websites:
        with tools.file_open('web/static/src/img/favicon.ico', 'rb') as f:
            websites.write({'favicon': base64.b64encode(f.read())})


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
    fill_favicon(env)
