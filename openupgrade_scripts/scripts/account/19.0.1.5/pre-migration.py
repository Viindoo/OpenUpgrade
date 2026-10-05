# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    ("taxable_supply_date", "account.move", "account_move", "date", None, "account"),
    (
        "deductible_amount",
        "account.move.line",
        "account_move_line",
        "float",
        None,
        "account",
        100,
    ),
    (
        "is_storno",
        "account.move.line",
        "account_move_line",
        "boolean",
        None,
        "account",
        False,
    ),
    (
        "no_followup",
        "account.move.line",
        "account_move_line",
        "boolean",
        None,
        "account",
        False,
    ),
    (
        "allow_foreign_vat",
        "account.report",
        "account_report",
        "boolean",
        None,
        "account",
        False,
    ),
]

_renamed_fields = [
    (
        "res.company",
        "res_company",
        "check_account_audit_trail",
        "restrictive_audit_trail",
    ),
]


_renamed_xmlids = [
    (
        "account_peppol_selfbilling.email_template_edi_self_billing_credit_note",
        "account.email_template_edi_self_billing_credit_note",
    ),
    (
        "account_peppol_selfbilling.email_template_edi_self_billing_invoice",
        "account.email_template_edi_self_billing_invoice",
    ),
]


def account_journal_invoice_reference_type(env):
    """
    Map account.journal#invoice_reference_type value 'none' to 'invoice'
    """
    openupgrade.copy_columns(
        env.cr, {"account_journal": [("invoice_reference_type", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("invoice_reference_type"),
        "invoice_reference_type",
        [("none", "invoice")],
        table="account_journal",
    )


def account_report(env):
    """
    Map account.report#default_opening_date_filter values 'previous_tax_period',
    'this_tax_period' to 'previous_return_period', 'this_return_period'
    Map account.report#filter_multi_company value 'disabled' to None
    """
    openupgrade.copy_columns(
        env.cr, {"account_report": [("default_opening_date_filter", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("default_opening_date_filter"),
        "default_opening_date_filter",
        [
            ("this_tax_period", "this_return_period"),
            ("previous_tax_period", "previous_return_period"),
        ],
        table="account_report",
    )
    openupgrade.copy_columns(
        env.cr, {"account_report": [("filter_multi_company", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("filter_multi_company"),
        "filter_multi_company",
        [
            ("disabled", False),
        ],
        table="account_report",
    )


def account_report_expression(env):
    """
    Map account.report.expression#date_scope value 'previous_tax_period' to
    'previous_return_period'
    """
    openupgrade.copy_columns(
        env.cr, {"account_report_expression": [("date_scope", None, None)]}
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("date_scope"),
        "date_scope",
        [
            ("previous_tax_period", "previous_return_period"),
        ],
        table="account_report_expression",
    )


def account_reconcile_model_archive(env):
    """The invoice_matching reconciliation model no longer exist and have been
    integrated into account_reconcile_oca; in any case, they must be archived
    to prevent buttons (in the reconciliation) from appearing for items
    (models) that do nothing.
    """
    env.cr.execute(
        """
        UPDATE account_reconcile_model
        SET active = False
        WHERE rule_type = 'invoice_matching'
        """
    )


def res_company_category_default_accounts(env):
    """
    Since 19.0 the company holds the default income and expense accounts of the
    product categories (income_account_id, expense_account_id) and writes them
    as the defaults of the categories (ir.default) on every write of a company
    (_set_category_defaults). The new columns take the defaults the categories
    have, the one of the company first, else the global one when the account is
    one of the company: left empty, the first write on a company replaces the
    defaults of the categories with nothing (the end-migration only fills the
    columns from a chart template, a company without one keeps them empty).
    """
    openupgrade.add_fields(
        env,
        [
            (
                "income_account_id",
                "res.company",
                "res_company",
                "many2one",
                None,
                "account",
            ),
            (
                "expense_account_id",
                "res.company",
                "res_company",
                "many2one",
                None,
                "account",
            ),
        ],
    )
    for column, field_name in (
        ("income_account_id", "property_account_income_categ_id"),
        ("expense_account_id", "property_account_expense_categ_id"),
    ):
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE res_company c
            SET {column} = a.id
            FROM (
                SELECT DISTINCT ON (rc.id) rc.id AS company_id, d.json_value
                FROM res_company rc
                JOIN ir_default d
                    ON d.company_id = rc.id OR d.company_id IS NULL
                JOIN ir_model_fields f ON f.id = d.field_id
                WHERE f.model = 'product.category' AND f.name = %s
                    AND d.user_id IS NULL AND d.condition IS NULL
                ORDER BY rc.id, d.company_id NULLS LAST, d.id
            ) dv
            JOIN account_account a ON a.id = CASE
                WHEN dv.json_value ~ '^[0-9]+$' THEN dv.json_value::int END
            JOIN account_account_res_company_rel r
                ON r.account_account_id = a.id
            WHERE c.id = dv.company_id AND r.res_company_id = c.id
                AND c.{column} IS NULL
            """,
            (field_name,),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    account_journal_invoice_reference_type(env)
    account_report(env)
    account_report_expression(env)
    account_reconcile_model_archive(env)
    res_company_category_default_accounts(env)
