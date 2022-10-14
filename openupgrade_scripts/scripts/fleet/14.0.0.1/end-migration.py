from openupgradelib import openupgrade


def _check_viin_fleet_installed(env):
    env.cr.execute("""
    SELECT *
    FROM ir_module_module
    WHERE name = 'viin_fleet'
        AND ir_module_module.state = 'installed';
    """
    )
    modules = env.cr.fetchone()
    if modules:
        return True
    return False


def _move_price_unit_from_fuel_to_service(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE fleet_vehicle_log_services s
        SET quantity = f.liter,
            price_unit = f.price_per_liter
        FROM fleet_vehicle_log_fuel f
        WHERE s.cost_id = f.cost_id and s.amount <> 0;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    if _check_viin_fleet_installed(env):
        _move_price_unit_from_fuel_to_service(env)
