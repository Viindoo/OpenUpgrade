# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('hr_attendance.hr_employee_print_badge', 'hr.hr_employee_print_badge')
]


def detach_user_from_archived_duplicate_employee(cr):
    """13.0 adds unique(user_id, company_id) on hr.employee. An archived
    employee that holds the user of an active employee of the same company
    (the employee 10.0 creates for the administrator, archived by the
    migration of 10.0: both hold the administrator since 12.0) loses the user,
    so that the constraint can be created; the active employee keeps it. Two
    active employees of one user are left as they are.
    """
    openupgrade.logged_query(
        cr, """
        UPDATE hr_employee e
        SET user_id = NULL
        WHERE NOT e.active AND e.user_id IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM hr_employee o
                WHERE o.user_id = e.user_id AND o.id != e.id AND o.active
                    AND o.company_id IS NOT DISTINCT FROM e.company_id)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    detach_user_from_archived_duplicate_employee(env.cr)
    openupgrade.update_module_moved_fields(
        env.cr, "hr.employee", ["barcode", "pin"], "hr_attendance", "hr",
    )
