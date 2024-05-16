# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "account.account_payment_term_2months",
    "account.tax_group_taxes",
    "account.account_invoice_send_rule_group_invoice",
    "account.sequence_reconcile_seq",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "account", "17.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
