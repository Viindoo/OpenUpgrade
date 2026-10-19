# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_fields_renames = [
    (
        "mail.channel",
        "mail_channel",
        "channel_last_seen_partner_ids",
        "channel_member_ids",
    )
]
_models_renames = [("mail.channel.partner", "mail.channel.member")]
_tables_renames = [("mail_channel_partner", "mail_channel_member")]
_columns_renames = {
    "mail_message": [("add_sign", "email_add_signature")],
}
_xmlids_renames = [
    (
        "mail.channel_partner_general_channel_for_admin",
        "mail.channel_member_general_channel_for_admin",
    ),
    (
        "mail.ir_rule_mail_channel_partner_group_system",
        "mail.ir_rule_mail_channel_member_group_system",
    ),
    (
        "mail.ir_rule_mail_channel_partner_group_user",
        "mail.ir_rule_mail_channel_member_group_user",
    ),
]
_columns_copies = {
    "mail_channel_rtc_session": [
        ("channel_partner_id", "channel_member_id", "integer")
    ],
}


def _avoid_mail_notification_new_constraint(env):
    """Prior to Odoo 16, there is no unique constraint on the mail_notification table,
    so if there's any duplicate, the upgrade will fail.

    Let's preventively delete the duplicated entries, as at the end, they are not
    needed.
    """
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM mail_notification
        WHERE id IN (
            SELECT id FROM (
                SELECT id, row_number()
                OVER (
                    partition BY res_partner_id, mail_message_id ORDER BY id
                ) AS rnum FROM mail_notification
            ) t WHERE t.rnum > 1
        )""",
    )


def delete_obsolete_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "mail", "mail_channel_partner", "partner_or_guest_exists"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "mail", "mail_channel_rtc_session", "channel_partner_unique"
    )


def ir_act_server_rename_state_email(env):
    """
    ir.actions.server state selection key 'email' is now 'mail_post'.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_act_server
        SET state='mail_post'
        WHERE state='email';
        """,
    )


def mail_channel_channel_type_required(env):
    """
    channel_type is now required on mail.channel.
    Set default value 'channel' if no value was set.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel
        SET channel_type='channel'
        WHERE channel_type IS NULL;
        """,
    )


def mail_channel_unset_wrong_group_public_id(env):
    """
    - On 15.0, group_public_id was set to 'base.group_user' by default for all records.
    ```
    group_public_id = fields.Many2one(
        'res.groups',
        string='Authorized Group',
        default=lambda self: self.env.ref('base.group_user')
    )
    ```
    - On 16.0, group_public_id become a computed field, and a sql constraint was added
    to check group_public_id need to be NULL if channel_type is not 'channel'.
    ```
    group_public_id = fields.Many2one(
        'res.groups',
        string='Authorized Group',
        compute='_compute_group_public_id',
        readonly=False,
        store=True
    )
    _sql_constraints = [
        (
        'group_public_id_check',
        "CHECK (channel_type = 'channel' OR group_public_id IS NULL)",
        'Group authorization and group auto-subscription are only supported on channels.'
        )
    ]
    ```
    - So that constraint will fail on 16.0 if group_public_id is still set to
    'base.group_user'.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel
        SET group_public_id = NULL
        WHERE channel_type != 'channel';
        """,
    )


def mail_channel_private_compatibility(env):
    """In v15 you could set a private group that only members could access, now in v16
    this is not possible.
    Defining the group_public_id empty will make everyone can access, and leaving the
    value that has group_public_id with 'base.group_user' by default is totally wrong.
    In order to maintain the compatibility of the existing channels, two transformations
    are necessary:
    - If a channel is private, but had only one auto-subscription group (group_ids), those
    group become the authorized one (group_public_id) of the channel, and it remains as such
    as a channel, since at the end, the auto-subscription groups adds as members all the
    users of those groups, acting in the same way.
    - If the list of members was manual, then the channel becomes a 'Direct Messages'
    (channel_type='group'), keeping the channel name and authorized members.
    """
    env.cr.execute(
        """
        SELECT
            c.id,
            c.name,
            (
                SELECT COUNT(res_groups_id)
                FROM mail_channel_res_groups_rel
                WHERE mail_channel_id = c.id
            ) AS total_groups,
            (
                SELECT res_groups_id
                FROM mail_channel_res_groups_rel
                WHERE mail_channel_id = c.id
                LIMIT 1
            ) AS auto_subscribe_group_0
        FROM mail_channel AS c
        WHERE c.channel_type = 'channel' AND c.public = 'private'
        """
    )
    for channel_id, _name, total_groups, auto_subscribe_group_0 in env.cr.fetchall():
        if total_groups == 1:
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE mail_channel
                SET group_public_id = %s
                WHERE id = %s
                """,
                (auto_subscribe_group_0, channel_id),
            )
        else:
            # Remove the auto-subscription groups linked also to avoid
            # _constraint_group_id_channel()
            openupgrade.logged_query(
                env.cr,
                """
                DELETE FROM mail_channel_res_groups_rel
                WHERE mail_channel_id= %s
                """,
                (channel_id,),
            )
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE mail_channel
                SET channel_type = 'group', group_public_id = NULL
                WHERE id = %s
                """,
                (channel_id,),
            )


def scheduled_date_set_empty_strings_to_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_mail
        SET scheduled_date = NULL
        WHERE scheduled_date = '';
        """,
    )


def _to_mail_notif_and_email_create_mail_notification_index(env):
    """
    Only execute this method when module 'to_mail_notif_and_email'
    is found and installed to avoid error when init mail module
    because it has a constrain that we have overide in 'to_mail_notif_and_email'
    if not then we will get error when running migration of mail module
    """
    module_to_mail_notif_and_email = env["ir.module.module"].search(
        [("name", "=", "to_mail_notif_and_email"), ("state", "=", "to upgrade")]
    )
    if module_to_mail_notif_and_email:
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM mail_notification mn1
                  USING mail_notification mn2
            WHERE mn1.id > mn2.id
            AND mn1.mail_message_id = mn2.mail_message_id
            AND mn1.res_partner_id = mn2.res_partner_id
            AND mn1.notification_type = mn2.notification_type;
            """,
        )
        env.cr.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS unique_mail_message_id_res_partner_id_if_set
            ON mail_notification (mail_message_id, res_partner_id, notification_type)
            WHERE res_partner_id IS NOT NULL
            """
        )


def _update_mail_channel_name(env):
    # The name is not translated any more: keep it in the language of the users (the one most active internal users
    # have; for en_US the column already holds it), not any of the translations of the channel (one per language,
    # PostgreSQL took any of them: "umum" or "chung chung" from one run to the other on a database in en_US)
    openupgrade.logged_query(
        env.cr,
        """
        WITH lang AS (
            SELECT p.lang
            FROM res_users u
            JOIN res_partner p ON p.id = u.partner_id
            WHERE u.active AND NOT u.share AND p.lang IS NOT NULL
            GROUP BY p.lang
            ORDER BY count(*) DESC, p.lang
            LIMIT 1
        ), sub AS(
            SELECT DISTINCT ON (t.res_id) t.res_id, t.value
            FROM ir_translation t
            JOIN lang ON lang.lang = t.lang
            WHERE t.name = 'mail.channel,name'
            AND t.value IS NOT NULL AND t.value != ''
            AND t.src != t.value
            ORDER BY t.res_id, t.id DESC
        )
        UPDATE mail_channel mc
        SET name = sub.value
        FROM sub
        WHERE mc.id = sub.res_id
        """,
    )


def _force_install_viin_mail_channel_privacy_module(env):
    viin_mail_channel_privacy_module = env["ir.module.module"].search(
        [("name", "=", "viin_mail_channel_privacy")]
    )
    if viin_mail_channel_privacy_module:
        viin_mail_channel_privacy_module.button_install()


def _correct_mail_channel_group_public_id(env):
    # to add new constraint mail_channel_group_public_id_check
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel mc
        SET group_public_id = NULL
        WHERE mc.channel_type != 'channel' AND mc.group_public_id IS NOT NULL
        """,
    )


def _correct_res_users_notification_type(env):
    # to add new constraint res_users_notification_type
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_users
        SET notification_type = 'email'
        WHERE notification_type != 'email' AND share
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_mail_channel_name(env)
    _avoid_mail_notification_new_constraint(env)
    delete_obsolete_constraints(env)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_columns(env.cr, _columns_renames)
    openupgrade.copy_columns(env.cr, _columns_copies)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    ir_act_server_rename_state_email(env)
    mail_channel_channel_type_required(env)
    scheduled_date_set_empty_strings_to_null(env)
    # This method is only exist in Viindoo/Openupgrade for some
    # Technical reason
    _to_mail_notif_and_email_create_mail_notification_index(env)
    _force_install_viin_mail_channel_privacy_module(env)
    _correct_mail_channel_group_public_id(env)
    _correct_res_users_notification_type(env)
    mail_channel_private_compatibility(env)
    mail_channel_unset_wrong_group_public_id(env)
