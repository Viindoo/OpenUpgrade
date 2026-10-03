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
        "mobile",
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

    # On the private phone, we transfer the phone from the partner, and if not
    # filled, the mobile
    field_mapping = {
        "private_city": ["city"],
        "private_street": ["street"],
        "private_street2": ["street2"],
        "private_email": ["email"],
        "private_phone": ["phone", "mobile"],
        "private_zip": ["zip"],
        "private_country_id": ["country_id"],
        "private_state_id": ["state_id"],
    }

    def _partner_values(table_alias, partner_field):
        column = f"{table_alias}.{partner_field}"
        if partner_field not in translated_fields:
            # For non-translated fields, use direct value
            return [column]
        # For translated fields, extract value from JSONB
        # Try en_US first, then fallback to first available key
        # Handle NULL fields safely
        return [
            f"""CASE WHEN {column} IS NOT NULL
                     THEN {column}->>'en_US' END""",
            f"""CASE WHEN {column} IS NOT NULL
                     THEN (SELECT {column}->>k
                            FROM jsonb_object_keys({column}) k
                            LIMIT 1) END""",
        ]

    for emp_field, emp_partner_fields in field_mapping.items():
        values = [f"he.{emp_field}"]
        # First the copy containing private data, then res.partner
        for table_alias in ("rpp", "rp"):
            for partner_field in emp_partner_fields:
                values += _partner_values(table_alias, partner_field)
        values_str = ",\n                ".join(values)
        set_parts.append(
            f"""{emp_field} = COALESCE(
                {values_str}
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


def _transfer_private_address_typed_as_name(env):
    """A private address is often entered as a contact whose name is the
    address itself ("12 Main Street, Springfield"), with no address field
    filled. Nothing above picks it up, and the end-migration merges that
    contact into the work contact, which keeps its own name: the address is
    lost. Keep it as the private street of the employee."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee he
        SET private_street = rp.name
        FROM res_partner rp
        WHERE he.address_home_id = rp.id
            AND he.private_street IS NULL AND he.private_street2 IS NULL
            AND he.private_city IS NULL AND he.private_zip IS NULL
            AND rp.name IS NOT NULL AND rp.name != he.name
            AND NOT COALESCE(rp.is_company, FALSE)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _transfer_employee_private_data(env)
    _transfer_private_address_typed_as_name(env)
    openupgrade.load_data(env, "hr", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xml_records)
