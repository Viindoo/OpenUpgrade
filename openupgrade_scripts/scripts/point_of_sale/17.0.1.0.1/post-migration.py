# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "point_of_sale.rule_pos_account_move",
    "point_of_sale.rule_pos_account_move_line",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "point_of_sale", "17.0.1.0.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
