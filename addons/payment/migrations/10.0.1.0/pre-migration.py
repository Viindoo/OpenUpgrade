# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'payment_acquirer': [
        ('auto_confirm', None, None),
    ],
}

xmlids_renames = [
    ('payment_adyen.payment_acquirer_adyen',
     'payment.payment_acquirer_adyen'),
    ('payment_authorize.payment_acquirer_authorize',
     'payment.payment_acquirer_authorize'),
    ('payment_buckaroo.payment_acquirer_buckaroo',
     'payment.payment_acquirer_buckaroo'),
    ('payment_ogone.payment_acquirer_ogone',
     'payment.payment_acquirer_ogone'),
    ('payment_paypal.payment_acquirer_paypal',
     'payment.payment_acquirer_paypal'),
    ('payment_sips.payment_acquirer_sips',
     'payment.payment_acquirer_sips'),
    ('payment_transfer.payment_acquirer_transfer',
     'payment.payment_acquirer_transfer'),
]


def rename_payment_method_to_token(env):
    """9.0 payment.method is 10.0 payment.token (same fields). Rename the model
    and its table: otherwise 10.0 creates an empty payment_token, the saved
    tokens are lost with the link of their transactions, and the 9.0 table
    stays behind, in the way of the new payment.method of 17.0 (same table
    name)."""
    cr = env.cr
    if not openupgrade.table_exists(cr, 'payment_method') or \
            openupgrade.table_exists(cr, 'payment_token'):
        return
    openupgrade.rename_models(cr, [('payment.method', 'payment.token')])
    openupgrade.rename_tables(cr, [('payment_method', 'payment_token')])
    openupgrade.rename_fields(env, [
        ('payment.transaction', 'payment_transaction',
         'payment_method_id', 'payment_token_id'),
    ])


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_xmlids(env.cr, xmlids_renames)
    rename_payment_method_to_token(env)
