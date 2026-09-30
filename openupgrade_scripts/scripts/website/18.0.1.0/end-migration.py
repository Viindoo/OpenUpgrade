# Copyright 2026 Tecnativa - Cristina Hidalgo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def archive_frozen_website_views(env):
    """Archive the website-specific views that froze templates of an old version.

    The 12.0 migration gave every template changed with the website editor of
    11.0 or older a website-specific copy (bootstrap_4_migration, the copies are
    marked in openupgrade_legacy_12_0_bs4_migrated_from). Those copies keep the
    template as it was then: in 18.0 the views of the modules no longer find what
    they extend in them, and one such copy in the layout (search box, footer)
    breaks every page of the website, /web/login included. The pages (views of a
    website.page) are content and stay; the other copies and the website-specific
    views built on them are archived: the website renders the templates of 18.0
    again. The archived views are kept (and logged), for their content to be
    carried over by hand where it matters.
    """
    cr = env.cr
    View = env["ir.ui.view"].with_context(active_test=False)
    archived = View.browse()
    if openupgrade.column_exists(
        cr, "ir_ui_view", "openupgrade_legacy_12_0_bs4_migrated_from"
    ):
        cr.execute(
            """SELECT v.id FROM ir_ui_view v
            WHERE v.openupgrade_legacy_12_0_bs4_migrated_from IS NOT NULL
                AND v.website_id IS NOT NULL AND v.active AND v.type = 'qweb'
                AND NOT EXISTS (
                    SELECT 1 FROM website_page p WHERE p.view_id = v.id)"""
        )
        archived = View.browse([row[0] for row in cr.fetchall()])
    built_on = archived
    while built_on:
        built_on = (
            View.search(
                [
                    ("inherit_id", "in", built_on.ids),
                    ("website_id", "!=", False),
                    ("active", "=", True),
                ]
            )
            - archived
        )
        archived |= built_on
    archived.write({"active": False})
    # a generic page is served only while its view has no website-specific
    # copy, archived ones included (ir.http._serve_page): give the archived
    # copies of page views a key of their own, or their pages answer 404
    page_keys = set(
        env["website.page"]
        .with_context(active_test=False)
        .search([("website_id", "=", False)])
        .view_id.mapped("key")
    )
    for view in archived.filtered(lambda v: v.key in page_keys):
        view.key = "%s_frozen_%s" % (view.key, view.id)
    if archived:
        _logger.warning(
            "%s website-specific views archived: they froze templates of an old "
            "version (their content is kept in the archived views): %s",
            len(archived),
            ", ".join(
                "%s (id %s, website %s)" % (v.key, v.id, v.website_id.id)
                for v in archived.sorted("key")
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.cow_templates_replicate_upstream(env.cr)
    archive_frozen_website_views(env)
