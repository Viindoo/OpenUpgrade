# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def move_checkout_street(cr):
    """The 9.0 checkout keeps the street of an address in street2 (its input
    'street' is the optional company name); the 10.0 checkout requires street.
    A customer whose address has street2 only must type the street again at
    the next order ("some required fields are empty"): move street2 to street
    when street is empty."""
    openupgrade.logged_query(
        cr, """
        UPDATE res_partner SET street = street2, street2 = NULL
        WHERE COALESCE(street, '') = '' AND COALESCE(street2, '') != ''
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    move_checkout_street(cr)
    pl_model = env['product.pricelist']
    sql = """
    UPDATE product_pricelist pp
    SET website_id = wp.website_id,
        selectable = wp.selectable
        FROM website_pricelist_openupgrade_10 wp
        WHERE wp.pricelist_id = pp.id
    """
    openupgrade.logged_query(cr, sql)
    # all remaining pricelists will be assigned to default
    sql = """select pricelist_id from
          website_pricelist_openupgrade_10"""
    cr.execute(sql)
    pricelist_ids = cr.fetchall()
    for pricelist in pl_model.search([('id', 'not in', pricelist_ids)]):
        pricelist.write({'website_id': pricelist._default_website().id})
    openupgrade.load_data(
        cr, 'website_sale', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
