# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _jsonb_translated_columns(cr, model, table):
    cr.execute(
        """
        SELECT isc.column_name
        FROM information_schema.columns isc
        JOIN ir_model_fields imf ON imf.name = isc.column_name AND imf.model = %s
        WHERE isc.table_name = %s AND imf.translate AND isc.data_type = 'jsonb'
        """,
        (model, table),
    )
    return [name for (name,) in cr.fetchall()]


def delete_record_translations(cr, module, xml_ids, field_list=None):
    """Only touch the translated columns that are jsonb already.

    openupgradelib picks every field flagged translate in ir_model_fields and
    applies the jsonb operator ? to its column. The translated columns of a
    module that has not been loaded yet are still text at that point (e.g. the
    website SEO fields of ir.ui.view while digest migrates), and the query dies
    on "operator does not exist: text ? unknown". Those columns get their
    translations converted when their own module loads.
    """
    if not isinstance(xml_ids, (list, tuple)) or not xml_ids:
        return delete_record_translations._original_method(
            cr, module, xml_ids, field_list=field_list
        )
    cr.execute(
        """SELECT model, array_agg(name) FROM ir_model_data
        WHERE module = %s AND name IN %s GROUP BY model""",
        (module, tuple(xml_ids)),
    )
    for model, names in cr.fetchall():
        table = openupgrade.get_model2table(model)
        if not openupgrade.table_exists(cr, table):
            continue
        columns = _jsonb_translated_columns(cr, model, table)
        if field_list:
            columns = [c for c in columns if c in field_list]
        if not columns:
            continue
        delete_record_translations._original_method(
            cr, module, names, field_list=columns
        )


if openupgrade.version_info[0] >= 16:
    delete_record_translations._original_method = (
        openupgrade.delete_record_translations
    )
    openupgrade.delete_record_translations = delete_record_translations
