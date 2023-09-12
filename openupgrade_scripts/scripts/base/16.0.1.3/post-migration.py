# Copyright 2023 Hunki Enterprises BV (https://hunki-enterprises.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

from odoo import modules

_logger = logging.getLogger(__name__)


def delete_module_not_exist(env):
    env.cr.execute("SELECT id, name FROM ir_module_module WHERE state = 'installed'")
    modules_to_delete = []
    for module in env.cr.dictfetchall():
        mod_path = modules.module.get_module_path(module["name"], downloaded=True)
        manifest_file = modules.module.module_manifest(mod_path)
        if module["name"] != "studio_customization":
            if not manifest_file:
                modules_to_delete.append(module["id"])
            else:
                info = modules.module.get_manifest(module["name"])
                if not info or not info["installable"]:
                    _logger.warning("Module %s has not been upgraded" % module["name"])
    if modules_to_delete:
        modules_to_delete = env["ir.module.module"].browse(modules_to_delete)
        modules_to_delete.module_uninstall()
        modules_to_delete.unlink()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "16.0.1.3/noupdate_changes.xml")
    env.cr.execute(
        "UPDATE res_partner p SET company_registry=c.company_registry "
        "FROM res_company c WHERE c.partner_id=p.id"
    )
    delete_module_not_exist(env)
