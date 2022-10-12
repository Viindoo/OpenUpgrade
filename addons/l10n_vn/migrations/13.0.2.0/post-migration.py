from openupgradelib import openupgrade


def assign_account_tags_to_repartition_lines(env):
    company_ids = env['res.company'].search([]).ids
    map_data = []
    for company_id in company_ids:
        map_xml_id_data = [
            ('tax_purchase_vat10','l10n_vn.account_tax_report_line_03_02_01_vn','l10n_vn.account_tax_report_line_03_01_01_vn'),
            ('tax_purchase_vat5','l10n_vn.account_tax_report_line_02_02_01_vn','l10n_vn.account_tax_report_line_02_01_01_vn'),
            ('tax_purchase_vat0','l10n_vn.account_tax_report_line_01_02_01_vn'),
            ('tax_sale_vat10','l10n_vn.account_tax_report_line_03_02_02_vn','l10n_vn.account_tax_report_line_03_01_02_vn'),
            ('tax_sale_vat5','l10n_vn.account_tax_report_line_02_02_02_vn','l10n_vn.account_tax_report_line_02_01_02_vn'),
            ('tax_sale_vat0','l10n_vn.account_tax_report_line_01_02_02_vn'),
                           ]
        for data in map_xml_id_data:
            tax = env.ref('l10n_vn.' + str(company_id) + '_' + data[0])
            invoice_repartition_lines = tax.invoice_repartition_line_ids
            refund_repartition_lines = tax.refund_repartition_line_ids
            base_report_line_data = env.ref(data[1])
            tax_report_line_data = len(data) > 2 and env.ref(data[2]) or False
            
            for line in invoice_repartition_lines.filtered_domain([('repartition_type', '=', 'base')]):
                map_data.extend([(line.id, tag.id) for tag in base_report_line_data.tag_ids.filtered_domain([('tax_negate', '=', False)])])
            for line in refund_repartition_lines.filtered_domain([('repartition_type', '=', 'base')]):
                map_data.extend([(line.id, tag.id) for tag in base_report_line_data.tag_ids.filtered_domain([('tax_negate', '=', True)])])
            
            if tax_report_line_data:
                for line in invoice_repartition_lines.filtered_domain([('repartition_type', '=', 'tax')]):
                    map_data.extend([(line.id, tag.id) for tag in tax_report_line_data.tag_ids.filtered_domain([('tax_negate', '=', False)])])
                for line in refund_repartition_lines.filtered_domain([('repartition_type', '=', 'tax')]):
                    map_data.extend([(line.id, tag.id) for tag in tax_report_line_data.tag_ids.filtered_domain([('tax_negate', '=', True)])])

    sql_query = ""
    sub_query = """
    INSERT INTO account_account_tag_account_tax_repartition_line_rel (
        account_tax_repartition_line_id,account_account_tag_id)
    VALUES %s;
    """
    for data in map_data:
        sql_query += sub_query

    openupgrade.logged_query(
        env.cr, sql_query, tuple(data for data in map_data)
    )


def assign_account_tags_to_move_lines(env):
    # move lines with tax repartition lines
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_tax_repartition_line atrl ON aml.tax_repartition_line_id = atrl.id
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        ON CONFLICT DO NOTHING"""
    )
    # move lines with taxes
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        JOIN account_move_line_account_tax_rel amlatr ON amlatr.account_move_line_id = aml.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.invoice_tax_id = amlatr.account_tax_id AND atrl.repartition_type = 'base')
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        WHERE aml.old_invoice_line_id IS NOT NULL AND am.type in ('out_invoice', 'in_invoice')
        ON CONFLICT DO NOTHING"""
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_account_tag_account_move_line_rel (
            account_move_line_id, account_account_tag_id)
        SELECT aml.id, aat_atr_rel.account_account_tag_id
        FROM account_move_line aml
        JOIN account_move am ON aml.move_id = am.id
        JOIN account_move_line_account_tax_rel amlatr ON amlatr.account_move_line_id = aml.id
        JOIN account_tax_repartition_line atrl ON (
            atrl.refund_tax_id = amlatr.account_tax_id AND atrl.repartition_type = 'base')
        JOIN account_account_tag_account_tax_repartition_line_rel aat_atr_rel ON
            aat_atr_rel.account_tax_repartition_line_id = atrl.id
        WHERE aml.old_invoice_line_id IS NOT NULL AND am.type in ('out_refund', 'in_refund')
        ON CONFLICT DO NOTHING"""
    )


@openupgrade.migrate()
def migrate(env, version):
    assign_account_tags_to_repartition_lines(env)
    assign_account_tags_to_move_lines(env)
