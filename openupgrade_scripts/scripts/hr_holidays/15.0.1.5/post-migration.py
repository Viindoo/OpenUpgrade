import logging

from openupgradelib import openupgrade

from odoo import api
from odoo.exceptions import ValidationError

from odoo.addons.hr_holidays.models.hr_leave import HolidaysRequest

_logger = logging.getLogger(__name__)


@api.constrains("holiday_allocation_id")
def _check_allocation_id(self):
    """Don't raise ValidationError in _check_allocation_id method."""
    try:
        return HolidaysRequest._check_allocation_id._original_method(self)
    except ValidationError:
        _logger.warning(
            "Could not find an allocation of type %s for the time off with ID %s."
            "\nRequires allocation of this type is now set to 'No Limit'."
            "\nPlease review requires allocation of this type manually "
            "after the migration."
            % (self.holiday_status_id.mapped("display_name"), self.ids)
        )


_check_allocation_id._original_method = HolidaysRequest._check_allocation_id
HolidaysRequest._check_allocation_id = _check_allocation_id


def _fill_hr_leave_type_holiday_allocation_id(env):
    Allocation = env["hr.leave.allocation"].with_context(active_test=False)
    employee_leaves = (
        env["hr.leave"]
        .with_context(active_test=False)
        .search(
            [
                ("holiday_status_id.requires_allocation", "=", "yes"),
                ("holiday_type", "=", "employee"),
                ("date_from", "!=", False),
                ("date_to", "!=", False),
            ]
        )
    )
    for employee in employee_leaves.employee_id:
        # sorted by `date_from`
        employee_allocations = Allocation.search(
            [("employee_id", "=", employee.id), ("holiday_type", "=", "employee")]
        ).sorted("date_from")
        number_of_days_diff = 0.0
        for allocation in employee_allocations:
            number_of_days = allocation.number_of_days
            # number_of_hours = allocation.number_of_hours_display
            leaves_of_employee = employee_leaves.filtered(
                lambda r: r.employee_id == employee
                and r.holiday_status_id == allocation.holiday_status_id
            )
            leaves_of_allocation = env["hr.leave"]
            total_days = number_of_days_diff
            leaves_of_employee = leaves_of_employee.sorted("date_from")
            for leave in leaves_of_employee:
                leaves_of_allocation |= leave
                if leave.state in ("confirm", "validate1", "validate"):
                    total_days += leave.number_of_days
                if total_days >= number_of_days or leave == leaves_of_employee[-1]:
                    number_of_days_diff = (
                        total_days - number_of_days
                        if total_days > number_of_days
                        else 0.0
                    )
                    # update `holiday_allocation_id`
                    leave_ids = str(tuple(leaves_of_allocation.ids)).replace(",)", ")")
                    openupgrade.logged_query(
                        env.cr,
                        """
                        UPDATE hr_leave
                        SET holiday_allocation_id = %s
                        WHERE id in %s
                        """
                        % (allocation.id, leave_ids),
                    )
                    # Exclude updated leaves
                    employee_leaves -= leaves_of_allocation
                    break


@openupgrade.migrate()
def migrate(env, version):
    _fill_hr_leave_type_holiday_allocation_id(env)
    openupgrade.load_data(env.cr, "hr_holidays", "15.0.1.5/noupdate_changes.xml")
