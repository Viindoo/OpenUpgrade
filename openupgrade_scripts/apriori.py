""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "crm_iap_lead": "crm_iap_mine",
    "crm_iap_lead_enrich": "crm_iap_enrich",
    "crm_iap_lead_website": "website_crm_iap_reveal",
    "l10n_eu_service": "l10n_eu_oss",
    "mail_client_extension": "mail_plugin",
    "payment_ingenico": "payment_ogone",
    # OCA/project
    "project_stage_state": "project_task_stage_state",
    # OCA/...
    # Viindoo/tvtmaaddons
    "to_hr_employee_birthday_filters": "viin_hr_employee_birthday",
    "to_equipment_hierarchy": "viin_maintenance",
    "viin_hr_equipment_hierarchy": "viin_hr_maintenance",
    "to_slugify_l10n_vn": "viin_unicode_slugify",
    "to_res_state_group": "viin_base_state_group",
    "to_l10n_vn_hr_payroll": "l10n_vn_viin_hr_payroll",
    "to_l10n_vn_picking_operation": "l10n_vn_viin_picking_operation",
    "to_l10n_vn_account_balance_carry_forward": "l10n_vn_viin_account_balance_carry_forward",
    "l10n_vn_edi": "l10n_vn_viin_edi",
    "viin_l10n_vn_accounting_sinvoice": "l10n_vn_viin_accounting_sinvoice",
    "to_l10n_vn_hr_payroll_account": "l10n_vn_viin_hr_payroll_account",
    "to_l10n_vn_hr_payroll_meal_account": "l10n_vn_viin_hr_payroll_meal_account",
    "to_l10n_vn_stock_reports": "l10n_vn_viin_stock_reports",
    # Viindoo/erponline-enterprise
    "to_enterprise_marks_account": "viin_hide_ent_modules_account",
    "viin_mobile_notification_firebase": "viin_mobile_firebase",
    "to_enterprise_marks_inter_company": "viin_hide_ent_modules_inter_company",
    "to_enterprise_marks_mrp": "viin_hide_ent_modules_mrp",
    "to_enterprise_marks_stock": "viin_hide_ent_modules_stock",
    "viin_enterprise_marks_event": "viin_hide_ent_modules_event",
    "viin_enterprise_marks_expense": "viin_hide_ent_modules_expense",
    "viin_enterprise_marks_hr_timesheet": "viin_hide_ent_modules_hr_timesheet",
    "viin_enterprise_marks_project": "viin_hide_ent_modules_project",
    "viin_enterprise_marks_sale": "viin_hide_ent_modules_sale",
    "viin_enterprise_marks_purchase": "viin_hide_ent_modules_purchase",
    "viin_enterprise_marks_website": "viin_hide_ent_modules_websitewebsite",
    "to_l10n_vn_account_asset": "l10n_vn_viin_account_asset",
    "to_l10n_vn_account_asset_sale": "l10n_vn_viin_account_asset_sale",
    "to_account_reports_l10n_vn": "l10n_vn_viin_account_reports",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_extended": "account_edi",
    "l10n_be_invoice_bba": "l10n_be",
    "l10n_ch_qr_iban": "l10n_ch",
    "l10n_se_ocr": "l10n_se",
    "payment_fix_register_token": "payment",
    "procurement_jit": "sale_stock",
    "sale_timesheet_edit": "sale_timesheet",
    "website_event_track_exhibitor": "website_event_exhibitor",
    "website_form": "website",
    "website_sale_management": "website_sale",
    # OCA/...
    # OCA/account-financial-tools
    "stock_account_prepare_anglo_saxon_out_lines_hook": "stock_account",
    # OCA/stock-logistics-workflow
    "stock_move_assign_picking_hook": "stock",
    # OCA/web
    "web_decimal_numpad_dot": "web",
    # Viindoo/tvtmaaddons
    "to_partner_business_type": "viin_partner_business_nature",
    "to_partner_employee_size": "viin_partner_business_nature",
    "to_partner_ownership_type": "viin_partner_business_nature",
    "viin_crm_business_type": "viin_crm_business_nature",
    "viin_crm_employee_size": "viin_crm_business_nature",
    "to_hr_public_employee_birthday_filters": "viin_hr_employee_birthday",
    "to_equipment_image": "viin_maintenance",
    "l10n_vn_c133": "l10n_vn_viin",
    "l10n_vn_c200": "l10n_vn_viin",
    "l10n_vn_common": "l10n_vn_viin",
    "to_account_financial_income": "viin_account",
    "to_account_income_deduct": "viin_account",
    "viin_l10n_vn_account_move_print": "l10n_vn_viin",
    "viin_l10n_vn_payment_print": "l10n_vn_viin",
    "viin_payment_mediate": "viin_account",
    # Viindoo/odoo-tvtma
    "to_tvtma_crm": "viin_crm",
    "to_tvtma_sales": "viin_sale",
    # Viindoo/enterprise
    "viin_mobile_notification": "viin_mobile",
    "viin_mobile_login": "viin_mobile",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "calendar.contacts": "calendar.filters",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {}
