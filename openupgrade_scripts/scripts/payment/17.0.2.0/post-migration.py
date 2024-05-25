# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _fill_payment_method(env):
    payment_tokens = env["payment.token"].with_context(active_test=False).search([])
    for payment_token in payment_tokens:
        payment_token.payment_method_id = payment_token.provider_id.payment_method_ids[
            :1
        ].id

    payment_transactions = (
        env["payment.transaction"].with_context(active_test=False).search([])
    )
    for transaction in payment_transactions:
        transaction.payment_method_id = transaction.provider_id.payment_method_ids[
            :1
        ].id


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "payment", "17.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["payment.payment_transaction_user_rule"]
    )
    _fill_payment_method(env)
