# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)

_xmlids_renames = [
    (
        "mail.access_res_users_settings_all",
        "base.access_res_users_settings_all",
    ),
    (
        "mail.access_res_users_settings_user",
        "base.access_res_users_settings_user",
    ),
    (
        "mail.res_users_settings_rule_admin",
        "base.res_users_settings_rule_admin",
    ),
    (
        "mail.res_users_settings_rule_user",
        "base.res_users_settings_rule_user",
    ),
    (
        "mail.constraint_res_users_settings_unique_user_id",
        "base.constraint_res_users_settings_unique_user_id",
    ),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    """
    Don't request an env for the base pre-migration as flushing the env in
    odoo/modules/registry.py will break on the 'base' module not yet having
    been instantiated.
    """
    if "openupgrade_framework" not in tools.config["server_wide_modules"]:
        _logger.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    openupgrade.clean_transient_models(cr)
    openupgrade.rename_xmlids(cr, _xmlids_renames)
