# -*- coding: utf-8 -*-
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'product_template': [
        ('type', None, None),
    ],
}


def migrate_digital_products(cr):
    """9.0 has a product type 'digital' ("Digital Content"): what is attached
    to such a product can be downloaded by the customers who paid for it.
    10.0 has no such type. A digital product is a service, and the files to
    download are the attachments of the product flagged product_downloadable.

    - the attachments of the digital products (not the ones that store a
      field of the product, like its image) are flagged;
    - the digital products become services. The 9.0 type is kept in the
      legacy column.
    """
    if not openupgrade.column_exists(
            cr, 'ir_attachment', 'product_downloadable'):
        cr.execute(
            "ALTER TABLE ir_attachment ADD COLUMN product_downloadable bool")
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_attachment a
        SET product_downloadable = TRUE
        WHERE a.res_field IS NULL AND (
            (a.res_model = 'product.template' AND a.res_id IN (
                SELECT id FROM product_template WHERE type = 'digital'))
            OR (a.res_model = 'product.product' AND a.res_id IN (
                SELECT pp.id FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE pt.type = 'digital')))
        """)
    openupgrade.logged_query(
        cr,
        "UPDATE product_template SET type = 'service' WHERE type = 'digital'")


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, _column_copies)
    migrate_digital_products(cr)
