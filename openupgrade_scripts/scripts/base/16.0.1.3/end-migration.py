from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Call disable_invalid_filters in every edition of openupgrade"""
    openupgrade.disable_invalid_filters(env)
