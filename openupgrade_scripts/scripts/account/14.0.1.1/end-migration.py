import logging
import threading
from odoo.models import PREFETCH_MAX
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


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


def _get_to_rec_number(todo, finished):
    to_rec_number = finished + PREFETCH_MAX
    remain = todo - finished
    return to_rec_number if remain >= to_rec_number else remain


def _switch_default_account_and_outstanding_account(env):
    env.cr.execute("""
        WITH sub AS(
            SELECT aml.id AS aml_id,
                am.id AS move_id,
                aj.payment_debit_account_id,
                aj.payment_credit_account_id
            FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN account_journal aj ON am.journal_id = aj.id
            WHERE
                AND aj.type IN ('bank', 'cash')
                AND aml.account_internal_type = 'liquidity'
                AND aml.statement_id IS NULL
        )
        UPDATE account_move_line aml
        SET account_id =
            CASE
                WHEN aml.credit > 0 AND aml.debit = 0 THEN sub.payment_credit_account_id
                WHEN aml.debit > 0 AND aml.credit = 0 THEN sub.payment_debit_account_id
            END
        FROM sub
        WHERE aml.id = sub.aml_id
            AND aml.display_type NOT IN ('line_section', 'line_note')
        RETURNING sub.move_id
    """)
    moves_to_reload_counterpart = env['account.move'].search([('id', 'in', [rec[0] for rec in env.cr.fetchall()])])
    records_count = len(moves_to_reload_counterpart)
    finished = 0
    for moves in env['to.base'].splittor(moves_to_reload_counterpart, PREFETCH_MAX):
        _logger.info(
            "start reload counterpart for journal items %s~%s in total %s records",
            finished + 1, _get_to_rec_number(records_count, finished), records_count
        )
        with env.cr.savepoint():
            moves.action_delete_counterpart()
            moves.action_smart_create_counterpart()
        finished += PREFETCH_MAX


def _recompute_amount_residual(env):
    account_move_lines_to_recompute = env['account.move.line'].search([
        ('parent_state', '=', 'posted'),
        ('currency_id', '!=', False),
        ('amount_residual_currency', '=', 0.0)
    ])
    records_count = len(account_move_lines_to_recompute)
    finished = 0
    for lines in env['to.base'].splittor(account_move_lines_to_recompute, PREFETCH_MAX):
        _logger.info(
            "start computing amount residual currency for journal items %s~%s in total %s records",
            finished + 1, _get_to_rec_number(records_count, finished), records_count
        )
        with env.cr.savepoint():
            lines.with_context(skip_account_move_synchronization=True)._compute_amount_residual()
        finished += PREFETCH_MAX


@openupgrade.migrate()
def migrate(env, version):
    _make_correct_account_type(env)
    _switch_default_account_and_outstanding_account(env)
    _recompute_amount_residual(env)
