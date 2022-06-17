# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com>
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools.translate import _


def fill_fleet_vehicle_log_contract_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_contract as fvlc
        SET
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            cost_subtype_id = fvc.cost_subtype_id,
            company_id = fvc.company_id,
            date = fvc.date
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvlc.cost_id
        """,
    )


def fill_fleet_vehicle_log_services_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            fleet_vehicle_log_services as fvls
        SET
            vehicle_id = fvc.vehicle_id,
            amount = fvc.amount,
            company_id = fvc.company_id,
            odometer_id = fvc.odometer_id,
            description = fvc.description,
            date = fvc.date,
            service_type_id = fvc.cost_subtype_id
        FROM
            fleet_vehicle_cost as fvc
        WHERE
            fvc.id =  fvls.cost_id
        """,
    )


def map_fleet_vehicle_log_contract_state(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("diesoon", "open")],
        table="fleet_vehicle_log_contract",
    )


def delete_domain_from_view(env):
    view = env.ref("fleet.fleet_vehicle_service_types_action")
    view.domain = None


def recompute_fleet_vehicle_log_contract_name(env):
    contracts = (
        env["fleet.vehicle.log.contract"].with_context(active_test=False).search([])
    )
    contracts._compute_contract_name()


def _move_data_from_cost_to_service(env):
    other_service_type_id = None
    env.cr.execute("""
    SELECT *
    FROM fleet_vehicle_cost c
    WHERE c.cost_type = 'other' AND c.cost_subtype_id IS NULL;
    """
    )
    if env.cr.fetchone():
        other_service_type_id = env['fleet.service.type'].create({
            'name': _('Other'),
            'category': 'service'
        }).id
    openupgrade.logged_query(
        env.cr,"""
        INSERT INTO fleet_vehicle_log_services (cost_id, vehicle_id, amount, date, description, create_uid, create_date,
        write_uid, write_date, active, service_type_id, odometer_id, company_id, state)
        SELECT id, vehicle_id, amount, date, description, create_uid, create_date, write_uid, write_date, True, COALESCE(cost_subtype_id, %(type_id)s),
        odometer_id, company_id, 'todo'
        FROM fleet_vehicle_cost c
        WHERE c.cost_type = 'other';
        """, {
            "type_id": other_service_type_id,
        })

def _move_data_from_fuel_to_service(env):
    fuel_service_type_id = None
    env.cr.execute("""
    SELECT *
    FROM fleet_vehicle_cost c join fleet_vehicle_log_fuel f ON c.id = f.cost_id
    WHERE c.cost_subtype_id IS NULL;
    """
    )
    if env.cr.fetchone():
        fuel_service_type_id = env['fleet.service.type'].create({
            'name': _('Refueling'),
            'category': 'service'
        }).id
    openupgrade.logged_query(
        env.cr,"""
        INSERT INTO fleet_vehicle_log_services (cost_id, vehicle_id, amount, date, description, create_uid, create_date,
            write_uid, write_date, active, service_type_id, odometer_id, company_id, state)
        SELECT c.id, c.vehicle_id, c.amount, c.date, c.description, c.create_uid, c.create_date, c.write_uid, c.write_date, True, COALESCE(c.cost_subtype_id, %(type_id)s),
         c.odometer_id, c.company_id, 'todo'
        FROM fleet_vehicle_cost c join fleet_vehicle_log_fuel f ON c.id = f.cost_id
        """, {
            "type_id": fuel_service_type_id,
        })


def set_module_viin_fleet_to_install(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to install'
        WHERE name = 'viin_fleet' AND state='uninstalled'
        """
    )

@openupgrade.migrate()
def migrate(env, version):
    fill_fleet_vehicle_log_contract_fields(env)
    fill_fleet_vehicle_log_services_fields(env)
    map_fleet_vehicle_log_contract_state(env)
    delete_domain_from_view(env)
    openupgrade.load_data(env.cr, "fleet", "14.0.0.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "fleet.fleet_rule_cost_visibility_manager",
            "fleet.fleet_rule_cost_visibility_user",
            "fleet.fleet_rule_fuel_log_visibility_manager",
            "fleet.fleet_rule_fuel_log_visibility_user",
            "fleet.ir_rule_fleet_cost",
            "fleet.ir_rule_fleet_log_fuel",
        ],
    )
    recompute_fleet_vehicle_log_contract_name(env)

    # Move data from fleet_vehicle_cost and fleet_vehicle_log_fuel to fleet_vehicle_log_services
    _move_data_from_cost_to_service(env)
    _move_data_from_fuel_to_service(env)

    # Install viin_fleet module
    set_module_viin_fleet_to_install(env)
