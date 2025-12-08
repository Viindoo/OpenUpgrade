from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_timesheet", "17.0.1.1/noupdate_changes.xml")
