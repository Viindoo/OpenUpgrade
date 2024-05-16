# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "auth_signup", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["auth_signup.openupgrade_legacy_17_0_reset_password_email"],
    )
