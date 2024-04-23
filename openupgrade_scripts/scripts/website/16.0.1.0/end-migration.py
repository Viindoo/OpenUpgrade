from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import (
    _convert_field_bootstrap_4to5_sql,
    convert_field_bootstrap_4to5,
)


def convert_custom_qweb_templates_bootstrap_4to5(env):
    """Convert customized website views to Bootstrap 5."""
    backup_column = openupgrade.get_legacy_name("arch_db_bs4")
    openupgrade.logged_query(
        env.cr, f"ALTER TABLE ir_ui_view ADD COLUMN {backup_column} TEXT"
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE ir_ui_view SET {backup_column} = arch_db
        WHERE type = 'qweb' AND website_id IS NOT NULL
        """,
    )
    # Find views to convert
    env.cr.execute(
        "SELECT id FROM ir_ui_view WHERE type = 'qweb' AND website_id IS NOT NULL"
    )
    view_ids = [x for x, *_ in env.cr.fetchall()]
    _convert_field_bootstrap_4to5_sql(env.cr, "ir_ui_view", "arch_db", ids=view_ids)


def convert_field_html_string_bootstrap_4to5(env):
    """Convert html field which might contain old bootstrap syntax"""
    # These models won't use bootstrap in their html fields
    exclusions = [
        "mail.message",
        "mail.mail",
        "mail.template",
        "res.users",
        "mail.channel",
        "mailing.mailing",
        "account.invoice.send",
        "mail.alias",
    ]
    fields = env["ir.model.fields"].search(
        [("ttype", "=", "html"), ("store", "=", True)]
    )
    for field in fields:
        model = field.model_id.model
        if model in exclusions:
            continue
        if env.get(model, False) is not False and env[model]._auto:
            if openupgrade.table_exists(env.cr, env[model]._table):
                if field.name in env[model]._fields and openupgrade.column_exists(
                    env.cr, env[model]._table, field.name
                ):
                    convert_field_bootstrap_4to5(
                        env, model, field.name, domain=[(field.name, "!=", False)]
                    )


def rename_t_group_website_restricted_editor(env):
    """Locate group directives in custom views with the former `group_website_publisher`
    group which is now renamed to `group_website_restricted_editor`. For example, the
    website_partner.partner_detail template"""
    views = env["ir.ui.view"].search(
        [
            (
                "arch_db",
                "ilike",
                "website.group_website_publisher",
            ),
            ("website_id", "!=", False),
        ]
    )
    for view in views:
        view.arch_db = view.arch_db.replace(
            "website.group_website_publisher", "website.group_website_restricted_editor"
        )


def _sync_website_visitor_access_token(env):
    """
    Following pr https://github.com/odoo/odoo/pull/110870
    this is needed
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_visitor
            SET access_token = partner_id::text
        WHERE partner_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM website_visitor t1 WHERE t1.access_token = t1.partner_id::text
        );
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_custom_qweb_templates_bootstrap_4to5(env)
    convert_field_html_string_bootstrap_4to5(env)
    rename_t_group_website_restricted_editor(env)
    _sync_website_visitor_access_token(env)
