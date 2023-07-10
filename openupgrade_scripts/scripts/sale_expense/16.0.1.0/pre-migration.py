from openupgradelib import openupgrade


def _dynamic_fast_fill_analytic_distribution_when_inherit_analytic_mixin(
    env, table_name
):
    """
    Dynamically fill analytic_distribution for model that inherit from analytic.mixin
    Hmmm this method should be placed in the library
    Take a look with example of account.move.line
    The idea is to take all the distribution of an account.move.line
    which has analytic.tag then form it as a jsonb like {'1': 100, '2': 50}
    and also check if the table has analytic_account_column then check if it
    exist in the analytic_account of all the analytic_distribution of the analytic tags
    then take it as the 100%, which mean an account.move.line both specify '2' as the
    analytic.account.id and it has 1 analytic.tag also have that analytic.account then
    the value will sum together
    """
    if not openupgrade.column_exists(env.cr, table_name, "analytic_distribution"):
        openupgrade.logged_query(
            env.cr,
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )
    is_having_analytic_account_id_col = openupgrade.column_exists(
        env.cr, table_name, "analytic_account_id"
    )
    # Build query
    select_query = f"""
        SELECT
        {table_name}.id,
        unnest(array_agg(tmp.tag_id)) AS tag,
        unnest(array_agg(tmp.account_id)) AS analytic_account_of_tag,
        unnest(array_agg(tmp.percentage)) AS percentage
    """
    groupby_query = f"""
        GROUP BY
            {table_name}.id
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH sub AS (
            WITH tmp AS (
                SELECT
                    id,
                    account_id,
                    percentage,
                    tag_id
                FROM
                account_analytic_distribution
            )
            {select_query}
            FROM
                {table_name}
                JOIN account_analytic_tag_{table_name}_rel rel
                    ON {table_name}.id = rel.{table_name}_id
                JOIN account_analytic_tag aat
                    ON aat.id = rel.account_analytic_tag_id
                JOIN tmp
                    ON tmp.tag_id = aat.id
            {groupby_query}
        )
        UPDATE {table_name}
        SET analytic_distribution = analytic_distribution_sub.analytic_distribution
        FROM (
            SELECT
                id,
                jsonb_object_agg(analytic_account_of_tag::text, total_percentage)
                AS analytic_distribution
            FROM (
                SELECT
                    sub.id,
                    analytic_account_of_tag,
                    sum(percentage) AS total_percentage
                FROM
                    sub
                GROUP BY
                    sub.id,
                    analytic_account_of_tag
            ) AS aggregated_data
            GROUP BY id
        ) AS analytic_distribution_sub
        WHERE {table_name}.id = analytic_distribution_sub.id
        """,
    )
    if is_having_analytic_account_id_col:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE {}
            SET analytic_distribution = analytic_distribution || jsonb_build_object({}::text, 100)
            WHERE analytic_account_id IS NOT NULL
            """.format(
                table_name, table_name + '.analytic_account_id'
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    _dynamic_fast_fill_analytic_distribution_when_inherit_analytic_mixin(
        env, "hr_expense"
    )
