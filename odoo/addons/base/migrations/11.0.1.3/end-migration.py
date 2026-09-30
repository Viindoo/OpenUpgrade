# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def unbind_filters_from_removed_actions(cr):
    """A favorite saved on a menu whose action a module removed (e.g. the
    Contacts of mail in 9.0, gone in 10.0) points to no action any more, and
    disable_invalid_filters would disable it: the users lose their saved
    searches. Unbind it instead: it then shows on every view of its model."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_filters f SET action_id = NULL
        WHERE f.action_id IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM ir_actions a WHERE a.id = f.action_id)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    unbind_filters_from_removed_actions(env.cr)
    openupgrade.disable_invalid_filters(env)
