from openupgradelib import openupgrade


def _make_correct_account_type(env):
    query = """
        UPDATE account_account as ac
            SET user_type_id=aat.user_type_id
        FROM account_account_template as aat
            LEFT JOIN account_chart_template as act
                        ON aat.chart_template_id = act.id
            LEFT JOIN res_company as c
                        ON c.chart_template_id = act.id
        WHERE ac.code =
                CASE
                    WHEN
                        act.code_digits < LENGTH(aat.code) THEN aat.code
                    ELSE
                        CONCAT(aat.code,
                            REPEAT('0',act.code_digits - LENGTH(aat.code)))
                END
            AND ac.user_type_id != aat.user_type_id
            AND ac.company_id = c.id;
        UPDATE account_account as ac
            SET internal_type=at.type,
                internal_group=at.internal_group
        FROM account_account_type as at
        WHERE ac.user_type_id=at.id;
        """
    openupgrade.logged_query(
        env.cr,
        query,
    )
    
def _switch_default_account_and_outstanding_account(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery as (
            SELECT aml.id as aml_id,
            aj.payment_debit_account_id,
            aj.payment_credit_account_id,
            aml.debit, aml.credit
            FROM account_move_line aml
            JOIN account_journal aj on aml.journal_id = aj.id
            WHERE legacy_statement_unreconcile = TRUE
            AND aj.type IN ('bank', 'cash')
        )
        UPDATE account_move_line aml
        SET account_id =
        CASE
            WHEN subquery.debit > 0 THEN subquery.payment_debit_account_id
            WHEN subquery.credit > 0 THEN subquery.payment_credit_account_id
        END
        FROM subquery
        WHERE aml.id = subquery.aml_id
        AND (aml.display_type NOT IN ('line_section', 'line_note') OR aml.display_type IS NULL)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _make_correct_account_type(env)
    _switch_default_account_and_outstanding_account(env)
