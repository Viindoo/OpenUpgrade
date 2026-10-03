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


def enable_coupon_sharing_within_entity(cr):
    """Check before merging `coupon_commercial_partner_applicability` into
    `loyalty_partner_applicability` if it was installed in v15 to set the parameter
    to True to keep the same functionality"""
    if openupgrade.is_module_installed(cr, "coupon_commercial_partner_applicability"):
        # The value of the configuration parameter is set to True.
        openupgrade.logged_query(
            cr,
            """
            INSERT INTO ir_config_parameter (key, value)
            VALUES ('loyalty_partner_applicability.allow_coupon_sharing', 'true')
            """,
        )


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


def update_translatable_fields(cr):
    # Edgy case for DBs with long history as well, where we could have a situation where:
    # - The source term is a languange different from 'en_US'
    # - That language term is blank
    # The result is that the resultant json won't take the term for that language and
    # it will appear with the value given to 'en_US' (as it's the default one)
    openupgrade.logged_query(
        cr,
        """
            UPDATE ir_translation
            SET state = 'translated', value = src
            WHERE type = 'model'
                AND src != ''
                AND value = ''
                AND value IS DISTINCT FROM src
        """,
    )
    # Fix terms with wrong to_translate state. DBs with long version history could have
    # terms that didn't have the right state and those would be ignored
    openupgrade.logged_query(
        cr,
        """
            UPDATE ir_translation set state = 'translated'
            WHERE type = 'model'
                AND state = 'to_translate'
                AND value is NOT NULL
                AND value IS DISTINCT FROM src
        """,
    )
    # exclude fields from translation update
    exclusions = {
        # ir.actions.* inherits the name and help columns from ir.actions.actions
        "ir.actions.act_window": ["name", "help"],
        "ir.actions.act_url": ["name", "help"],
        "ir.actions.server": ["name", "help"],
        "ir.actions.client": ["name", "help"],
        "ir.actions.report": ["name", "help"],
    }
    cr.execute(
        "SELECT f.name, m.model FROM ir_model_fields f "
        "JOIN ir_model m ON f.model_id=m.id WHERE f.translate"
    )
    for field, model in cr.fetchall():
        if field in exclusions.get(model, []):
            continue
        table = openupgrade.get_model2table(model)
        if not openupgrade.table_exists(cr, table):
            _logger.warning(
                "Couldn't find table for model %s - not updating translations", model
            )
            continue
        columns = tools.sql.table_columns(cr, table)
        if field in columns:
            if columns[field]["udt_name"] in ["varchar", "text"]:
                tools.sql.convert_column_translatable(cr, table, field, "jsonb")
        else:
            _logger.warning(
                "Couldn't find column for field %s - not updating translations", field
            )
            continue
        # borrowed from odoo/tools/translate.py#_get_translation_upgrade_queries
        translation_name = f"{model},{field}"
        emtpy_src = """'{"en_US": ""}'::jsonb"""
        openupgrade.logged_query(
            cr,
            f"""
            WITH t AS (
                SELECT it.res_id as res_id, jsonb_object_agg(it.lang, it.value) AS value,
                    bool_or(imd.noupdate) AS noupdate
                FROM ir_translation it
                LEFT JOIN ir_model_data imd ON imd.model = %(model)s AND imd.res_id = it.res_id
                WHERE it.type = 'model'
                    AND it.name = %(name)s
                    AND it.state = 'translated'
                    AND COALESCE(it.value, '') != ''
                GROUP BY it.res_id
            )
            UPDATE {table} m
            SET "{field}" = CASE
                WHEN m."{field}" IS NULL THEN {emtpy_src} || t.value
                WHEN t.noupdate IS FALSE THEN t.value || m."{field}"
                ELSE m."{field}" || t.value END
            FROM t
            WHERE t.res_id = m.id
            """,
            {
                "model": model,
                "name": translation_name,
            },
        )


_TECHNICAL_MODELS = (
    "ir.actions.act_url",
    "ir.actions.act_window",
    "ir.actions.client",
    "ir.actions.report",
    "ir.actions.server",
    "ir.actions.todo",
    "ir.cron",
    "ir.filters",
    "ir.model.access",
    "ir.property",
    "ir.rule",
    "ir.ui.menu",
    "ir.ui.view",
    "mail.template",
    "website.menu",
)


def release_records_of_lost_modules(cr):
    """A module that is removed without a successor is merged into the module
    it extended (apriori.lost_modules), and the update of that module deletes
    the records it no longer finds in the data files, except the noupdate
    ones: release the technical records, so that they are deleted too, and
    detach the xml ids of the records of models that go with the module (the
    rows stay). Business records stay.
    """
    from odoo.addons.openupgrade_scripts import apriori as _apriori

    lost_modules = tuple(getattr(_apriori, "lost_modules", []))
    if not lost_modules:
        return
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET noupdate = FALSE
        WHERE noupdate AND module IN %s AND model IN %s
        """,
        (lost_modules, _TECHNICAL_MODELS),
    )
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data d
        WHERE d.module IN %s AND d.model IN (
            SELECT m.model
            FROM ir_model m
            JOIN ir_model_data md ON md.model = 'ir.model'
                AND md.res_id = m.id AND md.module IN %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ir_model_data o
                WHERE o.model = 'ir.model' AND o.res_id = m.id
                    AND o.module NOT IN %s))
        """,
        (lost_modules,) * 3,
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
    enable_coupon_sharing_within_entity(cr)
    release_records_of_lost_modules(cr)
    openupgrade.update_module_names(
        cr, renamed_modules.items(), environment_namespec=True
    )
    openupgrade.update_module_names(
        cr, merged_modules.items(), merge_modules=True, environment_namespec=True
    )
    openupgrade.clean_transient_models(cr)
    # restricting inherited views to groups isn't allowed anymore
    cr.execute(
        "DELETE FROM ir_ui_view_group_rel r "
        "USING ir_ui_view v "
        "WHERE r.view_id=v.id AND v.inherit_id IS NOT NULL AND v.mode != 'primary'"
    )
    # pre-create res.partner~company_registry
    openupgrade.logged_query(
        cr, "ALTER TABLE res_partner ADD IF NOT EXISTS company_registry VARCHAR"
    )
    # Renamed model in ir_translation
    changed_models = dict(**apriori.renamed_models, **apriori.merged_models)
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
    # TODO: move to OCA/openupgradelib repo
    # Update key in ir_ui_view
    for old_model, new_model in changed_models.items():
        openupgrade.logged_query(
            cr,
            f"""
            UPDATE ir_ui_view
                SET key = REPLACE(key, '{old_model}.', '{new_model}.')
            WHERE key ilike '{old_model}.%'
            """,
        )
