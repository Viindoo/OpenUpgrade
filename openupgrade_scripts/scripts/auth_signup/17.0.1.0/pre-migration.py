# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "auth_signup.reset_password_email",
        "auth_signup.openupgrade_legacy_17_0_reset_password_email",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
