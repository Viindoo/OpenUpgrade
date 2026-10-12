# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def precompute_voucher_currency(cr):
    """12.0 stores account.voucher.currency_id (the currency of the journal,
    else of the company). Created by the ORM, the new column is computed for
    every voucher, and as account.voucher.line.price_subtotal depends on
    voucher_id.currency_id, every line of every voucher is computed again, one
    by one, for the same values, then the total of every voucher (makmur:
    6,660 vouchers of 8.0 with 1,714,123 lines, 50 minutes). The column is
    created and filled here with the value the ORM computes.
    """
    if openupgrade.column_exists(cr, "account_voucher", "currency_id"):
        return
    openupgrade.logged_query(
        cr, "ALTER TABLE account_voucher ADD COLUMN currency_id INTEGER")
    company = (
        "v.company_id" if openupgrade.column_exists(
            cr, "account_voucher", "company_id") else "j.company_id")
    openupgrade.logged_query(
        cr, """
        UPDATE account_voucher v
        SET currency_id = COALESCE(j.currency_id, c.currency_id)
        FROM account_journal j, res_company c
        WHERE j.id = v.journal_id AND c.id = COALESCE(%s, j.company_id)
        """ % company)


@openupgrade.migrate()
def migrate(env, version):
    precompute_voucher_currency(env.cr)
