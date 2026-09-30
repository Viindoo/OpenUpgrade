# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql

_tables_rename = [
    ("account_invoice_transaction_rel", "openupgrade_legacy_13_0_ait_rel")
]

_column_renames = {
    'payment_acquirer': [('website_published', None)],
}

_column_copies = {
    'payment_acquirer': [('environment', None, None)],  # Preserve source value
}

_field_renames = [
    ('payment.acquirer', 'payment_acquirer', 'image_medium', 'image_128'),
    ('payment.acquirer', 'payment_acquirer', 'environment', 'state'),
]

_xmlid_renames = [
    ('payment.payment_acquirer_ogone', 'payment.payment_acquirer_ingenico'),
]


def map_payment_acquirer_state(cr):
    """ Adapt payment acquirer states to new definition.

    Done here for avoiding possible errors due to invalid state value when
    updating records.
    """
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """UPDATE payment_acquirer
            SET state = CASE WHEN {} THEN 'enabled' ELSE 'disabled' END
            WHERE {} = 'prod'"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name('website_published')),
            sql.Identifier(openupgrade.get_legacy_name('environment'))
        )
    )
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """UPDATE payment_acquirer
            SET state = 'disabled'
            WHERE NOT {} AND {} = 'test'"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name('website_published')),
            sql.Identifier(openupgrade.get_legacy_name('environment'))
        )
    )
    # The environment of a wire transfer acquirer did nothing up to 12.0 (it
    # only shows payment instructions); as a state, 'test' puts a "Test Mode"
    # badge next to it on the checkout. A published one was in use: enable it.
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """UPDATE payment_acquirer
            SET state = 'enabled'
            WHERE provider = 'transfer' AND {} AND {} = 'test'"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name('website_published')),
            sql.Identifier(openupgrade.get_legacy_name('environment'))
        )
    )


def move_transfer_post_msg_to_pending_msg(cr):
    """Up to 12.0 a wire transfer acquirer keeps its payment instructions (the
    bank accounts) in post_msg, shown under the pending message once the order
    is placed. 13.0 drops post_msg and shows the instructions in pending_msg:
    append post_msg to pending_msg, and its translated terms with it, or the
    buyers no longer see where to pay."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE payment_acquirer
        SET pending_msg = COALESCE(pending_msg, '') || post_msg
        WHERE provider = 'transfer' AND COALESCE(post_msg, '') != ''
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_translation t
        SET name = 'payment.acquirer,pending_msg'
        FROM payment_acquirer a
        WHERE t.name = 'payment.acquirer,post_msg' AND t.res_id = a.id
            AND a.provider = 'transfer'
            AND NOT EXISTS (
                SELECT 1 FROM ir_translation t2
                WHERE t2.name = 'payment.acquirer,pending_msg'
                    AND t2.res_id = t.res_id AND t2.lang = t.lang
                    AND t2.type = t.type AND md5(t2.src) = md5(t.src))
        """,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    move_transfer_post_msg_to_pending_msg(env.cr)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_tables(env.cr, _tables_rename)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    # Fix image of payment.acquirer after renaming column to image_128
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image_medium' and res_model = 'payment.acquirer'
        """,
    )
    map_payment_acquirer_state(env.cr)
