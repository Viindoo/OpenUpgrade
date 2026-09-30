""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "account_facturx": "account_edi_facturx",
    "sale_coupon": "coupon",
    "website_rating": "portal_rating",
    # OCA/account-consolidation
    "account_consolidation": "account_consolidation_oca",
    # OCA/account-invoice-reporting
    "account_invoice_comment_template": "account_comment_template",
    # OCA/bank-statement-import
    # "account_bank_statement_import": "account_statement_import",  # from odoo
    "account_bank_statement_import_bypass_check": "account_statement_import_bypass_check",  # noqa: B950
    "account_bank_statement_clear_partner": "account_statement_clear_partner",
    "account_bank_statement_import_camt_details": "account_statement_import_camt_details",  # noqa: B950
    "account_bank_statement_import_camt_oca": "account_statement_import_camt",
    "account_bank_statement_import_move_line": "account_statement_import_move_line",
    "account_bank_statement_import_mt940_base": "account_statement_import_mt940_base",
    "account_bank_statement_import_oca_camt54": "account_statement_import_camt54",
    "account_bank_statement_import_ofx": "account_statement_import_ofx",
    "account_bank_statement_import_online": "account_statement_import_online",
    "account_bank_statement_import_online_paypal": "account_statement_import_online_paypal",  # noqa: B950
    "account_bank_statement_import_online_ponto": "account_statement_import_online_ponto",  # noqa: B950
    "account_bank_statement_import_online_qonto": "account_statement_import_online_qonto",  # noqa: B950
    "account_bank_statement_import_online_transferwise": "account_statement_import_online_transferwise",  # noqa: B950
    "account_bank_statement_import_paypal": "account_statement_import_paypal",
    "account_bank_statement_import_qif": "account_statement_import_qif",
    "account_bank_statement_import_split": "account_statement_import_split",
    "account_bank_statement_import_save_file": "account_statement_import_save_file",
    "account_bank_statement_import_transfer_move": "account_statement_import_transfer_move",  # noqa: B950
    "account_bank_statement_import_txt_xlsx": "account_statement_import_txt_xlsx",
    # OCA/e-commerce
    "website_sale_attribute_filter_category": "website_sale_product_attribute_filter_category",  # noqa: B950
    # OCA/event
    "website_event_crm": "website_event_crm_invitation",
    # OCA/edi
    "account_e-invoice_generate": "account_einvoice_generate",
    "edi": "edi_oca",
    "edi_account": "edi_account_oca",
    "edi_backend_partner": "edi_backend_partner_oca",
    "edi_exchange_template": "edi_exchange_template_oca",
    "edi_storage": "edi_storage_oca",
    "edi_voxel": "edi_voxel_oca",
    "edi_voxel_account_invoice": "edi_voxel_account_invoice_oca",
    "edi_voxel_sale_order_import": "edi_voxel_sale_order_import_oca",
    "edi_voxel_sale_secondary_unit": "edi_voxel_sale_secondary_unit_oca",
    "edi_voxel_secondary_unit": "edi_voxel_secondary_unit_oca",
    "edi_voxel_stock_picking": "edi_voxel_stock_picking_oca",
    "edi_voxel_stock_picking_secondary_unit": "edi_voxel_stock_picking_secondary_unit_oca",  # noqa: B950
    "edi_webservice": "edi_webservice_oca",
    "edi_xml": "edi_xml_oca",
    # OCA/hr-holidays
    "hr_leave_hour": "hr_leave_custom_hour_interval",
    # OCA/l10n-belgium
    "account_bank_statement_import_coda": "account_statement_import_coda",
    # OCA/l10n-spain
    "l10n_es_account_bank_statement_import_n43": "l10n_es_account_statement_import_n43",
    # OCA/manufacture
    "account_move_line_manufacture_info": "account_move_line_mrp_info",
    # OCA/pos
    "pos_picking_load": "pos_sale_order_load",
    # OCA/server-tools
    "base_jsonify": "jsonifier",
    "openupgrade_records": "upgrade_analysis",
    # OCA/website
    "website_analytics_piwik": "website_analytics_matomo",
    # OCA/l10n-italy
    "l10n_it_account_balance_report": "l10n_it_financial_statements_report",
    "l10n_it_causali_pagamento": "l10n_it_payment_reason",
    "l10n_it_codici_carica": "l10n_it_appointment_code",
    "l10n_it_dichiarazione_intento": "l10n_it_declaration_of_intent",
    "l10n_it_withholding_tax_causali": "l10n_it_withholding_tax_reason",
    # OCA/l10n-france
    "account_bank_statement_import_fr_cfonb": "account_statement_import_fr_cfonb",
    # OCA/...
    # Viindoo/tvtmaaddons
    "to_print_payment_vi": "viin_l10n_vn_payment_print",
    "to_hr_recruitment_request": "viin_hr_recruitment_approval",
    "to_tvtma_hr": "viin_hr",
    "to_foreign_trade_currency_rate": "viin_foreign_trade_currency_rate",
    "to_l10n_vn_foreign_trade": "viin_l10n_vn_foreign_trade",
    "to_transit_loc_accounts": "viin_stock_internal_transit_valuation",
    "viin_transit_loc_accounts_specific_identification": "viin_stock_internal_transit_valuation_specific_identification",  # noqa: B950
    "to_partner_share_holder": "viin_partner_shareholder",
    "to_hr_resoucre_calendar_rate": "viin_resource_calendar_rate",
    "to_account_bank_statement_import_rje": "viin_account_bank_statement_import_rje",
    "account_bank_statement_import": "viin_account_bank_statement_import",
    "to_foreign_trade": "viin_foreign_trade",
    "to_l10n_vn_employee_advance": "viin_l10n_vn_hr_account",
    "to_einvoice_common": "l10n_vn_edi",
    "to_einvoice_summary": "l10n_vn_edi_summary",
    "to_accounting_sinvoice": "viin_l10n_vn_accounting_sinvoice",
    "to_accounting_vninvoice": "viin_l10n_vn_accounting_vninvoice",
    "to_accounting_vninvoice_summary": "viin_l10n_vn_accounting_vninvoice_summary",
    "to_stock_product_allocation": "to_stock_product_allocation_approval",
    # Viindoo/erponline-enterprise
    "to_enterprice_marks_account": "to_enterprise_marks_account",
    "to_enterprice_marks_mrp": "to_enterprise_marks_mrp",
    "to_hide_ent_modules_website_theme_install": "to_hide_ent_modules_website_theme",
    "to_enterprice_marks_inter_company": "to_enterprise_marks_inter_company",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # Viindoo/tvtmaaddons: removed in 14.0 without a successor (public holidays
    # per year are part of resource.calendar.leaves)
    "to_holidays_in_years": "resource",
    # odoo
    "account_analytic_default": "account",
    "account_analytic_default_hr_expense": "hr_expense",
    "account_analytic_default_purchase": "purchase",
    "hr_expense_check": "hr_expense",
    "hr_holidays_calendar": "hr_holidays",
    "hw_proxy": "hw_drivers",
    "l10n_cn_small_business": "l10n_cn",
    "partner_autocomplete_address_extended": "base_address_extended",
    "payment_stripe_checkout_webhook": "payment_stripe",
    "pos_cash_rounding": "point_of_sale",
    "pos_kitchen_printer": "pos_restaurant",
    "pos_reprint": "point_of_sale",
    "website_theme_install": "website",
    # odoo/design-themes
    "theme_graphene_blog": "theme_graphene",
    # odoo/enterprise
    "hr_holidays_gantt_calendar": "hr_holidays_gantt",
    # OCA/helpdesk
    "helpdesk_mgmt_timesheet_time_control": "helpdesk_mgmt_timesheet",
    # OCA/hr -> OCA/payroll:
    "hr_period": "hr_payroll_period",
    # OCA/intrastat-extrastat
    "hs_code_link": "product_harmonized_system_delivery",
    # OCA/event
    "website_event_questions_free_text": "website_event_questions",
    # OCA/e-commerce
    "website_sale_product_style_badge": "website_sale",
    "website_snippet_carousel_product": "website_sale",
    # OCA/l10n-netherlands
    "l10n_nl_tax_invoice_basis": "l10n_nl_tax_statement",
    # OCA/margin-analysis
    "sale_order_margin_percent": "sale_margin",
    # OCA/partner-contact
    "base_vat_sanitized": "base_vat",
    "partner_bank_active": "base",
    # OCA/pos
    "pos_ticket_logo": "point_of_sale",
    # OCA/project
    "project_description": "project",
    "project_stage_closed": "project",
    # OCA/purchase-workflow
    "purchase_tier_validation_forward": "base_tier_validation_forward",
    # OCA/reporting-engine
    "bi_sql_editor_aggregate": "bi_sql_editor",
    # OCA/sale-reporting
    "report_qweb_pdf_fixed_column": "web",
    # OCA/sale-workflow
    "sale_mrp_link": "sale_mrp",
    "sale_order_price_recalculation": "sale",
    "sale_order_pricelist_tracking": "sale",
    # OCA/stock-logistics-warehouse
    "stock_inventory_include_exhausted": "stock",
    # OCA/web
    "web_editor_background_color": "web_editor",
    # OCA/website
    "website_cookie_notice": "website",
    "website_form_recaptcha": "website_form",
    "website_crm_recaptcha": "website_form",
    # OCA/web
    "web_confirm_duplicate": "web_copy_confirm",
    # OCA/...
    # Viindoo/tvtmaaddons
    "to_l10n_vn_qweb_layout": "l10n_vn_common",
    "to_l10n_vn_account_detail_sheet": "to_account_reports_l10n_vn",
    "to_l10n_vn_general_ledger": "to_account_reports_l10n_vn",
    "viin_l10n_vn_account_cash_book": "to_account_reports_l10n_vn",
    "viin_l10n_vn_invoice_declaration": "to_account_reports_l10n_vn",
    "to_foreign_trade_landed_cost": "viin_foreign_trade",
    "viin_l10n_vn_einvoice_common": "l10n_vn_edi",
    "to_warehouse_imp": "viin_stock",
    "to_l10n_vn_state_group": "to_res_state_group",
    "to_account_expense_tracking": "to_hr_expense",
    "to_l10n_vn_fleet_driver": "to_fleet_driver",
    "to_hr_holidays_period_limit": "hr_holidays",
    "to_hr_work_day_type": "hr",
    # no 14.0 code; website(_sale) 14.0 has its own search box (s_products_searchbar)
    "to_website_search_suggestion": "website",
    "to_website_search_suggestion_product": "website_sale",
    "to_shorten_url": "link_tracker",
    "to_website_registration_email_blacklist": "to_registration_email_blacklist",
    # removed in 14.0; auto-installed as soon as l10n_vn gets installed otherwise
    "viin_l10n_vn_account_payment_internal_transfer": "l10n_vn",
    # Viindoo/odoo-tvtma
    "viin_hr_department_multilang": "viin_hr",
    "to_website_erponline_cart": "website_sale",
    # a data module of the ERPOnline website, not ported beyond 13.0: its records
    # (website, pages, menus, blog, forum) are all noupdate and stay with the theme
    "to_website_erponline_data": "theme_erponline",
    "to_website_language_menu_erponline_data": "to_website_language_menu",
    "to_website_menu_icon_erponline_data": "to_website_menu_icon",
    # Viindoo/odoo-joomla2odoo
    "to_redirect_early": "website",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "crm.lead.tag": "crm.tag",
    "email_template.preview": "mail.template.preview",
    "event.answer": "event.question.answer",
    "product.style": "product.ribbon",
    "report.sale_coupon.report_coupon": "report.coupon.report_coupon",
    "sale.coupon": "coupon.coupon",
    "sale.coupon.generate": "coupon.generate.wizard",
    "sale.coupon.program": "coupon.program",
    "sale.coupon.reward": "coupon.reward",
    "sale.coupon.rule": "coupon.rule",
    "survey.user_input_line": "survey.user_input.line",
    "survey.label": "survey.question.answer",
    # OCA/bank-statement-import
    "account.bank.statement.import": "account.statement.import",
    # OCA/server-tools
    "openupgrade.analysis.wizard": "upgrade.analysis",
    "openupgrade.attribute": "upgrade.attribute",
    "openupgrade.comparison.config": "upgrade.comparison.config",
    "openupgrade.record": "upgrade.record",
    "openupgrade.generate.records.wizard": "upgrade.generate.record.wizard",
    "openupgrade.install.all.wizard": "upgrade.install.wizard",
    # Viindoo/tvtmaaddons
    # Viindoo/erponline-enterprise
    "account.asset.asset.add.wizard": "asset.fill.missing.values.wizard",
}

# only used here for upgrade_analysis
merged_models = {
    "account.sinvoice.serial": "account.einvoice.serial",
    "account.sinvoice.template": "account.einvoice.template",
    "account.sinvoice.type": "account.einvoice.type",
    "account.vninvoice.serial": "account.einvoice.serial",
    "account.vninvoice.template": "account.einvoice.template",
    "account.vninvoice.type": "account.einvoice.type",
}

# Modules of merged_modules that are not merged into anything: they are
# removed without a successor on our addons paths. The technical records they
# own (record rules, scheduled and server actions, views, menus, mail
# templates...) are deleted by the update even when they are noupdate, and the
# xml ids of records of models that go with them are detached: see
# release_records_of_lost_modules in the pre-migration of base.
lost_modules = [
    "to_holidays_in_years",
    "to_hr_work_day_type",
    "to_website_search_suggestion",
    "to_website_search_suggestion_product",
    "web_diagram",
]
