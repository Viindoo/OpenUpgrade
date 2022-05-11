from openupgradelib import openupgrade


def _convert_field_m2o_to_m2m(env):
    # Convert m2o to m2m in 'project.task'
    openupgrade.m2o_to_x2m(
        env.cr, env["project.task"], "project_task", "user_ids", "user_id"
    )


def _migration_add_followes_allowed_internal_user_ids_project(env):
    openupgrade.logged_query(
        env.cr,
        """
            SELECT project_project_id as pid, res_users_id as uid
            FROM project_allowed_internal_users_rel
        """,
    )
    for r in env.cr.dictfetchall():
        projects = env["project.project"].browse(r["pid"]).exists()
        partner_ids = env["res.users"].browse(r["uid"]).exists().partner_id.ids
        projects.message_subscribe(partner_ids)


def _migration_add_followes_allowed_portal_user_ids_project(env):
    openupgrade.logged_query(
        env.cr,
        """
            SELECT project_project_id as pid, res_users_id as uid
            FROM project_allowed_portal_users_rel
        """,
    )
    for r in env.cr.dictfetchall():
        projects = env["project.project"].browse(r["pid"]).exists()
        partner_ids = env["res.users"].browse(r["uid"]).exists().partner_id.ids
        projects.message_subscribe(partner_ids)


def _migration_add_followes_allowed_user_ids_task(env):
    openupgrade.logged_query(
        env.cr,
        """
            SELECT project_task_id as tid, res_users_id as uid
            FROM project_task_res_users_rel
        """,
    )
    for r in env.cr.dictfetchall():
        tasks = env["project.task"].browse(r["tid"]).exists()
        partner_ids = env["res.users"].browse(r["uid"]).exists().partner_id.ids
        tasks.message_subscribe(partner_ids)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "project", "15.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "project",
        [
            "mail_template_data_project_task",
            "rating_project_request_email_template",
            "project_public_members_rule",
        ],
    )
    _convert_field_m2o_to_m2m(env)
    _migration_add_followes_allowed_internal_user_ids_project(env)
    _migration_add_followes_allowed_portal_user_ids_project(env)
    _migration_add_followes_allowed_user_ids_task(env)
