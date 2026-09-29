""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "crm_iap_lead": "crm_iap_mine",
    "crm_iap_lead_enrich": "crm_iap_enrich",
    "crm_iap_lead_website": "website_crm_iap_reveal",
    "mail_client_extension": "mail_plugin",
    "payment_ingenico": "payment_ogone",
    "website_mail_channel": "website_mail_group",
    # OCA/account-financial-tools
    "account_menu": "account_usability",
    # OCA/account-fiscal-rule
    "l10n_eu_oss": "l10n_eu_oss_oca",
    # OCA/account-invoice-reporting
    "account_invoice_report_utm_campaign": "account_invoice_report_utm",
    # OCA/e-commerce
    "website_sale_attribute_filter_order": "website_sale_product_attribute_filter_order",
    # OCA/project
    "project_category": "project_type",
    "project_milestone": "project_task_milestone",
    "project_stage_state": "project_task_stage_state",
    "sale_project_service_tracking_copy_tasks": "sale_project_copy_tasks",
    # OCA/sale-promotion
    "sale_coupon_chatter": "coupon_chatter",
    "sale_coupon_commercial_partner_applicability": "coupon_commercial_partner_applicability",
    "sale_coupon_mass_mailing": "coupon_mass_mailing",
    "sale_coupon_portal": "coupon_portal",
    "sale_coupon_portal_commercial_partner_applicability": "coupon_portal_commercial_partner_applicability",  # noqa: B950
    # OCA/stock-logistics-worehouse
    "stock_inventory_cost_info": "stock_quant_cost_info",
    # OCA/timesheet:
    "hr_timesheet_activity_begin_end": "hr_timesheet_begin_end",
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
    "viin_l10n_vn_einvoice_sale": "l10n_vn_viin_einvoice_sale",
    "viin_l10n_vn_hr_account": "l10n_vn_viin_hr_account",
    "to_loan_management_l10n_vn": "l10n_vn_viin_loan_management",
    # Viindoo/odoo-tvtma
    "to_tvtma_sale_crm": "viin_sale_crm",  # moved to Viindoo/erponline-enterprise
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
    # Viindoo/themes
    "theme_common": "theme_viin_common",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_extended": "account_edi",
    "l10n_be_invoice_bba": "l10n_be",
    "l10n_eu_service": "l10n_eu_oss",  # due to OCA/account-fiscal-rule
    "l10n_ch_qr_iban": "l10n_ch",
    "l10n_se_ocr": "l10n_se",
    "payment_adyen_paybylink": "payment_adyen",
    "payment_fix_register_token": "payment",
    "procurement_jit": "sale_stock",
    "sale_timesheet_edit": "sale_timesheet",
    "sale_timesheet_purchase": "sale_timesheet",
    "website_event_track_exhibitor": "website_event_exhibitor",
    "website_form": "website",
    "website_sale_management": "website_sale",
    # odoo/design-themes
    "website_animate": "website",
    # odoo/enterprise
    "stock_barcode_mobile": "stock_barcode",
    # OCA/account-financial-tools
    "stock_account_prepare_anglo_saxon_out_lines_hook": "stock_account",
    # OCA/e-commerce
    "website_sale_product_attribute_filter_visibility": "website_sale",
    # OCA/account-invoicing
    "purchase_invoicing_no_zero_line": "purchase",
    # OCA/account-invoicing
    "purchase_batch_invoicing": "purchase",
    # OCA/e-commerce
    "website_sale_cart_no_redirect": "website_sale",
    # OCA/hr
    "hr_recruitment_notification": "hr_recruitment",
    "hr_contract_type": "hr_contract",
    # OCA/e-commerce
    "website_sale_attribute_filter_price": "website_sale",
    "website_sale_stock_available_display": "website_sale_stock",
    # OCA/hr-attendance
    "hr_attendance_user_list": "hr_attendance",
    # OCA/l10n-germany
    "l10n_de_steuernummer": "base_vat",
    # OCA/l10n-spain
    "l10n_es_extra_data": "l10n_es",
    # OCA/manufacture
    "mrp_subcontracting_resupply_link": "mrp_subcontracting_purchase",
    # OCA/pos
    "pos_invoicing": "point_of_sale",
    "pos_order_line_note": "point_of_sale",
    "pos_order_mgmt": "point_of_sale",
    "pos_order_return": "point_of_sale",
    "pos_sale_order_load": "pos_sale",
    # OCA/product-attribute
    "stock_account_product_cost_security": "product_cost_security",
    # OCA/server-tools
    "base_jsonify": "jsonifier",
    # OCA/stock-logistics-reporting
    "stock_inventory_valuation_pivot": "stock_account",
    # OCA/stock-logistics-warehouse
    "stock_inventory_exclude_sublocation": "stock",
    "stock_orderpoint_manual_procurement": "stock",
    # OCA/stock-logistics-workflow
    "stock_deferred_assign": "stock",
    "stock_move_assign_picking_hook": "stock",
    # OCA/survey
    "survey_description": "survey",
    # OCA/project
    "project_mail_chatter": "project",
    "project_task_dependency": "project",
    "project_timeline_task_dependency": "project_timeline",
    # OCA/timesheet
    "sale_timesheet_order_line_sync": "sale_timesheet",
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
    "to_currency_rate": "base",
    "to_l10n_vn_currency_conversion_diff": "to_currency_conversion_diff",
    "to_lines_count_on_account_move": "to_account_accountant",
    "viin_remove_only_reference_from_one2many": "web",
    # Viindoo/erponline-enterprise
    "to_enterprise_mobile": "base",
    # Viindoo/odoo-tvtma
    "to_tvtma_crm": "viin_crm",
    "to_tvtma_sales": "viin_sale",
    # Viindoo/enterprise
    "viin_mobile_notification": "viin_mobile",
    "viin_mobile_login": "viin_mobile",
    # OCA/website
    "website_google_analytics_4": "website",
    "website_snippet_timeline": "website",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "calendar.contacts": "calendar.filters",
    "mail.moderation": "mail.group.moderation",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    "stock.inventory": "stock.quant",
    "stock.inventory.line": "stock.move.line",
}
