# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "hr.hr_plan_activity_type_company_rule",
    "hr.hr_plan_company_rule",
]


def _transfer_employee_private_data(env):
    """On v17, there's no more private res.partner records, and the base migration
    has copied private partners to table ou_res_partner_private, so we transfer the
    information to the dedicated employee fields from the copy containing private
    data if it exists, and from res.partner otherwise
    """
    cr = env.cr

    partner_fields = [
        "city",
        "street",
        "street2",
        "email",
        "phone",
        "zip",
        "country_id",
        "state_id",
    ]

    # Check which fields are translated
    cr.execute(
        """
        SELECT name FROM ir_model_fields
        WHERE model = 'res.partner'
        AND name IN %s
        AND translate = TRUE
        """,
        (tuple(partner_fields),),
    )
    translated_fields = {field[0] for field in cr.fetchall()}

    # Build query parts dynamically
    set_parts = ["lang = rp.lang"]

    field_mapping = {
        "private_city": "city",
        "private_street": "street",
        "private_street2": "street2",
        "private_email": "email",
        "private_phone": "phone",
        "private_zip": "zip",
        "private_country_id": "country_id",
        "private_state_id": "state_id",
    }

    for emp_field, partner_field in field_mapping.items():
        if partner_field in translated_fields:
            # For translated fields, extract value from JSONB
            # Try en_US first, then fallback to first available key
            # Handle NULL fields safely
            set_parts.append(
                f"""{emp_field} = COALESCE(
                he.{emp_field},
                CASE WHEN rpp.{partner_field} IS NOT NULL
                     THEN rpp.{partner_field}->>'en_US' END,
                CASE WHEN rpp.{partner_field} IS NOT NULL
                     THEN (SELECT rpp.{partner_field}->>k
                            FROM jsonb_object_keys(rpp.{partner_field}) k
                            LIMIT 1) END,
                CASE WHEN rp.{partner_field} IS NOT NULL
                     THEN rp.{partner_field}->>'en_US' END,
                CASE WHEN rp.{partner_field} IS NOT NULL
                     THEN (SELECT rp.{partner_field}->>k
                            FROM jsonb_object_keys(rp.{partner_field}) k
                            LIMIT 1) END
            )"""
            )
        else:
            # For non-translated fields, use direct value
            set_parts.append(
                f"""{emp_field} = COALESCE(
                he.{emp_field},
                rpp.{partner_field},
                rp.{partner_field}
            )"""
            )

    set_parts_str = ",\n            ".join(set_parts)
    query = f"""
        UPDATE hr_employee he
        SET {set_parts_str}
        FROM res_partner rp
        LEFT JOIN ou_res_partner_private rpp
        ON rp.id = rpp.id
        WHERE he.address_home_id = rp.id
    """

    openupgrade.logged_query(cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _transfer_employee_private_data(env)
    openupgrade.load_data(env, "hr", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)
