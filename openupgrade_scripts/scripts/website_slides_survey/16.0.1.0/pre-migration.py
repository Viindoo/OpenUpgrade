# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _delete_sql_constraints(env):
    """Delete constraints to recreate it"""
    openupgrade.delete_sql_constraint_safely(
        env, "website_slides_survey", "slide_slide", "check_survey_id"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "website_slides_survey", "slide_slide", "check_certification_preview"
    )


def _fast_fill_name_on_slide_slide(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE slide_slide
        ADD COLUMN IF NOT EXISTS name VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE slide_slide slide
            SET name = survey.title
        FROM survey_survey survey
        WHERE slide.name IS NULL AND slide.survey_id = survey.id
        """,
    )


def _set_is_preview_on_slide_slide_for_certification(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE slide_slide
        SET is_preview = false
        WHERE slide_category = 'certification'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _delete_sql_constraints(env)
    _fast_fill_name_on_slide_slide(env)
    _set_is_preview_on_slide_slide_for_certification(env)
