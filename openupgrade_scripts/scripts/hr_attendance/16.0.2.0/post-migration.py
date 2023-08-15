from openupgradelib import openupgrade


def correct_rule_permissions(env):
    """
    Since commit 57b52e80e7bcf61f42f5125c9272666ac110860f, rule
    `hr_attendance_rule_attendance_employee` has changed the `perm_read` to True
    without any migration scripts. This function is to check and make sure the
    `perm_read` is True before loading the `noupdate_changes.xml` file, to avoid
    error of constraint `ir_rule_no_access_rights`.
    """
    rule_attendance_employee = env.ref(
        "hr_attendance.hr_attendance_rule_attendance_employee", raise_if_not_found=False
    )
    if rule_attendance_employee and not rule_attendance_employee.perm_read:
        rule_attendance_employee.perm_read = True


@openupgrade.migrate()
def migrate(env, version):
    correct_rule_permissions(env)
    openupgrade.load_data(env.cr, "hr_attendance", "16.0.2.0/noupdate_changes.xml")
