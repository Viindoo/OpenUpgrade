from openupgradelib import openupgrade


def recompute_total_amount_company(env):
    expense_to_recompute = env["hr.expense"].search([("sheet_id", "=", False)])
    expense_to_recompute._compute_total_amount_company()


@openupgrade.migrate()
def migrate(env, version):
    recompute_total_amount_company(env)
