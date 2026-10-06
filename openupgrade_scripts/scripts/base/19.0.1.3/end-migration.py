# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _ir_ui_menu_missing_action(env):
    """
    19.0 reads the path of the action of every menu when the web client loads
    its menus: a menu whose action record no longer exists stops the web client
    with "Record does not exist or has been deleted" (makmur: Human Resources /
    Configuration still pointed to the action hr.action_human_resources_configuration
    of 8.0, removed at 9.0). Such a menu loses its action, as a menu that only
    holds sub-menus.
    """
    env.cr.execute("SELECT id, action FROM ir_ui_menu WHERE action IS NOT NULL")
    missing = []
    for menu_id, action in env.cr.fetchall():
        model_name, _sep, res_id = action.partition(",")
        if (
            model_name not in env
            or not res_id.isdigit()
            or not env[model_name].sudo().browse(int(res_id)).exists()
        ):
            missing.append(menu_id)
    if missing:
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_ui_menu SET action = NULL WHERE id IN %s",
            (tuple(missing),),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.disable_invalid_filters(env)
    _ir_ui_menu_missing_action(env)
