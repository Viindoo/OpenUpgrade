# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_rename_xmlids = [
    (
        "note.mail_activity_data_reminder",
        "project_todo.mail_activity_data_reminder",
    ),
]


def _convert_note_tag_to_project_tags(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_tags (color, create_uid, write_uid, name, create_date, write_date)
        SELECT color, create_uid, write_uid, name, create_date, write_date
        FROM note_tag
        ON CONFLICT (name) DO NOTHING;
        """,
    )


def _convert_note_note_to_project_task(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task ADD COLUMN note_id INTEGER;
        INSERT INTO project_task(
            create_uid, write_uid, create_date, write_date,
            active, name, description, priority, sequence, state, project_id,
            display_in_project, company_id, color, note_id
        )
        SELECT create_uid, write_uid, create_date, write_date,
               open, name, memo, '0', sequence, '01_in_progress', null,
               true, company_id, color, id
        FROM note_note
        """,
    )


def _fill_project_tags(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
        SELECT
            project_task.id AS project_task_id,
            project_tags.id AS project_tags_id
        FROM note_tags_rel
        JOIN note_note ON note_tags_rel.note_id = note_note.id
        JOIN project_task ON project_task.note_id = note_note.id
        JOIN note_tag ON note_tags_rel.tag_id = note_tag.id
        JOIN project_tags ON project_tags.name = note_tag.name;
        """,
    )


def _fill_stage_for_todo_task(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task_type ADD COLUMN note_stage_id INTEGER;
        INSERT INTO project_task_type (
            create_uid, write_uid, create_date, write_date, active,
            user_id, sequence, name, fold, note_stage_id
        )
        SELECT
            create_uid, write_uid, create_date, write_date, true,
            user_id, sequence, name, fold, id
        FROM note_stage
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO project_task_user_rel(
            task_id, user_id, stage_id
        )
        SELECT
            project_task.id task_id,
            project_task_type.user_id,
            project_task_type.id stage_id
        FROM note_stage_rel rel
        JOIN project_task on project_task.note_id = rel.note_id
        JOIN project_task_type on project_task_type.note_stage_id = rel.stage_id
        """,
    )


def _migrate_attached_records(env):
    # migrate attachment, mail feature.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_model = 'project.task',
            res_id = project_task.id
        FROM project_task
        WHERE ir_attachment.res_model = 'note.note' AND
              ir_attachment.res_id = project_task.note_id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_message
        SET model = 'project.task',
            res_id = project_task.id
        FROM project_task
        WHERE mail_message.model = 'note.note' AND
              mail_message.res_id = project_task.note_id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_message_subtype SET res_model = 'project.task' WHERE res_model = 'note.note'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_followers
        SET res_model = 'project.task',
            res_id = project_task.id
        FROM project_task
        WHERE mail_followers.res_model = 'note.note' AND
              mail_followers.res_id = project_task.note_id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_activity
        SET res_model = 'project.task',
            res_id = project_task.id
        FROM project_task
        WHERE mail_activity.res_model = 'note.note' AND
              mail_activity.res_id = project_task.note_id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_activity_type SET res_model = 'project.task' WHERE res_model = 'note.note'
        """,
    )


def _drop_tmp_columns(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task DROP COLUMN note_id;
        ALTER TABLE project_task_type DROP COLUMN note_stage_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_note_tag_to_project_tags(env)
    _convert_note_note_to_project_task(env)
    _fill_project_tags(env)
    _fill_stage_for_todo_task(env)
    _migrate_attached_records(env)
    _drop_tmp_columns(env)
    openupgrade.rename_xmlids(env.cr, _rename_xmlids)
