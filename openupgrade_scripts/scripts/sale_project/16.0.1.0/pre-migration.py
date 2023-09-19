from openupgradelib import openupgrade


def _force_install_viin_analytic_tag_sale_project_module(env):
    viin_analytic_tag_sale_project_module = env["ir.module.module"].search(
        [("name", "=", "viin_analytic_tag_sale_project")]
    )
    if viin_analytic_tag_sale_project_module:
        viin_analytic_tag_sale_project_module.button_install()


@openupgrade.migrate()
def migrate(env, version):
    _force_install_viin_analytic_tag_sale_project_module(env)
