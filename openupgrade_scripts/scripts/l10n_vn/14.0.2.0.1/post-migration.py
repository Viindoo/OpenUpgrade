from openupgradelib import openupgrade


def _create_new_vietnam_accounts(env):
    """Create new accounts in v14"""
    for company in env["res.company"].search(
        [("chart_template_id", "=", env.ref("l10n_vn.vn_template").id)]
    ):
        accounts = env["account.account"].search([("company_id", "=", company.id)])
        vn_template = env.ref("l10n_vn.vn_template", raise_if_not_found=False)
        account_ids = []
        for account_id in ("1541", "1542", "1543", "1544", "911"):
            if not accounts.filtered(lambda a: a.code == account_id):
                account_ids.append(account_id)
        query = """INSERT INTO account_account
            ( name, code, user_type_id, company_id, reconcile)
            SELECT name, code, user_type_id, %s, reconcile
            FROM account_account_template
            WHERE chart_template_id = %s AND
                code IN %s"""
        openupgrade.logged_query(
            env.cr,
            query,
            (company.id, vn_template.id, tuple(account_ids)),
        )


def _make_correct_account_type(env):
    for company in env["res.company"].search(
        [("chart_template_id", "=", env.ref("l10n_vn.vn_template").id)]
    ):
        vn_template = env.ref("l10n_vn.vn_template", raise_if_not_found=False)
        query = """ UPDATE account_account as ac
            SET user_type_id=act.user_type_id
            FROM account_account_template as act
            WHERE ac.code = act.code
                AND ac.user_type_id != act.user_type_id
                AND ac.company_id = %s
                AND act.chart_template_id = %s """
        openupgrade.logged_query(
            env.cr,
            query,
            (company.id, vn_template.id),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "l10n_vn", "14.0.2.0.1/noupdate_changes.xml")
    _create_new_vietnam_accounts(env)
    _make_correct_account_type(env)
