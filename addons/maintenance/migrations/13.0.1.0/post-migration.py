from openupgradelib import openupgrade


def merge_field_active_to_archive(env):
    column = openupgrade.get_legacy_name('active')
    if openupgrade.column_exists(
            env.cr, "maintenance_request", column):
        openupgrade.logged_query(
            env.cr, """
            UPDATE maintenance_request
            SET archive = TRUE
            WHERE {} = FALSE AND archive = FALSE
            """.format(column),
            )


@openupgrade.migrate()
def migrate(env, version):
    merge_field_active_to_archive(env)
