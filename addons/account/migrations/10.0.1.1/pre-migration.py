# -*- coding: utf-8 -*-
# © 2017 Therp BV
# © 2021 Opener B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_invoice_state(cr):
    """In Odoo 9.0, an invoice was moved from state 'open' to state 'paid'
    on reconciliation of the move line that was linked as the trigger of
    payment subflow in the invoice workflow. This flow usually prevented
    zero amount invoices from getting into state `paid` because zero amount
    move lines are usually not reconciled. The invoice would be marked as
    `reconciled` correctly, because there was no residual amount.
    In Odoo 10.0, any invoice that is marked as `reconciled` will be moved to
    state `paid` as per `action_invoice_paid` that is triggered from the
    model's `_write` method. Preemtively set the correct state using SQL here
    for performance reasons.
    """
    openupgrade.logged_query(
        cr, """UPDATE account_invoice
        SET state = 'paid'
        WHERE state = 'open' AND reconciled""")


def precreate_column(cr, table, column, sql_type, default):
    """Create a new column of a big table with the default value the ORM
    would fill in: the ORM adds the column then writes every existing row
    with one UPDATE, while PostgreSQL (11 and later) keeps the default of
    ADD COLUMN for the existing rows without writing them. default is the
    SQL literal of the value the ORM writes."""
    if openupgrade.column_exists(cr, table, column):
        return
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ADD COLUMN "%s" %s DEFAULT %s'
        % (table, column, sql_type, default))
    openupgrade.logged_query(
        cr, 'ALTER TABLE "%s" ALTER COLUMN "%s" DROP DEFAULT' % (table, column))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # copy columns good practice in pre-mig script format of colum_spec should
    # be: { Table_name_in_db : [( old_column_name , new_column_name, type)]
    # defaults of new columname are fetchable via method get_legacy_name
    openupgrade.delete_model_workflow(env.cr, "account.invoice")
    openupgrade.rename_tables(
        cr,
        [
            ('account_operation_template', 'account_reconcile_model'),
        ]
    )
    update_invoice_state(cr)
    # makmur: about 2.1 million journal items, 4 minutes
    precreate_column(
        cr, 'account_move_line', 'tax_exigible', 'boolean', 'true')
