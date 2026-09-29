# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from random import choice
from string import digits

from openupgradelib import openupgrade

_field_renames = [
    ('hr.attendance', 'hr_attendance', 'name', 'check_in'),
]


def fill_employee_barcode_and_pin(env):
    """barcode and pin are new and get a random default. Left to the ORM, the
    default is evaluated once and written on every employee: they all share
    one badge ID and unique(barcode) cannot be created. Create the columns
    here with a value of their own for each employee.

    A 9.0 database may already have hr_employee.barcode from another module
    (e.g. to_attendance_device) with the same value on several employees: the
    first employee keeps it, the others get a new one.
    """
    cr = env.cr
    has_barcode = openupgrade.column_exists(cr, 'hr_employee', 'barcode')
    has_pin = openupgrade.column_exists(cr, 'hr_employee', 'pin')
    if not has_barcode:
        cr.execute("ALTER TABLE hr_employee ADD COLUMN barcode varchar")
    if not has_pin:
        cr.execute("ALTER TABLE hr_employee ADD COLUMN pin varchar")
    cr.execute("SELECT id, barcode FROM hr_employee ORDER BY id")
    barcodes = set()
    for employee_id, barcode in cr.fetchall():
        if barcode and barcode not in barcodes:
            barcodes.add(barcode)
        else:
            if barcode:
                openupgrade.message(
                    cr, 'hr_attendance', 'hr_employee', 'barcode',
                    'employee %s: badge ID %s is already used by another '
                    'employee, a new one is assigned', employee_id, barcode)
            barcode = None
            while not barcode or barcode in barcodes:
                barcode = "".join(choice(digits) for i in range(8))
            barcodes.add(barcode)
            cr.execute(
                "UPDATE hr_employee SET barcode = %s WHERE id = %s",
                (barcode, employee_id))
        if not has_pin:
            cr.execute(
                "UPDATE hr_employee SET pin = %s WHERE id = %s",
                ("".join(choice(digits) for i in range(4)), employee_id))


@openupgrade.migrate()
def migrate(env, version):
    fill_employee_barcode_and_pin(env)
    # As there are indexes, foreign keys, and so on, we need to keep the
    # original table, copy it and remove records, instead of renaming and copy
    # only sign in records
    openupgrade.logged_query(
        env.cr,
        """CREATE TABLE %s AS (
            SELECT * FROM hr_attendance
        )""" % openupgrade.get_legacy_name('hr_attendance')
    )
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM hr_attendance
        WHERE action != 'sign_in'"""
    )
    openupgrade.rename_fields(env, _field_renames)
    env.ref('hr_attendance.property_rule_attendace_manager').unlink()
    env.ref('hr_attendance.property_rule_attendace_employee').unlink()
