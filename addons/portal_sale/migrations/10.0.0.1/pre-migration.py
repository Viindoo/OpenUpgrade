# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# The templates of portal_sale are the ones 9.0 sends (portal_sale overrides
# the send actions of sale and account): they take over the xml ids of the
# templates of sale and account. Those are deleted: 9.0 never sends them, and
# kept without xml id they would stay next to the new ones under the same name
# (and fail to render from 15.0: they read fields removed since).
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
        superseded = imd.search([
            ('module', '=', new_module), ('name', '=', new_name),
        ])
        template = env['mail.template'].browse(
            superseded.mapped('res_id')).exists()
        superseded.unlink()
        openupgrade.rename_xmlids(env.cr, [(old, new)])
        try:
            with env.cr.savepoint():
                template.unlink()
        except Exception as error:
            _logger.warning(
                "Template %s kept without xml id: %s", template.ids, error)
