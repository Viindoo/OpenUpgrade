from openupgradelib import openupgrade


def recompute_total_amount_company(env):
    expense_to_recompute = env["hr.expense"].search([("sheet_id", "=", False)])
    expense_to_recompute._compute_total_amount_company()


def update_expense_unit_amount(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense
        SET unit_amount = 0.0
        WHERE id IN (
            SELECT he.id
            FROM hr_expense he
            JOIN product_product pp ON he.product_id = pp.id
            LEFT JOIN ir_property ip ON ip.name = 'standard_price'
                AND ip.res_id = CONCAT('product.product,', pp.id)
                AND he.company_id = ip.company_id
            WHERE  he.unit_amount != 0.0
                AND ip.value_float IS NULL
        )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    update_expense_unit_amount(env)
    recompute_total_amount_company(env)
