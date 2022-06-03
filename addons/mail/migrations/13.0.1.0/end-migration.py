from openupgradelib import openupgrade


def unlink_deprecated_message_from_channel(env):
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM mail_message_mail_channel_rel
           WHERE mail_message_id in (
               SELECT mm.id FROM mail_message_mail_channel_rel mmmcr
               JOIN mail_message mm ON mmmcr.mail_message_id = mm.id
               AND mm.model IS not null
               AND mm.model not in %s)""", (tuple(env.registry.models),))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    unlink_deprecated_message_from_channel(env)
