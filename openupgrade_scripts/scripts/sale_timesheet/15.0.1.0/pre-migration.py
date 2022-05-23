from openupgradelib import openupgrade


def _fast_fill_account_analytic_line_order_id(env):

    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS order_id integer DEFAULT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_analytic_line aal
            SET order_id = sol.order_id
            FROM sale_order_line sol
            WHERE aal.so_line IS NOT NULL AND aal.so_line = sol.id
            """,
    )


def _compute_is_cost_changed(env):
    if not openupgrade.column_exists(
        env.cr,
        "project_sale_line_employee_map",
        "is_cost_changed",
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE project_sale_line_employee_map
            ADD COLUMN is_cost_changed boolean
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_sale_line_employee_map
            SET is_cost_changed = CASE
                WHEN employee_id IS NOT NULL THEN true
                ELSE false
                END
            WHERE is_cost_changed IS NULL
            """,
    )


def _compute_cost(env):
    if not openupgrade.column_exists(
        env.cr,
        "project_sale_line_employee_map",
        "cost",
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE project_sale_line_employee_map
            ADD COLUMN cost numeric
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_sale_line_employee_map AS pslem
            SET cost = CASE
                WHEN he.timesheet_cost IS NOT NULL THEN he.timesheet_cost
                ELSE 0
                END
            FROM hr_employee AS he
                WHERE pslem.employee_id = he.id
            """,
    )


def _set_value_of_analytic_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_task
            SET analytic_account_id = so.analytic_account_id
            FROM
                project_task AS pt
                INNER JOIN sale_order AS so
                    ON pt.sale_order_id = so.id
            WHERE pt.analytic_account_id IS NULL
            """,
    )


def _compute_timesheet_invoice_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery (
                order_line_id,
                product_id,
                product_type,
                product_invoice_policy
                ) AS (
                    SELECT sol.id AS sol_id, product_id, pt.type, pt.invoice_policy
                    FROM sale_order_line sol
                        JOIN product_template AS pt
                            ON pt.id = sol.product_id
        )
        UPDATE account_analytic_line AS aal
        SET timesheet_invoice_type = CASE
            WHEN aal.amount > 0 THEN 'other_revenues'
            ELSE 'other_costs'
            END
        FROM subquery sb
        WHERE
            project_id IS NULL
            AND NOT (
                aal.so_line IS NOT NULL
                AND aal.so_line = sb.order_line_id
                AND sb.product_type = 'service'
            )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery (
                order_line_id,
                product_id,
                product_type,
                product_invoice_policy
                ) AS (
                    SELECT sol.id AS sol_id, product_id, pt.type, pt.invoice_policy
                    FROM sale_order_line sol
                        JOIN product_template AS pt
                            ON pt.id = sol.product_id
        )
        UPDATE account_analytic_line AS aal
        SET timesheet_invoice_type = CASE
            WHEN aal.amount > 0 THEN 'other_revenues'
            ELSE 'other_costs'
            END
        FROM subquery sb
        WHERE
            project_id IS NULL
            AND (
                aal.so_line IS NOT NULL
                AND aal.so_line = sb.order_line_id
                AND    sb.product_type = 'service'
            )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line AS aal
        SET timesheet_invoice_type = 'non_billable'
        WHERE
            project_id IS NOT NULL
            AND aal.so_line IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery (
                order_line_id,
                product_id,
                product_type,
                product_invoice_policy
                ) AS (
                    SELECT sol.id AS sol_id, product_id, pt.type, pt.invoice_policy
                    FROM sale_order_line sol
                        JOIN product_template AS pt
                            ON pt.id = sol.product_id
        )
        UPDATE account_analytic_line AS aal
        SET timesheet_invoice_type = Null
        FROM subquery sb
        WHERE
            project_id IS NOT NULL
            AND aal.so_line IS NOT NULL
            AND aal.so_line = sb.order_line_id
            AND sb.product_type != 'service'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery (
                order_line_id,
                product_id,
                product_type,
                product_invoice_policy
                ) AS (
                    SELECT sol.id AS sol_id, product_id, pt.type, pt.invoice_policy
                    FROM sale_order_line sol
                        JOIN product_template AS pt
                            ON pt.id = sol.product_id
        )
        UPDATE account_analytic_line AS aal
        SET timesheet_invoice_type = Case
            WHEN
                sb.product_type = 'service'
                AND sb.product_invoice_policy = 'timesheet'
                AND aal.amount > 0
            THEN 'timesheet_revenues'
            WHEN
                sb.product_type = 'service'
                AND sb.product_invoice_policy = 'timesheet'
                AND aal.amount <= 0
            THEN 'billable_time'
            WHEN
                sb.product_type = 'service'
                AND sb.product_invoice_policy = 'order'
            THEN 'billable_fixed'
            ELSE Null
            END
        FROM subquery sb
        WHERE
            project_id IS NOT NULL
            AND aal.so_line IS NOT NULL
            AND aal.so_line = sb.order_line_id
            AND sb.product_type = 'service'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fast_fill_account_analytic_line_order_id(env)
    _compute_is_cost_changed(env)
    _compute_cost(env)
    _set_value_of_analytic_account_id(env)
    _compute_timesheet_invoice_type(env)
