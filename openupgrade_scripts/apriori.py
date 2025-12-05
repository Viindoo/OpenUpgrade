""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "note": "project_todo",
    "sale_quotation_builder": "sale_pdf_quote_builder",
    "website_sale_delivery_mondialrelay": "website_sale_mondialrelay",
    # odoo/enterprise
    # OCA/delivery-carrier
    "delivery_carrier_customer_info": "partner_delivery_info",
    # OCA/social
    "mail_activity_unlink_log": "mail_activity_cancel_tracking",
    # Viindoo/tvtmaaddons
    "to_org_chart": "web_hierarchy",
    "viin_loan_management_patch_1": "viin_loan_management_bank_currency_rate",
    "viin_mail_channel_privacy": "viin_discuss_channel_privacy",
    "viin_website_event_checkin": "viin_event_checkin_website",
    # Viindoo/erponline-enterprise
    "viin_account_subscription": "viin_account_recurring",
    # Viindoo/customer-pecc3
    "viin_pecc3_project_template_document": "viin_pecc3_project_document",
    "viin_project_role_progress": "viin_pecc3_project_role_progress",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_payment_invoice_online_payment_patch": "account_payment",
    "account_sequence": "account",
    "association": "membership",
    "l10n_de_skr03": "l10n_de",
    "l10n_de_skr04": "l10n_de",
    "l10n_generic_coa": "account",
    "l10n_hr_euro": "l10n_hr",
    "l10n_in_tcs_tds": "l10n_in",
    "l10n_in_upi": "l10n_in",
    "l10n_latam_account_sequence": "l10n_latam_invoice_document",
    "l10n_multilang": "account",
    "loyalty_delivery": "sale_loyalty_delivery",
    "pos_cache": "point_of_sale",
    "pos_daily_sales_reports": "point_of_sale",
    "pos_epson_printer_restaurant": "point_of_sale",
    "purchase_price_diff": "purchase_stock",
    "spreadsheet_dashboard_sale_expense": "spreadsheet_dashboard_hr_expense",
    "web_kanban_gauge": "web",
    "website_event_crm_questions": "website_event_crm",
    "website_event_questions": "website_event",
    "website_payment_paypal": "website_payment",
    "website_sale_delivery": "website_sale",
    "website_sale_digital": "website_sale",
    "website_sale_loyalty_delivery": "website_sale_loyalty",
    "website_sale_stock_product_configurator": "website_sale_product_configurator",
    # OCA/account-invoicing
    "account_invoice_fiscal_position_update": "account",
    # OCA/e-commerce
    "website_sale_invoice_address": "website_sale",
    # OCA/hr-attendance
    "hr_attendance_geolocation": "hr_attendance",
    # OCA/l10n-germany
    "l10n_de_skr03_mis_reports": "l10n_de_mis_reports",
    "l10n_de_skr04_mis_reports": "l10n_de_mis_reports",
    # OCA/l10n-spain
    "l10n_es_dua": "l10n_es",
    "l10n_es_dua_sii": "l10n_es_aeat_sii_oca",
    "l10n_es_irnr": "l10n_es",
    "l10n_es_irnr_sii": "l10n_es_aeat_sii_oca",
    # OCA/maintenance
    "base_maintenance_config": "maintenance",
    "maintenance_plan": "maintenance",
    "maintenance_plan_activity": "maintenance",
    "maintenance_plan_employee": "maintenance",
    # OCA/product-attribute
    "product_catalog": "product",
    "product_catalog_sale": "sale",
    # OCA/purchase-workflow
    "purchase_discount": "purchase",
    # OCA/sale-promotion
    "loyalty_initial_date_validity": "loyalty",
    "sale_loyalty_initial_date_validity": "sale_loyalty",
    # OCA/sale-reporting
    "sale_report_country_state": "sale",
    # OCA/social
    "mail_activity_plan": "mail",
    "mass_mailing_custom_unsubscribe_event": "mass_mailing",
    # OCA/stock-logistics-warehouse
    "stock_lot_filter_available": "stock",
    # OCA/web
    "web_advanced_search": "web",
    "web_chatter_position": "web",
    "web_listview_range_select": "web",
    "web_pwa_oca": "web",
    # OCA/...
    # Viindoo/tvtmaaddons
    "l10n_vn_viin_account_qr_code_emv": "l10n_vn",
    "l10n_vn_viin_accounting_sinvoice_patch1": "l10n_vn_viin_accounting_sinvoice",
    "l10n_vn_viin_edi_patch2": "l10n_vn_viin_edi",
    "l10n_vn_viin_edi_patch3": "l10n_vn_viin_edi",
    "to_company_hotline": "base",
    "to_hr_payroll_patch1": "to_hr_payroll",
    "to_hr_timesheet_payroll_patch1": "to_hr_timesheet_payroll",
    "to_location_warehouse": "viin_stock",
    "to_mail_notif_and_email": "mail",
    "to_sale_loyalty_patch_1": "viin_loyalty",
    "to_stock_report_common": "viin_stock",
    "to_vietnam_bank_icons": "payment",
    "to_vietnamese_number2words": "base",
    "to_website_recaptcha": "google_recaptcha",
    "to_website_recaptcha_signup": "auth_signup",
    "viin_account_auto_transfer_patch_1": "viin_account_auto_transfer",
    "viin_account_qr_code_emv": "account_qr_code_emv",
    "viin_affiliate_website_patch": "viin_affiliate_website",
    "viin_analytic_tag": "viin_account",
    "viin_event_barcodes": "event",
    "viin_event_checkin": "event",
    "viin_event_checkin_crm": "event_crm",
    "viin_google_spreadsheet": "spreadsheet_oca",
    "viin_helpdesk_team_ticket_type": "viin_helpdesk",
    "viin_helpdesk_ticket_properties": "viin_helpdesk",
    "viin_hr_assignment_log": "viin_mail_tracking",
    "viin_hr_overtime_timeoff": "viin_hr_overtime",
    "viin_mail_search": "mail",
    "viin_resource_calendar_rate": "viin_hr_work_entry",
    "viin_sale_crm_follower_access_right": "viin_sales_team_collaboration",
    "viin_spreadsheet_dashboard": "spreadsheet_dashboard",
    "viin_unicode_slugify": "http_routing",
    "viin_user_assignment_log": "viin_mail_tracking",
    "viin_wallet_affiliate": "to_wallet",
    "viin_web_editor": "web_editor",
    "viin_website_form_helpdesk": "viin_website_helpdesk",
    "viin_website_helpdesk_ticket_properties": "viin_website_helpdesk",
    "viin_website_livechat": "website_livechat",
    # Viindoo/erponline-enterprise
    "to_account_asset_patch1": "to_account_asset",
    "to_account_asset_patch2": "to_account_asset",
    "to_account_asset_patch3": "to_account_asset",
    "to_account_budget_hr_timesheet_patch1": "to_account_budget_hr_timesheet",
    "to_account_budget_hr_timesheet_patch2": "to_account_budget_hr_timesheet",
    "to_account_budget_hr_timesheet_patch3": "to_account_budget_hr_timesheet",
    "to_account_budget_patch1": "to_account_budget",
    "to_mrp_multi_warehouse_access_control": "to_multi_warehouse_access_control_mrp",
    "viin_features_activate_account_patch_1": "viin_features_activate_account",
    "viin_mail_ice_server_data": "web_editor",
    "viin_product_recurring": "viin_sale_recurring",
    "viin_sem_website_blog": "viin_website_seo_advisor",
    "viin_sem_website_forum": "viin_website_seo_advisor",
    "viin_stock_patch1": "viin_stock",
    "viin_subscription": "viin_sale_subscription",
    # Viindoo/branding
    "viin_brand_iap": "iap",
    "viin_brand_note": "project_todo",
    "viin_brand_purchase_stock": "purchase_stock",
    "viin_brand_sale_quotation_builder": "sale_pdf_quote_builder",
    "viin_brand_sale_stock": "sale_stock",
    "viin_brand_stock_account": "stock_account",
    "viin_brand_website_livechat": "website_livechat",
    # Viindoo/saas-infrastructure
    "l10n_vn_viin_einvoice_saas_subscription": "l10n_vn_viin_einvoice_sale",
    "l10n_vn_viin_einvoice_saas_subscription_marketplace": "l10n_vn_viin_einvoice_sale",
    # Viindoo/odoo-tvtma
    "l10n_vn_viin_viindoo_edi": "l10n_vn_viin_edi",
    # Viindoo/customer-pecc3
    "viin_analytic_category": "analytic",
    "viin_hr_timesheet_analytic_category": "hr_timesheet",
    "viin_pecc3_project_budget": "viin_pecc3_project_info",
    "viin_pecc3_project_hr_expense_budget": "viin_pecc3_project_info",
    "viin_pecc3_project_role_budget": "viin_pecc3_project_info",
    "viin_pecc3_project_template_approval": "viin_pecc3_project_task_assignment_report",
    "viin_pecc3_project_approval": "viin_pecc3_project_task_assignment_report",
    "viin_pecc3_project_template_info": "viin_pecc3_project_info",
    "viin_pecc3_project_template_quatity": "viin_pecc3_quality_project",
    "viin_pecc3_project_template_quality_checklist": "viin_pecc3_project_quality_checklist",  # noqa: E501
    "viin_pecc3_project_template_task_noti": "viin_pecc3_project_task_noti",
    "viin_project_template": "project",
    "viin_project_template_quality": "viin_quality_project",
    "viin_project_template_role": "viin_project_role",
    "viin_project_view_all_tasks": "project",
    "viin_searchpanel_horizontal_scrollbar": "web",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "hr.leave.stress.day": "hr.leave.mandatory.day",
    "mail.channel": "discuss.channel",
    "mail.channel.member": "discuss.channel.member",
    "mail.channel.rtc.session": "discuss.channel.rtc.session",
    "mailing.contact.subscription": "mailing.subscription",
    "payment.icon": "payment.method",
    "restaurant.printer": "pos.printer",
    # OCA/...
    # Viindoo/erponline-enterprise
    "product.recurrence": "product.period.discount",
    "product.temporal.recurrence": "sale.period",
    "subscription.closing.reason": "subscription.close.reason",
    "appointment.type": "viin.appointment.type",
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "repair.line": "stock.move",
    # OCA/...
}
