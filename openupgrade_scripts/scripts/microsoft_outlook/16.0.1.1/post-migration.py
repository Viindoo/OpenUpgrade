from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fetchmail_server SET server_type = 'outlook'
        WHERE use_microsoft_outlook_service = TRUE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_mail_server SET smtp_authentication = 'outlook'
        WHERE use_microsoft_outlook_service = TRUE
        """,
    )
