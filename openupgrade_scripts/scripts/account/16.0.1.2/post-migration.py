from openupgradelib import openupgrade

_deleted_xml_records = [
    "account.data_account_off_sheet",
    "account.data_account_type_credit_card",
    "account.data_account_type_current_assets",
    "account.data_account_type_current_liabilities",
    "account.data_account_type_depreciation",
    "account.data_account_type_direct_costs",
    "account.data_account_type_equity",
    "account.data_account_type_expenses",
    "account.data_account_type_fixed_assets",
    "account.data_account_type_liquidity",
    "account.data_account_type_non_current_assets",
    "account.data_account_type_non_current_liabilities",
    "account.data_account_type_other_income",
    "account.data_account_type_payable",
    "account.data_account_type_prepayments",
    "account.data_account_type_receivable",
    "account.data_account_type_revenue",
    "account.data_unaffected_earnings",
    "account.account_tax_carryover_line_comp_rule",
    "account.analytic_default_comp_rule",
]

_modules_to_install = [
    "account_sequence",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "account", "16.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state = 'to install'
        WHERE name IN %s AND state = 'uninstalled'
        """,
        (tuple(_modules_to_install),)
    )
