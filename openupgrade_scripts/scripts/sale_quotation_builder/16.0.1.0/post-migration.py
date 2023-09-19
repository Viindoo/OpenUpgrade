from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5


def _bs5_field_migration(env):
    templates = env["sale.order.template"].with_context(active_test=False).search([])
    for template in templates:
        new_description = convert_string_bootstrap_4to5(template.website_description)
        if template.website_description != new_description:
            template.website_description = new_description


@openupgrade.migrate()
def migrate(env, version):
    _bs5_field_migration(env)
