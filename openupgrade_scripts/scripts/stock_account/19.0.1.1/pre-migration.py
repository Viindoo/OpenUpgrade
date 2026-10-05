# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "stock_account.stock_valuation_layer_company_rule",
    "stock_account.group_stock_accounting_automatic",
]


def stock_lot_avg_cost(env):
    """
    Precreate stock.lot#avg_cost to avoid compute method
    """
    openupgrade.add_fields(
        env,
        [
            ("avg_cost", "stock.lot", "stock_lot", "float", None, "stock_account", 0),
        ],
    )


def stock_move_is_fields(env):
    """
    Precreate stock.move#is_* to avoid compute method
    """
    openupgrade.add_fields(
        env,
        [
            (
                "is_in",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
            (
                "is_out",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
            (
                "is_dropship",
                "stock.move",
                "stock_move",
                "boolean",
                None,
                "stock_account",
                False,
            ),
        ],
    )


def res_company_category_defaults(env):
    """
    Since 19.0 the company holds the default valuation, cost method, stock
    journal and stock valuation account of the product categories, and writes
    them as the defaults of the categories (ir.default) on every write of a
    company (_set_category_defaults). The new columns take the defaults the
    categories have, the one of the company first, else the global one (journal
    and account: when they are of the company); left to their field defaults,
    the first write on a company turns every category without a value of its
    own to periodic valuation, standard cost and no stock journal.
    """
    openupgrade.add_fields(
        env,
        [
            (
                "inventory_valuation",
                "res.company",
                "res_company",
                "selection",
                None,
                "stock_account",
                "periodic",
            ),
            (
                "cost_method",
                "res.company",
                "res_company",
                "selection",
                None,
                "stock_account",
                "standard",
            ),
            (
                "account_stock_journal_id",
                "res.company",
                "res_company",
                "many2one",
                None,
                "stock_account",
            ),
            (
                "account_stock_valuation_id",
                "res.company",
                "res_company",
                "many2one",
                None,
                "stock_account",
            ),
        ],
    )
    company_default = """
        SELECT DISTINCT ON (rc.id) rc.id AS company_id, d.json_value
        FROM res_company rc
        JOIN ir_default d ON d.company_id = rc.id OR d.company_id IS NULL
        JOIN ir_model_fields f ON f.id = d.field_id
        WHERE f.model = 'product.category' AND f.name = %s
            AND d.user_id IS NULL AND d.condition IS NULL
        ORDER BY rc.id, d.company_id NULLS LAST, d.id
    """
    for column, field_name, mapping in (
        (
            "inventory_valuation",
            "property_valuation",
            {
                "manual_periodic": "periodic",
                "periodic": "periodic",
                "real_time": "real_time",
            },
        ),
        (
            "cost_method",
            "property_cost_method",
            {"standard": "standard", "fifo": "fifo", "average": "average"},
        ),
    ):
        for old_value, new_value in mapping.items():
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE res_company c
                SET {column} = %s
                FROM ({company_default}) dv
                WHERE c.id = dv.company_id
                    AND dv.json_value = %s
                """,
                (new_value, field_name, f'"{old_value}"'),
            )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE res_company c
        SET account_stock_journal_id = j.id
        FROM ({company_default}) dv
        JOIN account_journal j ON j.id = CASE
            WHEN dv.json_value ~ '^[0-9]+$' THEN dv.json_value::int END
        WHERE c.id = dv.company_id AND j.company_id = c.id
            AND c.account_stock_journal_id IS NULL
        """,
        ("property_stock_journal",),
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE res_company c
        SET account_stock_valuation_id = a.id
        FROM ({company_default}) dv
        JOIN account_account a ON a.id = CASE
            WHEN dv.json_value ~ '^[0-9]+$' THEN dv.json_value::int END
        JOIN account_account_res_company_rel r ON r.account_account_id = a.id
        WHERE c.id = dv.company_id AND r.res_company_id = c.id
            AND c.account_stock_valuation_id IS NULL
        """,
        ("property_stock_valuation_account_id",),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    stock_lot_avg_cost(env)
    stock_move_is_fields(env)
    res_company_category_defaults(env)
