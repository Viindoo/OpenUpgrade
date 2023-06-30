from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "website.group_website_publisher",
        "website.group_website_restricted_editor",
    )
]

# delete xml xpath for odoo add it again
_xmlids_delete = [
    "website.s_image_gallery_options",
    "website.s_product_catalog_options",
    "website.s_table_of_content_options",
    "website.s_media_list_options",
    "website.s_timeline_options",
    "website.website_configurator",
]


def _set_xml_ids_noupdate_value(env):
    openupgrade.set_xml_ids_noupdate_value(
        env, "website", ["action_website", "s_masonry_block_default_image_2"], False
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


@openupgrade.migrate()
def migrate(env, version):
    _set_xml_ids_noupdate_value(env)
    _fill_partner_id_if_null(env)
    _fill_language_ids_if_null(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
