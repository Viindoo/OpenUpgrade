# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "hr_holidays.hr_leave_stress_day_rule_multi_company",
    "hr_holidays.mail_act_leave_allocation_second_approval",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_holidays", "17.0.1.6/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
