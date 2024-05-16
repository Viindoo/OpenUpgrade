from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(env, "utm", "utm_campaign", "unique_name")
    openupgrade.delete_sql_constraint_safely(env, "utm", "utm_medium", "unique_name")
    openupgrade.delete_sql_constraint_safely(env, "utm", "utm_source", "unique_name")
    openupgrade.delete_sql_constraint_safely(env, "utm", "utm_tag", "name_uniq")
