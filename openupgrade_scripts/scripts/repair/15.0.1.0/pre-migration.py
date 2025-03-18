from openupgradelib import openupgrade


def _convert_field_to_html(env):
    openupgrade.convert_field_to_html(
        env.cr, "repair_order ", "internal_notes", "internal_notes"
    )
    openupgrade.convert_field_to_html(
        env.cr, "repair_order ", "quotation_notes", "quotation_notes"
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_field_to_html(env)
