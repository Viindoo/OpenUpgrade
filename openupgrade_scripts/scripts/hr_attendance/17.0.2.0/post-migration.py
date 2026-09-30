# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import uuid

from openupgradelib import openupgrade

from odoo import Command

_deleted_xml_records = [
    "hr_attendance.hr_attendance_report_rule_multi_company",
    "hr_attendance.hr_attendance_rule_attendance_employee",
    "hr_attendance.hr_attendance_rule_attendance_manager",
    "hr_attendance.hr_attendance_rule_attendance_manual",
    "hr_attendance.hr_attendance_rule_attendance_overtime_employee",
    "hr_attendance.hr_attendance_rule_attendance_overtime_manager",
]


def fill_res_company_hr_attendance_display_overtime(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET hr_attendance_display_overtime = hr_attendance_overtime
        """,
    )


def fill_res_company_attendance_kiosk_use_pin(env):
    group = env.ref("hr_attendance.group_hr_attendance_use_pin")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE res_company rc
        SET attendance_kiosk_use_pin = TRUE
        FROM res_users ru
        JOIN res_groups_users_rel group_rel ON group_rel.uid = ru.id
            AND group_rel.gid = {group.id}
        JOIN res_company_users_rel company_rel ON company_rel.user_id = ru.id
        WHERE company_rel.cid = rc.id AND ru.active
        """,
    )


def fill_res_company_attendance_kiosk_key(env):
    companies = env["res.company"].search([])
    for company in companies:
        company.attendance_kiosk_key = uuid.uuid4().hex


def fill_hr_attendance_overtime_hours(env):
    attendances = env["hr.attendance"].search([])
    # this way, the query in the compute method only is executed once
    attendances._compute_overtime_hours()


def _drop_links_the_target_group_has(env, old_xmlid, new_xmlid):
    """rename_xmlids(allow_merge=True) merges the groups in SQL: one UPDATE per
    many2many table (members, implied groups...) moves the links of the old group
    to the new one, and the unique pair of the table stops it when both groups
    have the same user, which happens with these two groups. openupgradelib then
    deletes the links of the old group left behind: its other members lost the
    access. Drop the links the new group already has, the UPDATE then goes through.
    """
    old = env.ref(old_xmlid, raise_if_not_found=False)
    new = env.ref(new_xmlid, raise_if_not_found=False)
    if not old or not new or old == new:
        return
    env.cr.execute(
        """SELECT cl.relname, a.attname
        FROM pg_constraint c
        JOIN pg_class cl ON cl.oid = c.conrelid
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
        WHERE c.contype = 'f' AND c.confrelid = 'res_groups'::regclass
            AND array_length(c.conkey, 1) = 1
            AND (SELECT count(*) FROM pg_attribute a2
                 WHERE a2.attrelid = c.conrelid AND a2.attnum > 0
                    AND NOT a2.attisdropped) = 2"""
    )
    for table, column in env.cr.fetchall():
        env.cr.execute(
            """SELECT attname FROM pg_attribute
            WHERE attrelid = %s::regclass AND attnum > 0
                AND NOT attisdropped AND attname != %s""",
            ('"%s"' % table, column),
        )
        other = env.cr.fetchone()[0]
        openupgrade.logged_query(
            env.cr,
            f"""DELETE FROM "{table}" t
            WHERE t."{column}" = %(old)s AND EXISTS (
                SELECT 1 FROM "{table}" t2
                WHERE t2."{column}" = %(new)s AND t2."{other}" = t."{other}")""",
            {"old": old.id, "new": new.id},
        )


def hr_attendance_menus(env):
    group_hr_attendance = env.ref("hr_attendance.group_hr_attendance")
    group_hr_attendance_kiosk = env.ref("hr_attendance.group_hr_attendance_kiosk")
    # Remove the groups of 16.0 from the Attendances menu
    env.ref("hr_attendance.menu_hr_attendance_root").write(
        {
            "groups_id": [
                Command.unlink(group_hr_attendance.id),
                Command.unlink(group_hr_attendance_kiosk.id),
            ]
        }
    )
    _drop_links_the_target_group_has(
        env,
        "hr_attendance.group_hr_attendance",
        "hr_attendance.group_hr_attendance_own_reader",
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "hr_attendance.group_hr_attendance",
                "hr_attendance.group_hr_attendance_own_reader",
            ),
        ],
        allow_merge=True,
    )
    # Remove the groups of 16.0 from the Attendances > Kiosk Mode menu
    env.ref("hr_attendance.menu_hr_attendance_kiosk_no_user_mode").write(
        {
            "groups_id": [
                Command.unlink(group_hr_attendance_kiosk.id),
            ]
        }
    )
    _drop_links_the_target_group_has(
        env,
        "hr_attendance.group_hr_attendance_kiosk",
        "hr_attendance.group_hr_attendance_own_reader",
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "hr_attendance.group_hr_attendance_kiosk",
                "hr_attendance.group_hr_attendance_own_reader",
            ),
        ],
        allow_merge=True,
    )


def add_attendance_own_reader_to_base_user(env):
    """
    Add hr_attendance.group_hr_attendance_own_reader to base.group_user's implied_ids.
    This ensures all users have access to read their own attendance records.
    """
    group_user = env.ref("base.group_user")
    group_attendance_own_reader = env.ref(
        "hr_attendance.group_hr_attendance_own_reader"
    )
    if group_attendance_own_reader not in group_user.implied_ids:
        group_user.write(
            {
                "implied_ids": [Command.link(group_attendance_own_reader.id)],
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    fill_res_company_hr_attendance_display_overtime(env)
    fill_res_company_attendance_kiosk_use_pin(env)
    fill_res_company_attendance_kiosk_key(env)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)
    fill_hr_attendance_overtime_hours(env)
    hr_attendance_menus(env)
    add_attendance_own_reader_to_base_user(env)
