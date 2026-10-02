# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()
def _recompute_slide_slide_type(env):
    """Recompute the field by calling its compute method.

    Archived slides are included: their column still holds the 15.0 values.
    """
    slides = env["slide.slide"].with_context(active_test=False).search([])
    slides._compute_slide_type()


def _fill_values_on_slide_slide(env):
    slides = env["slide.slide"].with_context(active_test=False).search([])
    slides._compute_slides_statistics()


def _fill_nbr_article_on_slide_channel(env):
    env["slide.channel"].with_context(active_test=False).search(
        []
    )._compute_slides_statistics()


@openupgrade.migrate()
def migrate(env, version):
    _recompute_slide_slide_type(env)
    _fill_values_on_slide_slide(env)
    _fill_nbr_article_on_slide_channel(env)
