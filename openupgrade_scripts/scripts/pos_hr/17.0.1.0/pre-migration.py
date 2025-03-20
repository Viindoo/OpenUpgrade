# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_tables_renames = [
    ("hr_employee_pos_config_rel", "pos_hr_basic_employee_hr_employee"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _tables_renames)
