# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_renamed_xmlids = [
    (
        "base.lang_sr_RS",
        "base.lang_sr@Cyrl",
    ),
    (
        "spreadsheet_dashboard.dashboard_management",
        "base.module_category_productivity_dashboard",
    ),
]


def _fix_list_view_type(cr):
    """
    Former tree views have view type list now.

    It's not strictly necessary to change this, but squelches a lot of warnings
    in the log
    """
    openupgrade.logged_query(cr, "UPDATE ir_ui_view SET type='list' WHERE type='tree'")


def _fix_list_view_mode(cr):
    """
    Previous actions had a default value of tree,form, but now the default is list,form.
    If any records do not define this field explicitly,
    the default value from the previous version is kept, which causes an error.
    """
    openupgrade.logged_query(
        cr,
        r"""UPDATE ir_act_window
            SET view_mode = REGEXP_REPLACE(view_mode, '(^|,)tree(,|$)', '\1list\2', 'g')
        WHERE view_mode ~ '(^|,)tree(,|$)'
        """,
    )


def _fix_serbian_res_lang_record(cr):
    """
    ISO code of Serbian (Cyrillic) has been changed
    """
    openupgrade.logged_query(
        cr, "UPDATE res_lang SET code='sr@Cyrl', iso_code='sr@Cyrl' WHERE code='sr_RS'"
    )


def _fix_company_layout_background(cr):
    """
    res.company#layout_background has lost the geometric option
    """
    openupgrade.logged_query(
        cr,
        "UPDATE res_company SET layout_background='Blank' "
        "WHERE layout_background='Geometric'",
    )


def _create_cron_action_xmlids(cr):
    """Loading a record of a model with _inherits also gives its parent record an
    external id: <xml id of the cron>_ir_actions_server for a scheduled action.
    A cron created before that mechanism, and kept since in noupdate data, has
    none, and a data file referencing it fails ("External ID not found":
    stock_rule_views.xml references stock.ir_cron_scheduler_action_ir_actions_server
    in 18.0). Create the missing ones as Odoo would have."""
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        SELECT d.module, d.name || '_ir_actions_server', 'ir.actions.server',
            c.ir_actions_server_id, d.noupdate
        FROM ir_model_data d
        JOIN ir_cron c ON c.id = d.res_id
        WHERE d.model = 'ir.cron' AND c.ir_actions_server_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM ir_model_data d2
                WHERE d2.module = d.module
                    AND d2.name = d.name || '_ir_actions_server')
        """,
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


def drop_report_views(cr):
    """Drop the SQL views of the models built on one (reports, synthetic lines):
    their module creates them again from its tables when it loads (init()).
    Left in place, they break the openupgradelib helpers that update every table
    holding a column of a kind (reference fields in rename_models, merge_records):
    "cannot update view approval_synthetic_line" (a union view of viin_approval)
    in the mail and hr_recruitment pre-migrations. Only views named after the
    table of a model are dropped, views of other origin are left alone.
    """
    cr.execute("SELECT model FROM ir_model")
    tables = {model.replace(".", "_") for (model,) in cr.fetchall()}
    cr.execute(
        "SELECT table_name FROM information_schema.views WHERE table_schema = 'public'"
    )
    for (view,) in cr.fetchall():
        if view in tables:
            openupgrade.logged_query(cr, f'DROP VIEW IF EXISTS "{view}" CASCADE')


@openupgrade.migrate(use_env=False)
def _move_stale_partner_barcode_column(cr):
    """res.partner.barcode is company dependent since 14.0 and has no column up
    to 17.0; 18.0 gives it a jsonb column and converts an existing column of
    that name in place. A database that went through 14.0 before its migration
    kept the barcodes (see base 14.0) still has the plain column of 13.0 there:
    "invalid input syntax for type json" on a barcode with a leading zero. Move
    it aside, as stock does for product_template.responsible_id; post-migration
    takes the barcodes that never became properties from it."""
    cr.execute(
        """
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = current_schema()
            AND table_name = 'res_partner' AND column_name = 'barcode'
        """
    )
    row = cr.fetchone()
    if row and row[0] != "jsonb":
        openupgrade.rename_columns(cr, {"res_partner": [("barcode", None)]})


def migrate(cr, version):
    openupgrade.logged_query(
        cr,
        f"""
        CREATE TABLE {openupgrade.get_legacy_name("ir_module_module")
            } AS (SELECT name, state FROM ir_module_module);
        """,
    )
    _move_stale_partner_barcode_column(cr)
    release_records_of_lost_modules(cr)
    drop_report_views(cr)
    openupgrade.update_module_names(
        cr, renamed_modules.items(), environment_namespec=True
    )
    openupgrade.update_module_names(
        cr, merged_modules.items(), merge_modules=True, environment_namespec=True
    )
    openupgrade.clean_transient_models(cr)
    openupgrade.rename_xmlids(cr, _renamed_xmlids)
    openupgrade.copy_columns(
        cr,
        {"ir_act_window_view": [("view_mode", None, None)]},
    )
    old_column = openupgrade.get_legacy_name("view_mode")
    openupgrade.map_values(
        cr,
        old_column,
        "view_mode",
        [("tree", "list")],
        table="ir_act_window_view",
    )
    _fix_list_view_type(cr)
    _fix_list_view_mode(cr)
    _fix_serbian_res_lang_record(cr)
    _fix_company_layout_background(cr)
    # Crons created before 11.0 lack the XML ID of their server action,
    # referenced by the stock and mrp procurement menus since 18.0 (the
    # openupgradelib of this environment has no add_inherits_parent_xmlids yet)
    _create_cron_action_xmlids(cr)
