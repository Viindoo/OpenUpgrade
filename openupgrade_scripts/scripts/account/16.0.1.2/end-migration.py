from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "analytic_tag"):
        openupgrade.logged_query(
            env.cr,
            """
                INSERT INTO analytic_tag (
                    id,
                    name,
                    color,
                    active,
                    company_id,
                    create_uid,
                    write_uid,
                    write_date
                )
                SELECT
                    id,
                    name,
                    color,
                    active,
                    company_id,
                    create_uid,
                    write_uid,
                    write_date
                FROM
                    account_analytic_tag
            """,
        )

        openupgrade.logged_query(
            env.cr,
            """
                INSERT INTO account_move_line_analytic_tag_rel (
                    account_move_line_id,
                    analytic_tag_id
                )
                SELECT
                    account_move_line_id,
                    account_analytic_tag_id
                FROM
                    account_analytic_tag_account_move_line_rel
            """,
        )
