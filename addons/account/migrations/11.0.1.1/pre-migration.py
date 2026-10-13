# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# backup of state column with old / non existing values 'proforma' and
# 'proforma2'
column_copies = {
    'account_invoice': [
        ('state', None, None),
    ],
}

# It comes from the renaming of website_portal_sale > sale_payment
_portal_xmlid_renames = [
    ('sale_payment.portal_my_invoices', 'account.portal_my_invoices'),
]

# It comes from the renaming of portal_sale > sale
_portal_sale_xmlid_renames = [
    ('sale.portal_account_invoice_user_rule',
     'account.account_invoice_rule_portal'),
    ('sale.portal_account_invoice_line_rule',
     'account.account_invoice_line_rule_portal'),
]


def precreate_column(cr, table, column, sql_type, default):
    """Create a new column of a big table with the default value the ORM
    would fill in: the ORM adds the column then writes every existing row
    with one UPDATE, while PostgreSQL (11 and later) keeps the default of
    ADD COLUMN for the existing rows without writing them. default is the
    SQL literal of the value the ORM writes."""
    if not openupgrade.table_exists(cr, table) or \
            openupgrade.column_exists(cr, table, column):
        return False
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ADD COLUMN "%s" %s DEFAULT %s'
        % (table, column, sql_type, default))
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ALTER COLUMN "%s" DROP DEFAULT' % (table, column))
    return True


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    # account_tax_cash_basis was merged with account, so there is no module
    # entry anymore to check if it was installed. Check one of its columns
    # instead.
    if openupgrade.column_exists(env.cr, 'account_tax', 'use_cash_basis'):
        openupgrade.rename_columns(
            env.cr, {'account_tax': [('use_cash_basis', None)]})
    openupgrade.delete_record_translations(env.cr, 'account', [
        'mail_template_data_notification_email_account_invoice',
        'email_template_edi_invoice'
    ])
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_sale_xmlid_renames)
    # tax_base_amount: 0 on every journal item that is not a tax line, set by
    # the post-migration with an update of every item (makmur: 2 million
    # items, 3.5 minutes); given here as default to all of them, the tax lines
    # (none or a few) back to empty for the post-migration to compute them
    if precreate_column(
            env.cr, 'account_move_line', 'tax_base_amount', 'numeric', '0'):
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_move_line SET tax_base_amount = NULL
            WHERE tax_line_id IS NOT NULL""")
    openupgrade.add_fields(
        env, [
            ('price_total', 'account.invoice.line', 'account_invoice_line',
             'monetary', False, 'account'),
            ('tax_base_amount', 'account.move.line', 'account_move_line',
             'monetary', False, 'account'),
        ]
    )
