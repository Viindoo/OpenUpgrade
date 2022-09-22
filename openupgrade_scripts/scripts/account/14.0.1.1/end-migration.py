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


def _recompute_amount_residual(env):
    account_move_lines_to_recompute = env['account.move.line'].search([
        ('parent_state', '=', 'posted'),
        ('move_id.payment_state', 'in', ['not_paid', 'in_payment', 'partial'])])
    account_move_lines_to_recompute._compute_amount_residual()


@openupgrade.migrate()
def migrate(env, version):
    _recompute_amount_residual(env)
    _make_correct_account_type(env)
