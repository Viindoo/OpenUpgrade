from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(
        env.cr, "hr_recruitment", "15.0.1.1/noupdate_changes.xml"
    )
