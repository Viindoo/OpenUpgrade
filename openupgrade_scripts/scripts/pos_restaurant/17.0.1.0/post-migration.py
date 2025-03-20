# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _restaurant_floor_convert_restaurant_floor_m2o_to_m2m(env):
    """
    Convert m2o to m2m in 'restaurant.floor'
    """
    openupgrade.m2o_to_x2m(
        env.cr,
        env["restaurant.floor"],
        "restaurant_floor",
        "pos_config_ids",
        "pos_config_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _restaurant_floor_convert_restaurant_floor_m2o_to_m2m(env)
