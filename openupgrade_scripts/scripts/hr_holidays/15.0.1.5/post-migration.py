import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _fill_hr_leave_type_holiday_allocation_id(env):
    leaves = env["hr.leave"].search(
        [
            ("holiday_status_id.requires_allocation", "=", "yes"),
            ("date_from", "!=", False),
            ("date_to", "!=", False),
        ],
        order="date_to, id",
    )
    leaves._compute_from_holiday_status_id()


def _map_hr_leave_allocation_date_to(env):
    env.cr.execute(
        """
        SELECT id FROM hr_leave_allocation
        WHERE state = 'validate' AND %s IS NOT NULL
        """,
        (openupgrade.get_legacy_name("date_to"),),
    )
    allocation_ids = [d[0] for d in env.cr.fetchall()]
    allocations_to_update = env["hr.leave.allocation"]
    for hla in env["hr.leave.allocation"].browse(allocation_ids):
        leave_unit = "number_of_%s_display" % (
            "hours" if hla.holiday_status_id.request_unit == "hour" else "days"
        )
        if hla.max_leaves >= sum(hla.taken_leave_ids.mapped(leave_unit)):
            allocations_to_update |= hla

    if allocations_to_update:
        # Using SQL to update date_to
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE hr_leave_allocation
            SET date_to = %s
            WHERE id IN %s
            """
            % (
                openupgrade.get_legacy_name("date_to"),
                tuple(allocations_to_update.ids),
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    _fill_hr_leave_type_holiday_allocation_id(env)
    openupgrade.load_data(env.cr, "hr_holidays", "15.0.1.5/noupdate_changes.xml")
    _map_hr_leave_allocation_date_to(env)
