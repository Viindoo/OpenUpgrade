# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_models_renames = [
    ("mail.channel", "discuss.channel"),
    ("mail.channel.member", "discuss.channel.member"),
    ("mail.channel.rtc.session", "discuss.channel.rtc.session"),
]
_tables_renames = [
    ("mail_channel", "discuss_channel"),
    ("mail_channel_member", "discuss_channel_member"),
    ("mail_channel_rtc_session", "discuss_channel_rtc_session"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
