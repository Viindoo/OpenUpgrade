# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def move_fields_from_invoice_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET purchase_line_id = ail.purchase_line_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.purchase_line_id IS NOT NULL"""
    )


def change_type_purchase_order_date_approve(env):
    # An order can have several messages of the subtype (approved again, state tracked again later): a plain
    # UPDATE ... FROM takes any of them, not the same from one run to the other, sometimes of another day than the
    # date of the former version. Take the last message of the day of that date (the date was today in the time zone
    # of the user who approved, the author of the message), else the last message.
    query = """
        UPDATE purchase_order po
        SET date_approve = mm.date
        FROM (
            SELECT DISTINCT ON (mm.res_id) mm.res_id, mm.date
            FROM mail_message mm
            JOIN purchase_order p ON p.id = mm.res_id
            LEFT JOIN res_partner rp ON rp.id = mm.author_id
            LEFT JOIN pg_timezone_names tz ON tz.name = rp.tz
            WHERE mm.subtype_id = %s
                AND mm.model = 'purchase.order'
            ORDER BY mm.res_id,
                ((mm.date AT TIME ZONE 'UTC' AT TIME ZONE COALESCE(tz.name, 'UTC'))::date
                 IS NOT DISTINCT FROM p.{legacy}) DESC,
                mm.date DESC, mm.id DESC
        ) mm
        WHERE mm.res_id = po.id
            AND po.date_approve IS NULL""".format(
        legacy=openupgrade.get_legacy_name("date_approve"))
    openupgrade.logged_query(env.cr, query, (env.ref('purchase.mt_rfq_approved').id,))
    openupgrade.logged_query(env.cr, query, (env.ref('purchase.mt_rfq_confirmed').id,))


def fill_account_move_purchase_order_rel_table(env):
    # Remove temp table and re-create m2m table through ORM method
    openupgrade.logged_query(env.cr, "DROP TABLE account_move_purchase_order_rel")
    Move = env["purchase.order"]
    Move._fields["invoice_ids"].update_db(Move, False)
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_purchase_order_rel (
            purchase_order_id, account_move_id)
        SELECT rel.purchase_order_id, am.id
        FROM account_invoice_purchase_order_rel rel
        JOIN account_move am ON am.old_invoice_id = rel.account_invoice_id
        ON CONFLICT DO NOTHING"""
    )


def fill_purchase_order_line_qty_received_method(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order_line pol
        SET qty_received_method = 'manual'
        FROM product_product pp
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pol.product_id = pp.id
            AND pt.type IN ('consu', 'service')"""
    )


@openupgrade.migrate()
def migrate(env, version):
    move_fields_from_invoice_to_moves(env)
    change_type_purchase_order_date_approve(env)
    fill_account_move_purchase_order_rel_table(env)
    fill_purchase_order_line_qty_received_method(env.cr)
    openupgrade.load_data(
        env.cr, "purchase", "migrations/13.0.1.2/noupdate_changes.xml")
