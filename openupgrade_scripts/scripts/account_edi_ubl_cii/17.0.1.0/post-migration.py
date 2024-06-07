# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _res_partner_fill_value(env):
    partners = (
        env["res.partner"]
        .with_context(active_test=False)
        .search(
            [
                "|",
                "|",
                ("country_id", "!=", False),
                ("vat", "!=", False),
                ("company_registry", "!=", False),
            ]
        )
    )
    partners._compute_ubl_cii_format()
    partners._compute_peppol_endpoint()
    partners._compute_peppol_eas()


@openupgrade.migrate()
def migrate(env, version):
    _res_partner_fill_value(env)
