from openupgradelib import openupgrade

def _recompute_hr_job(env):
    jobs = env['hr.job'].search([])
    jobs._compute_employees()

@openupgrade.migrate()
def migrate(env, version):
    _recompute_hr_job(env)
