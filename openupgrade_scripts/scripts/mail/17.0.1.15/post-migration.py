# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "mail.ir_rule_mail_channel_member_group_system",
    "mail.ir_rule_mail_channel_member_group_user",
    "mail.mail_channel_admin",
    "mail.mail_channel_rule",
    "mail.channel_all_employees",
    "mail.channel_member_general_channel_for_admin",
]


def _fill_res_company_alias_domain_id(env):
    icp = env["ir.config_parameter"]

    domain = icp.get_param("mail.catchall.domain")
    if domain:
        alias_domain = env["mail.alias.domain"].create(
            {
                "bounce_alias": icp.get_param("mail.bounce.alias"),
                "catchall_alias": icp.get_param("mail.catchall.alias"),
                "default_from": icp.get_param("mail.default.from"),
                "name": domain,
            }
        )
        companies = env["res.company"].with_context(active_test=False).search([])
        companies.write({"alias_domain_id": alias_domain.id})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "mail", "17.0.1.15/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _fill_res_company_alias_domain_id(env)
