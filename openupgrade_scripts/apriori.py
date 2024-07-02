""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "coupon": "loyalty",
    "payment_test": "payment_demo",
    "payment_transfer": "payment_custom",
    "sale_coupon": "sale_loyalty",
    "sale_coupon_delivery": "sale_loyalty_delivery",
    "website_sale_coupon": "website_sale_loyalty",
    "website_sale_coupon_delivery": "website_sale_loyalty_delivery",
    # odoo/enterprise
    "helpdesk_sale_coupon": "helpdesk_sale_loyalty",
    "sale_coupon_taxcloud": "sale_loyalty_taxcloud",
    "sale_coupon_taxcloud_delivery": "sale_loyalty_taxcloud_delivery",
    # OCA/account-reconcile
    "account_reconciliation_widget": "account_reconcile_oca",
    # OCA/bank-statement-import
    "account_bank_statement_import_qif": "account_statement_import_qif",
    "account_statement_import": "account_statement_import_file",
    "account_statement_import_file_reconciliation_widget": (
        "account_statement_import_file_reconcile_oca"
    ),
    "account_statement_import_txt_xlsx": "account_statement_import_sheet_file",
    # OCA/crm
    "crm_project": "crm_lead_to_task",
    # OCA/knowledge
    "knowledge": "document_knowledge",
    # OCA/project
    "project_stage_mgmt": "project_task_stage_mgmt",
    # OCA/sale-promotion
    "coupon_incompatibility": "loyalty_incompatibility",
    "coupon_limit": "loyalty_limit",
    "coupon_mass_mailing": "loyalty_mass_mailing",
    "coupon_multi_gift": "loyalty_multi_gift",
    "coupon_criteria_multi_product": "loyalty_criteria_multi_product",
    "sale_coupon_criteria_multi_product": "sale_loyalty_criteria_multi_product",
    "sale_coupon_incompatibility": "sale_loyalty_incompatibility",
    "sale_coupon_limit": "sale_loyalty_limit",
    "sale_coupon_multi_gift": "sale_loyalty_multi_gift",
    "sale_coupon_order_line_link": "sale_loyalty_order_line_link",
    "sale_coupon_order_suggestion": "sale_loyalty_order_suggestion",
    "sale_coupon_partner": "sale_loyalty_partner",
    "website_sale_coupon_page": "website_sale_loyalty_page",
    "website_sale_coupon_selection_wizard": "website_sale_loyalty_suggestion_wizard",
    # OCA/server-ux
    "mass_editing": "server_action_mass_edit",
    # OCA/l10n-italy
    "l10n_it_ricevute_bancarie": "l10n_it_riba",
    # OCA/...
    # Viindoo/tvtmaaddons
    "to_affiliate": "viin_affiliate",
    "to_affiliate_sale": "viin_affiliate_sale",
    "to_website_affiliate": "viin_affiliate_website",
    "to_hr_skills_recruitment": "viin_hr_recruitment_skills_resume",
    "to_mrp_account": "viin_mrp_account",
    "to_orderpoint_mail_thread": "viin_mail_thread_stock",
    "to_partner_tax_code": "viin_partner_tax_code",
    "to_project_access": "viin_project",
    "to_stock_backdate": "viin_stock_backdate",
    "to_stock_picking_backdate": "viin_stock_account_backdate",
    "to_uom_mail_thread": "viin_mail_thread_uom",
    "to_stock_production_lot_partner_infor": "viin_stock_lot_partner_infor",
    "to_account_balance_carry_forward": "viin_account_auto_transfer",
    "l10n_vn_viin_account_balance_carry_forward": "l10n_vn_viin_account_auto_transfer",
    # google_drive, google_spreadsheet is orinally from odoo but has been remove since 16.0
    # because of some technical problem but they have been brought back in viindoo yeahh
    "google_drive": "viin_google_drive",
    "google_spreadsheet": "viin_google_spreadsheet",
    "viin_product_categ_mail_thread": "viin_mail_thread_account",
    "viin_product_categ_mail_thread_purchase": "viin_mail_thread_purchase",
    "viin_product_categ_mail_thread_stock_account": "viin_mail_thread_stock_account",
    "viin_webp": "viin_web_editor",
    "viin_user_assignment_log_project": "test_viin_user_assignment_log_project",
    # Viindoo/enterprise
    # Viindoo/odoo-tvtma
    "viin_saas_membership_white_label": "viin_saas_reseller_white_label",
    "viin_viindoo_membership": "viin_viindoo_saas_reseller",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_facturx": "account_edi_ubl_cii",
    "account_edi_ubl": "account_edi_ubl_cii",
    "account_edi_ubl_bis3": "account_edi_ubl_cii",
    "account_sale_timesheet": "sale_project",
    "base_address_city": "base_address_extended",
    "fetchmail": "mail",
    "fetchmail_gmail": "google_gmail",
    "fetchmail_outlook": "microsoft_outlook",
    "gift_card ": "loyalty",
    "l10n_be_edi": "account_edi_ubl_cii",
    "l10n_nl_edi": "account_edi_ubl_cii",
    "l10n_no_edi": "account_edi_ubl_cii",
    "note_pad": "note",
    "pad": "web_editor",
    "pad_project": "project",
    "pos_coupon": "pos_loyalty",
    "pos_gift_card": "pos_loyalty",
    "project_account": "project",
    "sale_gift_card": "sale_loyalty",
    "sale_project_account": "sale_project",
    "website_sale_delivery_giftcard": "website_sale_loyalty_delivery",
    "website_sale_gift_card": "website_sale_loyalty",
    # OCA/account-financial-tools
    "account_balance_line": "account",
    "account_move_force_removal": "account",
    # OCA/account-invoicing
    "account_invoice_search_by_reference": "account",
    # OCA/account-invoice-reporting
    "account_invoice_report_due_list": "account",
    # OCA/e-commerce
    "website_sale_require_login": "website_sale",
    # OCA/pos
    "pos_margin_account_invoice_margin": "point_of_sale",
    "pos_order_line_no_unlink": "point_of_sale",
    "pos_product_sort": "point_of_sale",
    # OCA/product-variant
    "purchase_variant_configurator_on_confirm": "purchase_variant_configurator",
    # OCA/project
    "project_task_milestone": "project",
    # OCA/purchase-workflow
    "product_form_purchase_link": "purchase",
    # OCA/sale-promotion
    "coupon_commercial_partner_applicability": "loyalty_partner_applicability",
    "sale_coupon_selection_wizard": "sale_loyalty_order_suggestion",
    # OCA/sale-workflow
    "sale_product_set_layout": "sale_product_set",
    # OCA/social
    "mail_preview_audio": "mail",
    "mail_preview_base": "mail",
    # OCA/stock-logistics-workflow
    "stock_picking_backorder_strategy": "stock",
    # OCA/web
    "web_drop_target": "web",
    "web_ir_actions_act_view_reload": "web",
    # Viindoo/tvtmaaddons
    "payment_zalo_atm": "payment_zalopay",
    "payment_zalo_international_card": "payment_zalopay",
    "payment_zalopay_merchant_code": "payment_zalopay",
    "to_hr_contract_actions": "viin_hr_contract",
    "to_http_reroute_encoding": "http_routing",
    "to_partner_check_unique_vat": "viin_partner_tax_code",
    "to_project_stages": "viin_project",
    "to_sale_purchase_multi_comp": "sale_purchase",
    "to_tax_is_vat": "viin_account",
    "viin_account_balance_carry_forward_advanced": "viin_account_auto_transfer",
    "viin_google_drive_support_oauth2": "viin_google_drive",
    "viin_hr_holidays_accrual_plan": "viin_hr_holidays",
    "viin_hr_employee_resource_calendar": "viin_hr_contract",
    "viin_mrp_packaging": "viin_mrp",
    "viin_project_access_advance": "viin_project",
    "viin_project_kanban_state_notification": "viin_project",
    "viin_project_update": "viin_project",
    "viin_project_update_pad": "project",
    "viin_reverse_move_line": "viin_account",
    "viin_website_image_optimization_disable": "viin_web_editor",
    "viin_hr_timesheet_approval_patch1": "to_hr_timesheet_approval",
    "viin_hr_holidays_patch1": "viin_hr_holidays",
    "viin_social_facebook_page_setting": "viin_social_facebook",
    "viin_social_facebook_page_setting_patch1": "viin_social_facebook",
    # Viindoo/enterprise
    "to_account_asset_patch1": "to_account_asset",
    "to_mrp_account_patch1": "viin_mrp_account",
    "viin_hide_ent_modules_account": "to_hide_ent_modules",
    "viin_hide_ent_modules_crm": "to_hide_ent_modules",
    "viin_hide_ent_modules_event": "to_hide_ent_modules",
    "viin_hide_ent_modules_expense": "to_hide_ent_modules",
    "viin_hide_ent_modules_hr_timesheet": "to_hide_ent_modules",
    "viin_hide_ent_modules_iap": "to_hide_ent_modules",
    "viin_hide_ent_modules_inter_company": "to_hide_ent_modules",
    "viin_hide_ent_modules_mrp": "to_hide_ent_modules",
    "viin_hide_ent_modules_point_of_sale": "to_hide_ent_modules",
    "viin_hide_ent_modules_project": "to_hide_ent_modules",
    "viin_hide_ent_modules_purchase": "to_hide_ent_modules",
    "viin_hide_ent_modules_sale": "to_hide_ent_modules",
    "viin_hide_ent_modules_sale_timesheet": "to_hide_ent_modules",
    "viin_hide_ent_modules_stock": "to_hide_ent_modules",
    "viin_hide_ent_modules_website": "to_hide_ent_modules",
    "viin_mobile_firebase": "viin_mobile",
    "to_quality_patch1": "to_quality",
    "viin_quality_product": "to_quality",
    "viin_quality_template": "to_quality",
    "viin_quality_template_patch1": "to_quality",
    "viin_quality_template_stock": "to_quality_stock",
    "viin_web_dashboard": "spreadsheet_dashboard",
    "viin_website_seo_advisor_patch1": "viin_website_seo_advisor",
    "viin_website_patch1": "viin_website",
    "viin_website_helpdesk_patch1": "viin_website_helpdesk",
    "viin_mrp_account_carry_forward": "viin_account_auto_transfer",
    "viin_mrp_gantt": "viin_mrp",
    "viin_mrp_split_merge": "mrp",  # Feature available in odoo v16.0
    "viin_mrp_standard_consumption": "viin_mrp",
    # Viindoo/saas-infrastructure
    "viin_odoo_module_sale_subscription": "viin_odoo_module_subscription",
    "viin_saas_sale_subscription_free_product": "viin_saas_sale_subscription_loyalty",
    # Viindoo/odoo-tvtma
    "viin_saas_membership": "viin_saas_reseller",
    "viin_saas_reseller_portal": "viin_saas_reseller",
    "viin_viindoo_membership_white_label": "viin_viindoo_saas_reseller",
    "viin_website_product_add_to_cart_snippet": "website_sale",
    # Viindoo/branding
    "viin_brand_web": "viin_brand_common",
    "viin_brand_web_editor": "web_editor",
    "viin_brand_website_blog": "website_blog",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "account.analytic.group": "account.analytic.plan",
    "account.tax.carryover.line": "account.report.external.value",
    "account.tax.report": "account.report",
    "account.tax.report.line": "account.report.line",
    "coupon.coupon": "loyalty.card",
    "coupon.program": "loyalty.program",
    "coupon.reward": "loyalty.reward",
    "coupon.rule": "loyalty.rule",
    "mail.channel.partner": "mail.channel.member",
    "payment.acquirer": "payment.provider",
    "payment.acquirer.onboarding.wizard ": "payment.provider.onboarding.wizard",
    "sale.coupon.apply.code": "sale.loyalty.coupon.wizard",
    "sale.payment.acquirer.onboarding.wizard": "sale.payment.provider.onboarding.wizard",
    "stock.location.route": "stock.route",
    "stock.production.lot": "stock.lot",
    # OCA/...
    # Viindoo/tvtmaaddons
    "approval.request": "viin.approval.request",
    "helpdesk.sla": "viin.helpdesk.sla",
    "helpdesk.stage": "viin.helpdesk.stage",
    "helpdesk.tag": "viin.helpdesk.tag",
    "helpdesk.team": "viin.helpdesk.team",
    "helpdesk.ticket": "viin.helpdesk.ticket",
    "helpdesk.ticket.type": "viin.helpdesk.ticket.type",
    # Viindoo/enterprise
    # Viindoo/odoo-tvtma
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "gift.card": "loyalty.card",
    # OCA/...
    # Viindoo/tvtmaaddons
    # Viindoo/enterprise
    # Viindoo/odoo-tvtma
}
