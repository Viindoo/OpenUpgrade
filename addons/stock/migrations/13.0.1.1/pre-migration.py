# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'stock_location': [
        ('usage', None, None),
    ],
}

_model_renames = [
    ('report.stock.forecast', 'report.stock.quantity'),
    ('stock.fixed.putaway.strat', 'stock.putaway.rule'),
]

_table_renames = [
    ('stock_fixed_putaway_strat', 'stock_putaway_rule'),
]

_field_renames = [
    ('stock.putaway.rule', 'stock_putaway_rule', 'fixed_location_id', 'location_out_id'),
    ('stock.move', 'stock_move', 'propagate', 'propagate_cancel'),
    ('stock.rule', 'stock_rule', 'propagate', 'propagate_cancel'),
    ('stock.scrap', 'stock_scrap', 'date_expected', 'date_done'),
]

_column_renames = {
    'stock_inventory': [
        ('category_id', None),
        ('filter', None),
        ('location_id', None),
        ('lot_id', None),
        ('package_id', None),
        ('partner_id', None),
        ('product_id', None),
    ],
}

_xmlid_renames = [
    # mail.template
    ('delivery.mail_template_data_delivery_confirmation', 'stock.mail_template_data_delivery_confirmation'),
    # ir.model.access
    ('stock.access_stock_fixed_putaway_strat', 'stock.access_stock_putaway_manager'),
    ('stock.access_stock_fixed_putaway_user', 'stock.access_stock_putaway_all'),
    ('stock.access_stock_forecast_user', 'stock.access_report_stock_quantity'),
    # from stock_production_lot_multi_company module
    ('stock.production_lot_comp_rule', 'stock.stock_production_lot_rule'),
]


def assure_stock_rule_company_is_correct(env):
    # avoid company_id check error during update
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_rule sr
        SET company_id = sw.company_id
        FROM stock_warehouse sw
        WHERE sr.warehouse_id = sw.id AND
         (sw.company_id != sr.company_id or sr.company_id IS NULL)"""
    )


def fill_inventory_line_categ(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_inventory_line ADD categ_id int4",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_inventory_line sil
        SET categ_id = pt.categ_id
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE pp.id = sil.product_id"""
    )


def prefill_stock_picking_type_sequence_code(env):
    """Prefill this field for avoiding the not null warning during update."""
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_picking_type ADD sequence_code VARCHAR"
    )
    openupgrade.logged_query(
        env.cr, "UPDATE stock_picking_type SET sequence_code = '-'"
    )


def prefill_stock_move_propagate_date(env):
    """propagate_date and propagate_date_minimum_delta are new on stock.move;
    the post-migration (fill_propagate_date_minimum_delta) sets them on every
    move, from the setting of 12.0 and the delta of the company of the move:
    two updates of every move (makmur: 1.7 million moves, 5 minutes). When
    the setting is on and all the companies have the same delta, every move
    gets the same values: the columns are added with them as default, which
    PostgreSQL gives to the existing rows without writing them, and the
    default is dropped at once (the ORM declares none in the database). The
    updates of the post-migration then find nothing to change.
    """
    cr = env.cr
    if (openupgrade.column_exists(cr, "stock_move", "propagate_date")
            or openupgrade.column_exists(
                cr, "stock_move", "propagate_date_minimum_delta")
            or not openupgrade.column_exists(
                cr, "res_company", "propagation_minimum_delta")):
        return
    defaults = []
    cr.execute("""
        SELECT value::boolean FROM ir_config_parameter
        WHERE key = 'stock.use_propagation_minimum_delta'""")
    row = cr.fetchone()
    if row and row[0]:
        defaults.append(("propagate_date", "boolean", "TRUE"))
    cr.execute("SELECT DISTINCT propagation_minimum_delta FROM res_company")
    deltas = [r[0] for r in cr.fetchall()]
    cr.execute("SELECT 1 FROM stock_move WHERE company_id IS NULL LIMIT 1")
    if len(deltas) == 1 and deltas[0] is not None and not cr.fetchone():
        defaults.append(
            ("propagate_date_minimum_delta", "integer", "%d" % deltas[0]))
    for column, sql_type, value in defaults:
        openupgrade.logged_query(
            cr, "ALTER TABLE stock_move ADD COLUMN %s %s DEFAULT %s"
            % (column, sql_type, value))
        openupgrade.logged_query(
            cr, "ALTER TABLE stock_move ALTER COLUMN %s DROP DEFAULT" % column)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    if openupgrade.table_exists(env.cr, 'report_stock_quantity'):
        # OCA module `stock_forecast_report` was installed
        # Renaming model and table for not collapsing with the following renames
        openupgrade.rename_models(
            env.cr, [("report.stock.quantity", "report.stock.quantity.ou")]
        )
        openupgrade.rename_tables(
            env.cr, [("report_stock_quantity", "report_stock_quantity_ou")]
        )
        # Remove duplicated access
        env.ref("stock.access_report_stock_quantity").unlink()
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    assure_stock_rule_company_is_correct(env)
    fill_inventory_line_categ(env)
    prefill_stock_picking_type_sequence_code(env)
    prefill_stock_move_propagate_date(env)
