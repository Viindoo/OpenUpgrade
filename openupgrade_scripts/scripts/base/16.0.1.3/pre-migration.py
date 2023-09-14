# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts import apriori
from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_logger = logging.getLogger(__name__)


# To change content of some field's value when a model's name has been changed
_RENAMED_CHANGED_MODELS_NAME = [
    # Odoo
    ("calendar_event", "res_model"),
    ("mail_activity", "res_model"),
    ("mail_followers", "res_model"),
    ("mail_compose_message", "model"),
    ("mail_wizard_invite", "res_model"),
    ("mailing_trace", "model"),
    ("payment_link_wizard", "res_model"),
    ("portal_share", "res_model"),
    ("rating_rating", "res_model"),
    ("rating_rating", "parent_res_model"),
    ("sms_composer", "res_model"),
    ("snailmail_letter", "model"),
    ("ir_act_window", "res_model"),
    ("ir_attachment", "res_model"),
    ("ir_model_data", "model"),
    # tvtmaaddons
    ("user_assignment", "res_model"),
    ("rotating_token", "model"),
    # erponline-enterprise
    ("website_seo_analyze_result", "res_model"),
    # saas-infrastructure-common
    ("progress_task", "model"),
]


def login_or_registration_required_at_checkout(cr):
    """The website_sale_require_login module is merged into website_sale. Check if the
    it was installed in v15 to set the website.account_on_checkout field as mandatory
    so that the functionality remains the same, login/registration required for
    checkout."""
    # Check if the module is installed and its status is "installed".
    if openupgrade.is_module_installed(cr, "website_sale_require_login"):
        # Add the field 'account_on_checkout' to the 'website' table if it doesn't exist yet.
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE website
            ADD COLUMN IF NOT EXISTS account_on_checkout VARCHAR
            """,
        )
        # Set the value 'mandatory' in the field for all records in the table 'website'.
        openupgrade.logged_query(
            cr,
            """
            UPDATE website
            SET account_on_checkout = 'mandatory'
            """,
        )


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
    login_or_registration_required_at_checkout(cr)
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    # restricting inherited views to groups isn't allowed any more
    cr.execute(
        "DELETE FROM ir_ui_view_group_rel r "
        "USING ir_ui_view v "
        "WHERE r.view_id=v.id AND v.inherit_id IS NOT NULL AND v.mode != 'primary'"
    )
    # Renamed model in ir_translation
    changed_models = apriori.renamed_models | apriori.merged_models
    for old_model, new_model in changed_models.items():
        openupgrade.logged_query(
            cr,
            f"""
            UPDATE ir_translation
                SET name = REPLACE(name, '{old_model},', '{new_model},')
            WHERE name ilike '{old_model},%'
            """,
        )
    # Rename field's content of a model's name which has been changed
    # Ex: parent_res_model of rating_rating table store model's name
    for table, column in _RENAMED_CHANGED_MODELS_NAME:
        if not openupgrade.table_exists(cr, table) or not openupgrade.column_exists(
            cr, table, column
        ):
            continue
        for old_model, new_model in changed_models.items():
            openupgrade.logged_query(
                cr,
                f"""
                UPDATE {table}
                    SET {column} = '{new_model}'
                WHERE {column} = '{old_model}'
                """,
            )
