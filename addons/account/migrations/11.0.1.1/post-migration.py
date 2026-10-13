# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Opener B.V. <https://opener.amsterdam>
# Copyright 2018-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from psycopg2.extras import execute_values
from openupgradelib import openupgrade

import logging

_logger = logging.getLogger(__name__)


@openupgrade.logging()
def _migrate_security(env):
    """Update security-related changes."""
    group_account_invoice = env.ref("account.group_account_invoice")
    group_account_manager = env.ref("account.group_account_manager")
    group_account_user = env.ref("account.group_account_user")
    group_account_user.implied_ids -= group_account_invoice
    group_account_manager.implied_ids = (
        group_account_manager.implied_ids -
        group_account_user + group_account_invoice
    )


def migrate_account_tax_cash_basis(env):
    # Migrate tax exigibility settings
    if not openupgrade.column_exists(
            env.cr, 'account_tax',
            openupgrade.get_legacy_name('use_cash_basis')):
        return  # pragma: no cover
    field = AsIs(openupgrade.get_legacy_name('use_cash_basis'))
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_tax
        SET tax_exigibility = 'on_payment'
        WHERE %s IS TRUE;""", (field,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_tax
        SET tax_exigibility = 'on_invoice'
        WHERE %s IS NOT TRUE;""", (field,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE res_company rc
        SET tax_exigibility = TRUE WHERE EXISTS (
            SELECT id FROM account_tax
            WHERE company_id = rc.id AND tax_exigibility = 'on_payment')""")


def migrate_account_report_invoice_with_payments(env):
    env.ref("account.account_invoices").attachment_use = False


@openupgrade.logging()
def fill_account_invoice_line_total(env):
    """Try to compute the field `price_total` in a more optimized way for
    speeding up the migration.
    """
    # We first set price_subtotal for lines without taxes
    line_obj = env['account.invoice.line']
    empty_lines = line_obj.search([('invoice_line_tax_ids', '=', 'False')])
    if empty_lines:
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_invoice_line
            SET price_total = price_subtotal
            WHERE id IN %s""", (tuple(empty_lines.ids), )
        )
    # Now we compute easily the lines with only 1 tax, no included in price,
    # and that tax is simply a percentage (which are most of the cases)
    env.cr.execute(
        """SELECT id FROM (
            SELECT ail.id,
                COUNT(at.id) AS rnum,
                MIN(CASE WHEN at.amount_type = 'percent' THEN 0 ELSE 1 END)
                    AS amount_type,
                MIN(CASE WHEN at.price_include THEN 0 ELSE 1 END)
                    AS price_include
            FROM account_invoice_line ail,
                account_invoice_line_tax rel,
                account_tax at
            WHERE
                ail.id = rel.invoice_line_id
                AND at.id = rel.tax_id
            GROUP BY ail.id
        ) sub
        WHERE sub.rnum = 1
            AND sub.amount_type = 0
            AND sub.price_include = 1"""
    )
    simple_lines = line_obj.browse([x[0] for x in env.cr.fetchall()])
    if simple_lines:
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_invoice_line ail
            SET price_total = ail.price_subtotal + round(
                ail.price_unit * ail.quantity *
                (1 - COALESCE(ail.discount, 0.0) / 100.0) *
                at.amount / 100.0, CEIL(LOG(1.0 / cur.rounding))::INTEGER)
            FROM account_tax at,
                account_invoice_line_tax rel,
                account_invoice ai,
                res_currency cur
            WHERE ail.id = rel.invoice_line_id
                AND at.id = rel.tax_id
                AND ai.id = ail.invoice_id
                AND cur.id = ai.currency_id
                AND ail.id IN %s""", (tuple(simple_lines.ids), ),
        )
    # Compute the rest (which should be minority) with regular method
    rest_lines = line_obj.search([]) - empty_lines - simple_lines
    openupgrade.logger.debug("Compute the rest of the account.invoice.line"
                             "totals: %s" % len(rest_lines))
    # The values are written by batches instead of one write per line: the
    # domain of empty_lines (the string 'False') selects no line, so every line
    # without tax comes here (makmur: 584,278 lines, 7 minutes, mostly the
    # writes). Same values, converted as the ORM writes them (monetary: rounded
    # to the currency, as text), same write_uid and write_date, and what
    # depends on price_total is recomputed as after a write.
    field = line_obj._fields['price_total']
    for lines in openupgrade.chunked(rest_lines, single=False):
        rows = []
        for line in lines:
            # avoid error on taxes with other type of computation ('code' for
            # example, provided by module `account_tax_python`). We will need
            # to add the computation on the corresponding module
            # post-migration.
            types = ['percent', 'fixed', 'group', 'division']
            if any(x.amount_type not in types
                   for x in line.invoice_line_tax_ids):
                continue
            # This has been extracted from `_compute_price` method
            currency = line.invoice_id and line.invoice_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(
                price, currency, line.quantity, product=line.product_id,
                partner=line.invoice_id.partner_id,
            )
            value = field.convert_to_column(taxes['total_included'], line)
            if not isinstance(value, str):
                value = repr(float(value))
            rows.append((line.id, value))
        if not rows:
            continue
        execute_values(env.cr._obj, """
            UPDATE account_invoice_line l
            SET price_total = v.price_total::numeric, write_uid = %d,
                write_date = (now() at time zone 'UTC')
            FROM (VALUES %%s) AS v (id, price_total)
            WHERE l.id = v.id""" % env.uid, rows, page_size=len(rows))
        done = line_obj.browse([row[0] for row in rows])
        done.invalidate_cache(['price_total'], done.ids)
        done.modified(['price_total'])
        done.recompute()
    openupgrade.logger.debug("Compute finished")


@openupgrade.logging()
def fill_account_move_line_tax_base_amount(env):
    """Compute the field `tax_base_amount` in a more optimized way for speeding
    up the migration.
    """
    # First, put 0 on all of them without originator tax (given by the
    # pre-migration: only a line that differs is written)
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line
        SET tax_base_amount = 0
        WHERE tax_line_id IS NULL
            AND tax_base_amount IS DISTINCT FROM 0""",
    )
    # Then, get from SQL the sum of bases for the rest
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET tax_base_amount = sub.base
        FROM (
            SELECT aml.move_id, rel.account_tax_id, SUM(aml.balance) AS base
            FROM account_move_line aml,
                account_move_line_account_tax_rel rel
            WHERE aml.id = rel.account_move_line_id
            GROUP BY aml.move_id, rel.account_tax_id
        ) AS sub
        WHERE sub.move_id = aml.move_id
            AND sub.account_tax_id = aml.tax_line_id
        """,
    )

def cancel_no_entry_posted_payments(env):
    # In SQL: the ORM turns ('move_line_ids', '=', False) into id NOT IN (the
    # list of every payment with journal items), compared item by item with
    # each payment (makmur: 351,505 payments, 2 minutes)
    env.cr.execute("""
        SELECT ap.id FROM account_payment ap
        WHERE ap.state IN ('posted', 'reconciled')
            AND NOT EXISTS (SELECT 1 FROM account_move_line aml
                            WHERE aml.payment_id = ap.id)
        ORDER BY ap.payment_date DESC, ap.name DESC""")
    payments = env['account.payment'].browse([r[0] for r in env.cr.fetchall()])
    _logger.info("Cancelling all no-entry-posted-payments with ids: %s" % payments.ids)
    payments.cancel()


@openupgrade.migrate()
def migrate(env, version):
    # map old / non existing value 'proforma' and 'proforma2' to value 'draft'
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('proforma', 'draft'), ('proforma2', 'draft')],
        table='account_invoice', write='sql')
    # copy statement_line_id values from account.move to account.move.line
    env.cr.execute("""
        UPDATE account_move_line aml
        SET statement_line_id = am.statement_line_id
        FROM account_move am
        WHERE aml.move_id = am.id AND am.statement_line_id IS NOT NULL;
    """)
    # Migrate draft payments to cancelled if they don't have any move lines
    # but they have been posted before (i.e. when move_name is set)
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_payment
        SET state = 'cancelled'
        WHERE state = 'draft' AND move_name IS NOT NULL
        AND id NOT IN (
            SELECT payment_id FROM account_move_line
            WHERE payment_id IS NOT NULL)""")
    # Populate new 'sequence' field according to previous order field 'name'
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_payment_term apt
        SET sequence = sub.sequence
        FROM (SELECT id, row_number() over (ORDER BY name asc) AS sequence
              FROM account_payment_term) sub
        WHERE sub.id = apt.id """)
    # Set accounting configuration steps to done if there are moves
    openupgrade.logged_query(
        env.cr,
        """UPDATE res_company rc
        SET account_setup_bank_data_done = TRUE,
            account_setup_bar_closed = TRUE,
            account_setup_coa_done = TRUE,
            account_setup_company_data_done = TRUE,
            account_setup_fy_data_done = TRUE
        WHERE EXISTS (
            SELECT id FROM account_move
            WHERE company_id = rc.id)""")

    migrate_account_tax_cash_basis(env)
    migrate_account_report_invoice_with_payments(env)
    fill_account_invoice_line_total(env)
    fill_account_move_line_tax_base_amount(env)
    _migrate_security(env)
    cancel_no_entry_posted_payments(env)

    openupgrade.load_data(
        env.cr, 'account', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
