# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "hr.offboarding_plan",
        "hr.openupgrade_legacy_17_0_offboarding_plan",
    ),
    (
        "hr.onboarding_plan",
        "hr.openupgrade_legacy_17_0_onboarding_plan",
    ),
    (
        "hr.offboarding_setup_compute_out_delais",
        "hr.openupgrade_legacy_17_0_offboarding_setup_compute_out_delais",
    ),
    (
        "hr.offboarding_take_back_hr_materials",
        "hr.openupgrade_legacy_17_0_offboarding_take_back_hr_materials",
    ),
    (
        "hr.onboarding_plan_training",
        "hr.openupgrade_legacy_17_0_onboarding_plan_training",
    ),
    (
        "hr.onboarding_setup_it_materials",
        "hr.openupgrade_legacy_17_0_onboarding_setup_it_materials",
    ),
    (
        "hr.onboarding_training",
        "hr.openupgrade_legacy_17_0_onboarding_training",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
