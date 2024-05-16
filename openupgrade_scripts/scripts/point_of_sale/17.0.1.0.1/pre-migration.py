# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_tables_renames = [
    ("pos_config_printer_rel", "openupgrade_legacy_17_0_pos_config_printer_rel"),
    ("printer_category_rel", "openupgrade_legacy_17_0_printer_category_rel"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _tables_renames)
