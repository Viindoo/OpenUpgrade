from openupgradelib import openupgrade

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


@openupgrade.migrate()
def migrate(env, version):
    _fill_partner_id_if_null(env)
    _fill_language_ids_if_null(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
    delete_constraint_website_visitor_partner_uniq(env)
    keep_the_first_domain_when_duplicate(env)
