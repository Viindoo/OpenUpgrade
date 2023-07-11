from itertools import chain

from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5

_xmlids_renames = [
    (
        "website.group_website_publisher",
        "website.group_website_restricted_editor",
    ),
    (
        "website_sale.menu_reporting",
        "website.menu_reporting",
    ),
]

# delete xml xpath for odoo add it again
_xmlids_delete = [
    "website.website_configurator",
    "website.website_menu",
]


def delete_constraint_website_visitor_partner_uniq(env):
    openupgrade.delete_sql_constraint_safely(
        env,
        "website",
        "website_visitor",
        "partner_uniq",
    )


def _fill_partner_id_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_visitor
        SET partner_id = CASE
            WHEN length(access_token) != 32 THEN CAST(access_token AS integer)
            ELSE partner_id
                        END
        WHERE partner_id IS NULL;
        """,
    )


def _fill_language_ids_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO website_lang_rel (website_id, lang_id)
        SELECT w.id, rl.id
        FROM website w
        CROSS JOIN res_lang rl
        WHERE w.id NOT IN (SELECT website_id FROM website_lang_rel)
        AND rl.active = true;
        """,
    )


def keep_the_first_domain_when_duplicate(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website
        SET domain = NULL
        WHERE id NOT IN (
        SELECT MIN(id)
        FROM website
        GROUP BY domain
        );
        """,
    )


def boostrap_5_migration(env):
    """Convert customized website views to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT iuv.id FROM ir_ui_view iuv JOIN website w on w.id = iuv.website_id
        WHERE iuv.type = 'qweb' AND iuv.website_id IS NOT NULL
    """
    )
    view_ids = list(chain.from_iterable(env.cr.fetchall()))
    all_view_need_bs5_migration = env["ir.ui.view"].browse(view_ids)
    for view in all_view_need_bs5_migration:
        new_arch = convert_string_bootstrap_4to5(view.arch_db)
        view.arch_db = new_arch


@openupgrade.migrate()
def migrate(env, version):
    _fill_partner_id_if_null(env)
    _fill_language_ids_if_null(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
    delete_constraint_website_visitor_partner_uniq(env)
    keep_the_first_domain_when_duplicate(env)
    boostrap_5_migration(env)
