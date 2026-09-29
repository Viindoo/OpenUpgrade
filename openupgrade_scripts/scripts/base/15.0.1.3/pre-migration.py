# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import csv
import logging

from openupgradelib import openupgrade

from odoo import modules, tools

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules
except ImportError:
    renamed_modules = {}
    merged_modules = {}
    _logger.warning(
        "You are using openupgrade_framework without having"
        " openupgrade_scripts module available."
        " The upgrade process will not work properly."
    )

rename_xmlids_l10n_ec = [
    ("l10n_ec.state_ec_1", "base.state_ec_01"),
    ("l10n_ec.state_ec_2", "base.state_ec_02"),
    ("l10n_ec.state_ec_3", "base.state_ec_03"),
    ("l10n_ec.state_ec_4", "base.state_ec_04"),
    ("l10n_ec.state_ec_5", "base.state_ec_05"),
    ("l10n_ec.state_ec_6", "base.state_ec_06"),
    ("l10n_ec.state_ec_7", "base.state_ec_07"),
    ("l10n_ec.state_ec_8", "base.state_ec_08"),
    ("l10n_ec.state_ec_9", "base.state_ec_09"),
    ("l10n_ec.state_ec_10", "base.state_ec_10"),
    ("l10n_ec.state_ec_11", "base.state_ec_11"),
    ("l10n_ec.state_ec_12", "base.state_ec_12"),
    ("l10n_ec.state_ec_13", "base.state_ec_13"),
    ("l10n_ec.state_ec_14", "base.state_ec_14"),
    ("l10n_ec.state_ec_15", "base.state_ec_15"),
    ("l10n_ec.state_ec_16", "base.state_ec_16"),
    ("l10n_ec.state_ec_17", "base.state_ec_17"),
    ("l10n_ec.state_ec_18", "base.state_ec_18"),
    ("l10n_ec.state_ec_19", "base.state_ec_19"),
    ("l10n_ec.state_ec_20", "base.state_ec_20"),
    ("l10n_ec.state_ec_21", "base.state_ec_21"),
    ("l10n_ec.state_ec_22", "base.state_ec_22"),
    ("l10n_ec.state_ec_23", "base.state_ec_23"),
    ("l10n_ec.state_ec_24", "base.state_ec_24"),
]

rename_xmlids_mail = [
    ("mail.icp_mail_catchall_alias", "base.icp_mail_catchall_alias"),
    ("mail.icp_mail_bounce_alias", "base.icp_mail_bounce_alias"),
]


def update_uninstallable_modules_state(cr):
    cr.execute("SELECT name FROM ir_module_module WHERE state = 'installed'")
    module_list = [name for (name,) in cr.fetchall()]
    uninstallable_modules = []
    for module in module_list:
        info = modules.module.load_information_from_description_file(module)
        if module != "studio_customization" and (not info or not info["installable"]):
            uninstallable_modules.append(module)
    if uninstallable_modules:
        cr.execute(
            """UPDATE ir_module_module
            SET state='uninstallable'
            WHERE name IN %s AND state='installed'""",
            (tuple(uninstallable_modules),),
        )


def adopt_manual_country_states(cr):
    """Give the xml ids of base/data/res.country.state.csv to the states that
    users created by hand with the same country and code.

    Those rows have no xml id, so loading the csv inserts a second state and
    dies on res_country_state_name_code_uniq, e.g. a German state entered in
    2019 as DE-NW before 15.0 shipped the German states:
      Key (country_id, code)=(58, DE-NW) already exists.
    Only rows without any xml id are adopted, and only when the xml id is free.
    """
    path = modules.get_module_resource("base", "data", "res.country.state.csv")
    with open(path, encoding="utf-8") as csv_file:
        rows = [
            (row["id"], row["country_id:id"].split(".")[-1], row["code"])
            for row in csv.DictReader(csv_file)
        ]
    cr.execute(
        """CREATE TEMPORARY TABLE openupgrade_csv_state
        (name varchar, country varchar, code varchar) ON COMMIT DROP"""
    )
    cr.executemany("INSERT INTO openupgrade_csv_state VALUES (%s, %s, %s)", rows)
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        SELECT DISTINCT ON (csv.name) 'base', csv.name, 'res.country.state', s.id,
            false
        FROM openupgrade_csv_state csv
        JOIN ir_model_data c ON c.module = 'base' AND c.name = csv.country
            AND c.model = 'res.country'
        JOIN res_country_state s ON s.country_id = c.res_id AND s.code = csv.code
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model_data d
            WHERE d.model = 'res.country.state' AND d.res_id = s.id)
        AND NOT EXISTS (
            SELECT 1 FROM ir_model_data d
            WHERE d.module = 'base' AND d.name = csv.name)
        ORDER BY csv.name, s.id
        """,
    )
    cr.execute("DROP TABLE openupgrade_csv_state")


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
        logging.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )

    # Perform module renames and merges
    release_records_of_lost_modules(cr)
    openupgrade.update_module_names(
        cr, renamed_modules.items(), environment_namespec=True
    )
    openupgrade.update_module_names(
        cr, merged_modules.items(), merge_modules=True, environment_namespec=True
    )

    openupgrade.rename_xmlids(cr, rename_xmlids_l10n_ec)
    openupgrade.rename_xmlids(cr, rename_xmlids_mail)
    adopt_manual_country_states(cr)

    openupgrade.clean_transient_models(cr)
    openupgrade.convert_field_to_html(
        cr, "res_company", "report_footer", "report_footer"
    )
    openupgrade.convert_field_to_html(
        cr, "res_company", "report_header", "report_header"
    )
    openupgrade.convert_field_to_html(
        cr, "res_partner", "comment", "comment", verbose=False
    )
