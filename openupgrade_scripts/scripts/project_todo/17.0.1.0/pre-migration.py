# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _convert_note_tag_to_project_tags(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_tags (
            color, create_uid, write_uid, name, create_date, write_date
        )
        SELECT color, create_uid, write_uid, name, create_date, write_date
        FROM note_tag
        ON CONFLICT (name) DO NOTHING;
        """,
    )


def _convert_note_note_to_project_task(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_task ADD COLUMN old_note_id INTEGER"
    )
    # if the OCA project_task_code was installed, code is required
    column_exists = openupgrade.column_exists(env.cr, "project_task", "code")
    openupgrade.logged_query(
        env.cr,
        f"""
            INSERT INTO project_task(
                create_uid, write_uid, create_date, write_date,
                active, name, description, priority, sequence, state, project_id,
                display_in_project, company_id, color, old_note_id
                {column_exists and ", code" or ""}
            )
            SELECT create_uid, write_uid, create_date, write_date,
                open, name, memo, '0', sequence, '01_in_progress', null,
                true, company_id, color, id
                {column_exists and ", ('OU' || id::VARCHAR)" or ""}
            FROM note_note
            """,
    )


def _migrate_task_tags(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
        SELECT pt.id, ptag.id
        FROM note_tags_rel rel
        JOIN project_task pt ON pt.old_note_id = rel.note_id
        JOIN note_tag nt ON rel.tag_id = nt.id
        JOIN project_tags ptag ON ptag.name = nt.name
        ON CONFLICT (project_task_id, project_tags_id) DO NOTHING;
        """,
    )


def _convert_note_stage_to_project_task_type(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE project_task_type ADD COLUMN old_note_stage_id INTEGER"
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_type (
            create_uid, write_uid, create_date, write_date, active,
            user_id, sequence, name, fold, old_note_stage_id
        )
        SELECT
            create_uid, write_uid, create_date, write_date, true,
            user_id, sequence, name, fold, id
        FROM note_stage
        """,
    )


def _migrate_user_ids(env):
    # Migrate user_ids from note_note.user_id (directly assigned users)
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_user_rel (task_id, user_id)
        SELECT pt.id, nn.user_id
        FROM note_note nn
        JOIN project_task pt ON pt.old_note_id = nn.id
        WHERE nn.user_id IS NOT NULL
        ON CONFLICT (task_id, user_id) DO NOTHING
        """,
    )
    # Migrate user_ids from mail_followers
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_user_rel (task_id, user_id)
        SELECT DISTINCT pt.id, ru.id
        FROM mail_followers mf
        JOIN project_task pt ON pt.old_note_id = mf.res_id
        JOIN res_partner rp ON rp.id = mf.partner_id
        JOIN res_users ru ON ru.partner_id = rp.id
        WHERE mf.res_model = 'note.note'
            AND ru.id IS NOT NULL
        ON CONFLICT (task_id, user_id) DO NOTHING
        """,
    )


def _migrate_stage_ids(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH current_stage AS (
            SELECT nsr.note_id, ns.user_id, ptt.id FROM note_stage_rel nsr
            JOIN note_stage ns ON nsr.stage_id = ns.id
            JOIN project_task_type ptt ON ptt.old_note_stage_id = ns.id
        )
        UPDATE project_task_user_rel rel
        SET stage_id = cs.id
        FROM current_stage cs
        JOIN project_task pt ON cs.note_id = pt.old_note_id
        WHERE rel.user_id = cs.user_id AND rel.task_id = pt.id AND rel.stage_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH default_stage AS (
            SELECT DISTINCT ON (user_id) user_id, id FROM project_task_type
            WHERE old_note_stage_id IS NOT NULL
            ORDER BY user_id, sequence, old_note_stage_id
        )
        UPDATE project_task_user_rel rel
        SET stage_id = ds.id
        FROM default_stage ds
        WHERE rel.user_id = ds.user_id AND rel.stage_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_note_tag_to_project_tags(env)
    _convert_note_note_to_project_task(env)
    _convert_note_stage_to_project_task_type(env)
    _migrate_task_tags(env)
    _migrate_user_ids(env)
    _migrate_stage_ids(env)
    openupgrade.merge_models(env.cr, "note.note", "project.task", "old_note_id")
