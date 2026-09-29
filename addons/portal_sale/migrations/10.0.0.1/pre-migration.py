# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

# The templates of portal_sale are the ones 9.0 sends (portal_sale overrides
# the send actions of sale and account): they take over the xml ids of the
# templates of sale and account, which stay in the database without xml id.
xmlids_renames = [
    ('portal_sale.email_template_edi_sale',
     'sale.email_template_edi_sale'),
    ('portal_sale.email_template_edi_invoice',
     'account.email_template_edi_invoice'),
]


@openupgrade.migrate()
def migrate(env, version):
    imd = env['ir.model.data']
    for old, new in xmlids_renames:
        old_module, old_name = old.split('.')
        if not imd.search([
                ('module', '=', old_module), ('name', '=', old_name)]):
            # nothing to take over the xml id: keep the template of
            # sale / account under its xml id
            continue
        new_module, new_name = new.split('.')
        imd.search([
            ('module', '=', new_module), ('name', '=', new_name),
        ]).unlink()
        openupgrade.rename_xmlids(env.cr, [(old, new)])
