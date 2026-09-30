# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_survey_user_input_line_answer_type(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("answer_type"),
        "answer_type",
        [("text", "char_box"), ("number", "numerical_box"), ("free_text", "text_box")],
        table="survey_user_input_line",
    )


def map_survey_question_question_type(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("question_type"),
        "question_type",
        [("textbox", "char_box"), ("free_text", "text_box")],
        table="survey_question",
    )


@openupgrade.migrate()
def migrate(env, version):
    map_survey_user_input_line_answer_type(env)
    map_survey_question_question_type(env)
    openupgrade.load_data(env.cr, "survey", "14.0.3.2/noupdate_changes.xml")
    # cron of 9.0 (noupdate) calling survey.user_input.do_clean_emptys, a method
    # removed in 14.0: databases upgraded before the 10.0 script deleted it still
    # have it, and it would fail at every run
    openupgrade.delete_records_safely_by_xml_id(
        env, ["survey.ir_cron_clean_empty_surveys"]
    )
