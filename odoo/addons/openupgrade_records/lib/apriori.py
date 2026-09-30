""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'crm_reveal': 'crm_iap_lead',
    'document': 'attachment_indexation',
    'payment_ogone': 'payment_ingenico',
    # OCA/delivery-carrier
    'delivery_carrier_label_ups': 'delivery_ups_oca',
    # OCA/edi
    'edi_oca': 'edi',
    # OCA/event
    'website_event_filter_selector': 'website_event_filter_city',
    # OCA/hr
    # TODO: Transform possible data
    'hr_skill': 'hr_skills',
    # OCA/iot
    'iot': 'iot_oca',
    'iot_amqp': 'iot_amqp_oca',
    'iot_input': 'iot_input_oca',
    'iot_output': 'iot_output_oca',
    # OCA/manufacture
    'quality_control': 'quality_control_oca',
    'quality_control_mrp': 'quality_control_mrp_oca',
    'quality_control_stock': 'quality_control_stock_oca',
    'quality_control_team': 'quality_control_team_oca',
    # OCA/margin-analysis
    'product_pricelist_margin': 'product_pricelist_simulation',
    # OCA/pos
    'pos_journal_image': 'pos_payment_method_image',
    # OCA/product-attribute
    'product_pricelist_print_website_sale': 'product_pricelist_direct_print_website_sale',
    'sale_product_classification': 'product_abc_classification_sale',
    # OCA/stock-logistics-warehouse
    'stock_putaway_product_form': 'stock_putaway_product_template',
    # Viindoo/tvtmaaddons
    'hr_payroll': 'to_hr_payroll',
    'hr_payroll_account': 'to_hr_payroll_account',
    'to_hr_overtime_payroll': 'viin_hr_overtime_payroll',
    'to_stock_picking_validate_manual_time': 'to_stock_picking_backdate',
    # Viindoo/odoo-web_gantt
    'project_gantt': 'viin_project_gantt',
    # Viindoo/odoo-tvtma
    # the mega menu itself is in the website module of Odoo now; what is left of
    # the module (icon_class, text_hide) became to_website_menu_icon
    'to_website_mega_menu': 'to_website_menu_icon',
    'to_website_mega_menu_erponline_data': 'to_website_menu_icon_erponline_data',
    # OCA/l10n-netherlands -> OCA/account-financial-reporting
    'l10n_nl_mis_reports': 'mis_template_financial_report',
}

merged_modules = {
    # Odoo
    'account_cancel': 'account',
    'account_voucher': 'account',
    'crm_phone_validation': 'crm',
    'decimal_precision': 'base',
    'delivery_hs_code': 'delivery',
    'hw_scale': 'hw_drivers',
    'hw_scanner': 'hw_drivers',
    'hw_screen': 'hw_drivers',
    'l10n_fr_certification': 'account',
    'l10n_fr_sale_closing': 'l10n_fr',
    'mrp_bom_cost': 'mrp_account',
    'mrp_byproduct': 'mrp',
    'payment_stripe_sca': 'payment_stripe',
    'stock_zebra': 'stock',
    'survey_crm': 'survey',
    'test_pylint': 'test_lint',
    'web_settings_dashboard': 'base_setup',
    'website_crm_phone_validation': 'website_crm',
    'website_sale_link_tracker': 'website_sale',
    'website_survey': 'survey',
    # Odoo: removed without a successor on our addons paths. Merging them into the
    # module they extended lets the update remove their views, fields and access
    # rights (website_hr gave public users access to employees); columns are kept.
    # OCA/crm has crm_project for 13.0: add that repository and drop this line to
    # keep the wizard that converts a lead into a task.
    'crm_project': 'crm',
    'website_hr': 'hr',
    # OCA/account-analytic
    'account_analytic_default_account': 'account_analytic_default',
    # OCA/account-financial-tools
    'account_coa_menu': 'account_menu',
    'account_group_menu': 'account_menu',
    'account_move_chatter': 'account',
    'account_tag_menu': 'account_menu',
    'account_type_menu': 'account_menu',
    # OCA/account-invoicing
    'account_invoice_repair_link': 'repair',
    # OCA/account-reconcile
    'account_set_reconcilable': 'account',
    'bank_statement_foreign_currency': 'account',
    'account_reconciliation_widget_partial': 'account',
    # OCA/e-commerce
    'website_sale_category_description': 'website_sale',
    # OCA/event
    'event_activity': 'event',
    'website_event_share': 'website_event',
    # OCA/geospatial
    'base_geolocalize_openstreetmap': 'base_geolocalize',
    # OCA/l10n-spain
    'l10n_es_account_invoice_sequence': 'l10n_es',
    'l10n_es_aeat_mod303_extra_data': 'l10n_es_aeat_mod303',
    'l10n_es_aeat_sii': 'l10n_es_aeat_sii_oca',
    'l10n_es_aeat_sii_extra_data': 'l10n_es_aeat_sii_oca',
    'l10n_es_extra_data': 'l10n_es',
    'l10n_es_ticketbai_batuz_extra_data': 'l10n_es_ticketbai_batuz',
    'l10n_es_ticketbai_extra_data': 'l10n_es_ticketbai',
    'l10n_es_vat_book_extra_data': 'l10n_es_vat_book',
    # OCA/manufacture
    'repair_calendar_view': 'base_repair',
    # OCA/multi-company
    'stock_production_lot_multi_company': 'stock',
    # OCA/partner-contact
    'base_vat_sanitized': 'base_vat',
    'partner_group': 'partner_company_group',
    # OCA/product-attribute
    'product_pricelist_show_product_ref': 'product',
    'product_active_propagate': 'product',
    # OCA/product-variant
    'sale_order_variant_mgmt': 'sale_product_matrix',
    # OCA/purchase-reporting
    'purchase_report_extension': 'purchase',
    # OCA/sale-workflow
    'sale_disable_inventory_check': 'sale_stock',
    # OCA/server-backend
    'base_suspend_security': 'base',
    # OCA/social
    'mail_history': 'mail',
    'mass_mailing_unique': 'mass_mailing',
    # OCA/stock-logistics-reporting
    'stock_forecast_report': 'stock',
    'stock_picking_report_custom_description': 'stock',
    # OCA/stock-logistics-warehouse
    'sale_stock_info_popup': 'sale_stock',
    # OCA/stock-logistics-workflow
    'stock_picking_responsible': 'stock',
    # OCA/timesheet
    'sale_timesheet_existing_project': 'sale_timesheet',
    # OCA/web
    'web_export_view': 'web',
    'web_favicon': 'base',
    'web_tree_resize_column': 'web',
    'web_view_searchpanel': 'web',
    'web_widget_color': 'web',
    'web_widget_float_formula': 'web',
    'web_widget_many2many_tags_multi_selection': 'web',
    'web_widget_one2many_product_picker_sale_stock_available_info_popup': (
        'web_widget_one2many_product_picker_sale_stock'
    ),
    # OCA/website
    'website_adv_image_optimization': 'website',
    'website_canonical_url': 'website',
    'website_form_builder': 'website_form',
    'website_logo': 'website',
    'website_megamenu': 'website',
    'website_snippet_anchor': 'website',
    'website_anchor_smooth_scroll': 'website',
    # muk-it/muk_base - Agreed to move to OCA
    'muk_attachment_lobject': 'dms',
    'muk_security': 'dms',
    'muk_autovacuum': 'dms',
    'muk_utils': 'dms',
    # muk-it/muk_web - Agreed to move to OCA
    'muk_web_preview': 'mail_preview_base',
    'muk_web_preview_audio': 'mail_preview_audio',
    'muk_web_preview_image': 'mail_preview_base',
    'muk_web_preview_video': 'mail_preview_base',
    'muk_web_searchpanel': 'web',
    'muk_web_utils': 'dms',
    # muk-it/muk_dms - Agreed to move to OCA
    'muk_dms': 'dms',
    'muk_dms_access': 'dms',
    'muk_dms_actions': 'dms',
    'muk_dms_attachment': 'dms',
    'muk_dms_field': 'dms',
    'muk_dms_file': 'dms',
    'muk_dms_lobject': 'dms',
    'muk_dms_mail': 'dms',
    'muk_dms_thumbnails': 'dms',
    'muk_dms_view': 'dms',
    # Viindoo/erponline-enterprise
    'to_enterprise_marks_hr_payroll': 'to_hr_payroll',
    # Viindoo/odoo-joomla2odoo
    'to_website_content_language': 'to_website_language_page',
    'to_website_content_language_blog': 'to_website_language_blog',
    # Viindoo/odoo-tvtma
    'to_odoo_saas_erponline': 'to_odoo_saas_sale',
    'to_refresh_sale_order': 'sale',
    'to_tvtma_project': 'project',
    'to_website_erponline': 'to_website_erponline_data',
    'to_website_language_forum_erponline_data': 'to_website_erponline_data',
    'to_website_language_page_erponline_data': 'to_website_erponline_data',
    'to_website_logo': 'website',
    # Viindoo/saas-infrastructure
    'to_response': 'to_saas_base',
    # Viindoo/tvtmaaddons
    'to_equipment_archive': 'maintenance',
    'to_hr_advanced': 'to_hr_payroll',
    'to_hr_payroll_account_advanced': 'to_hr_payroll_account',
    'to_hr_payroll_contribution': 'to_hr_payroll',
    'to_hr_payroll_leave_type_code': 'to_hr_payroll',
    'to_l10n_vn_hr_insurance': 'to_l10n_vn_hr_payroll',
    'to_l10n_vn_hr_insurance_account': 'to_l10n_vn_hr_payroll_account',
    'to_account_journal_entry_chatter': 'account',
    'to_hr_scheduled_working_days': 'to_hr_payroll',
    'to_hr_subordinates': 'hr_org_chart',
    'to_invoice_partner_vat': 'account',
    'to_l10n_vn_account_financial_income': 'to_account_financial_income',
    'to_l10n_vn_account_income_deduct': 'to_account_income_deduct',
    'to_mail_archive': 'mail',
}

# only used here for openupgrade_records analysis:
renamed_models = {
    # Odoo
    'account.register.payments': 'account.payment.register',
    'crm.reveal.industry': 'crm.iap.lead.industry',
    'crm.reveal.role': 'crm.iap.lead.role',
    'crm.reveal.seniority': 'crm.iap.lead.seniority',
    'mail.blacklist.mixin': 'mail.thread.blacklist',
    'mail.mail.statistics': 'mailing.trace',
    'mail.statistics.report': 'mailing.trace.report',
    'mail.mass_mailing': 'mailing.mailing',
    'mail.mass_mailing.contact': 'mailing.contact',
    'mail.mass_mailing.list': 'mailing.list',
    'mail.mass_mailing.list_contact_rel': 'mailing.contact.subscription',
    'mail.mass_mailing.stage': 'utm.stage',
    'mail.mass_mailing.tag': 'utm.tag',
    'mail.mass_mailing.test': 'mailing.mailing.test',
    'mass.mailing.list.merge': 'mailing.list.merge',
    'mass.mailing.schedule.date': 'mailing.mailing.schedule.date',
    'mrp.subproduct': 'mrp.bom.byproduct',
    'sms.send_sms': 'sms.composer',
    'stock.fixed.putaway.strat': 'stock.putaway.rule',
    'report.stock.forecast': 'report.stock.quantity',
    'survey.mail.compose.message': 'survey.invite',
    'website.redirect': 'website.rewrite',
    # OCA/...
}

# only used here for openupgrade_records analysis:
merged_models = {
    # Odoo
    'account.invoice': 'account.move',
    'account.invoice.line': 'account.move.line',
    'account.invoice.tax': 'account.move.line',
    'account.voucher': 'account.move',
    'account.voucher.line': 'account.move.line',
    'lunch.order.line': 'lunch.order',
    'mail.mass_mailing.campaign': 'utm.campaign',
    'slide.category': 'slide.slide',
    'survey.page': 'survey.question',
    # OCA/...
}

# Modules of merged_modules that are not merged into anything: they are
# removed without a successor on our addons paths. The technical records they
# own (record rules, scheduled and server actions, views, menus, mail
# templates...) are deleted by the update even when they are noupdate, and the
# xml ids of records of models that go with them are detached: see
# release_records_of_lost_modules in the pre-migration of base.
lost_modules = [
    'crm_project',
    'website_hr',
]

# Records of a module that 13.0 moves to another module, the new one being
# installed by the migration (its own scripts do not run): their xml ids are
# moved before it loads its data, or it creates them a second time (unique
# constraints fail, e.g. the overtime rule codes).
# {(module of 12.0 after the renames above, module of 13.0): [xml id names]}
moved_xmlids = {
    # Viindoo/tvtmaaddons: overtime rules, codes and reasons moved from
    # to_hr_overtime_payroll (renamed viin_hr_overtime_payroll) to the new
    # viin_hr_overtime
    ("viin_hr_overtime_payroll", "viin_hr_overtime"): [
        'access_hr_overtime_reason_employee',
        'access_hr_overtime_rule_code_employee',
        'access_hr_overtime_rule_employee',
        'action_hr_overtime_reason',
        'action_hr_overtime_rule_codes',
        'action_hr_overtime_rules',
        'hr_overtime_config_menu',
        'hr_overtime_reason_form_view',
        'hr_overtime_reason_menu',
        'hr_overtime_reason_tree_view',
        'hr_overtime_rule_code_menu',
        'hr_overtime_rule_code_tree_view',
        'hr_overtime_rule_form_view',
        'hr_overtime_rule_menu',
        'hr_overtime_rule_tree_view',
        'menu_hr_overtime_report_main',
        'rule_code_ot0006',
        'rule_code_ot0618',
        'rule_code_ot1822',
        'rule_code_ot2224',
        'rule_code_othol0006',
        'rule_code_othol0618',
        'rule_code_othol1822',
        'rule_code_othol2224',
        'rule_code_otholsat0006',
        'rule_code_otholsat0612',
        'rule_code_otholsat1218',
        'rule_code_otholsat1822',
        'rule_code_otholsat2224',
        'rule_code_otholsun0006',
        'rule_code_otholsun1822',
        'rule_code_otholsun2224',
        'rule_code_otsat0006',
        'rule_code_otsat0612',
        'rule_code_otsat1218',
        'rule_code_otsat1822',
        'rule_code_otsat2224',
        'rule_code_otsun0006',
        'rule_code_otsun1822',
        'rule_code_otsun2224',
        'view_employee_form',
    ],
}
