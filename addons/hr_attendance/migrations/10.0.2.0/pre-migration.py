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
    """
    cr = env.cr
    if openupgrade.column_exists(cr, 'hr_employee', 'barcode'):
        return
    cr.execute(
        """ALTER TABLE hr_employee
        ADD COLUMN barcode varchar, ADD COLUMN pin varchar""")
    cr.execute("SELECT id FROM hr_employee ORDER BY id")
    barcodes = set()
    for employee_id, in cr.fetchall():
        barcode = None
        while not barcode or barcode in barcodes:
            barcode = "".join(choice(digits) for i in range(8))
        barcodes.add(barcode)
        pin = "".join(choice(digits) for i in range(4))
        cr.execute(
            "UPDATE hr_employee SET barcode = %s, pin = %s WHERE id = %s",
            (barcode, pin, employee_id))


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
