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
    # OCA/...
    # Viindoo/tvtmaaddons
    "to_hr_employee_birthday_filters": "viin_hr_employee_birthday",
    "to_equipment_hierarchy": "viin_maintenance",
    "viin_hr_equipment_hierarchy": "viin_hr_maintenance",
    "to_slugify_l10n_vn": "viin_unicode_slugify",
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
    # Viindoo/tvtmaaddons
    "to_partner_business_type": "viin_partner_business_nature",
    "to_partner_employee_size": "viin_partner_business_nature",
    "to_partner_ownership_type": "viin_partner_business_nature",
    "viin_crm_business_type": "viin_crm_business_nature",
    "viin_crm_employee_size": "viin_crm_business_nature",
    "to_hr_public_employee_birthday_filters": "viin_hr_employee_birthday",
    "to_equipment_image": "viin_maintenance",
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
