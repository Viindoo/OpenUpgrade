# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'sale_order_line': [
        ('qty_delivered', 'qty_delivered_manual', None),
    ],
}

_column_renames = {
    'payment_transaction': [
        ('sale_order_id', None),
    ],
    'sale_order': [
        ('payment_tx_id', None),
    ],
}

_column_renames2 = {
    'sale_order': [
        ('require_payment', None),
    ],
}

_field_renames_order_dates = [
    ('sale.order', 'sale_order', 'commitment_date',
     openupgrade.get_legacy_name('commitment_date')),
    ('sale.order', 'sale_order', 'requested_date', 'commitment_date'),
]


_config_param_renames = [
    ('sale_payment.automatic_invoice', 'sale.automatic_invoice'),
    ('sale_payment.default_email_template', 'sale.default_email_template'),
]


def rename_sale_payment_config_parameters(cr, keys_spec):
    for (old, new) in keys_spec:
        query = ("UPDATE ir_config_parameter SET key = %s "
                 "WHERE key = %s")
        openupgrade.logged_query(cr, query, (new, old))


def fill_sale_order_line_sections(cr):
    """It's done here instead of post-migration to avoid
    possible new rows added in the migration"""
    cr.execute(
        "ALTER TABLE sale_order_line ADD COLUMN display_type varchar",
    )
    # First sort sales order line by layout category and sequence
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET sequence = sub.rank * 5
        FROM (
            SELECT id, rank()
            OVER (
                PARTITION BY order_id ORDER BY layout_category_id, sequence, id
            ) FROM sale_order_line
        ) sub
        WHERE sol.id = sub.id
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_line ALTER COLUMN product_id DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_line ALTER COLUMN product_uom DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        INSERT INTO sale_order_line (order_id, layout_category_id,
            sequence, name,
            price_unit, product_uom_qty, customer_lead,
            display_type, create_uid, create_date, write_uid, write_date,
            company_id, order_partner_id, salesman_id, currency_id, state)
        SELECT sol.order_id, sol.layout_category_id,
            min(sol.sequence) -1 as sequence, max(COALESCE(slc.name, ' ')),
            0, 0, 0, 'line_section', min(sol.create_uid), min(sol.create_date),
            min(sol.write_uid), min(sol.write_date),
            -- the stored related fields of the order the lines share: the
            -- record rules read company_id (without it the sections were
            -- hidden, also from the order they head)
            min(sol.company_id), min(sol.order_partner_id),
            min(sol.salesman_id), min(sol.currency_id), min(sol.state)
        FROM sale_order_line sol
        LEFT JOIN sale_layout_category slc ON slc.id = sol.layout_category_id
        WHERE sol.order_id IN (
            SELECT order_id
            FROM sale_order_line
            WHERE layout_category_id IS NOT NULL)
        GROUP BY sol.order_id, sol.layout_category_id
        ORDER BY sol.order_id, sol.layout_category_id, sequence
        """
    )


@openupgrade.migrate()
def migrate(env, version):

    # if website_quote is installed in v11, the column require_payment should exists
    # in this case, we need to make a backup for the column so that we will not lose
    # the data since this column is now a boolean field in sale module instead of
    # website_quote as it was in Odoo 11 in post-migration, we will use this backup
    # field to fill the value for the new field require_payment and require_signature
    if openupgrade.column_exists(env.cr, 'sale_order', 'require_payment'):
        _column_copies['sale_order'] = [
            ('require_payment', None, None),
        ]
    openupgrade.copy_columns(env.cr, _column_copies)

    if openupgrade.column_exists(env.cr, 'sale_order', 'payment_tx_id'):
        # from sale_payment module
        openupgrade.rename_columns(env.cr, _column_renames)
        rename_sale_payment_config_parameters(env.cr, _config_param_renames)
        openupgrade.lift_constraints(env.cr, "sale_order", "payment_tx_id")
        openupgrade.lift_constraints(env.cr, "sale_order ", "payment_acquirer_id")
        openupgrade.lift_constraints(env.cr, "payment_transaction ", "sale_order_id")
    if openupgrade.column_exists(env.cr, 'sale_order', 'requested_date'):
        # from sale_order_dates module
        openupgrade.rename_fields(env, _field_renames_order_dates)
    if (openupgrade.table_exists(env.cr, 'sale_quote_line')
            and openupgrade.column_exists(
                env.cr, 'sale_order', 'require_payment')):
        # from website_quote module (its tables stay when it is uninstalled,
        # the column of sale.order goes)
        openupgrade.rename_columns(env.cr, _column_renames2)
    fill_sale_order_line_sections(env.cr)
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE sale_order_line ADD COLUMN qty_delivered_method varchar",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE sale_order_line ADD COLUMN untaxed_amount_invoiced "
        "NUMERIC")
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE sale_order_line ADD COLUMN untaxed_amount_to_invoice "
        "NUMERIC")
