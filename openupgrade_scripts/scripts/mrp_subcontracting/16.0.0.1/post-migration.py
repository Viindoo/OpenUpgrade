from openupgradelib import openupgrade


def _mrp_production_fill_subcontractor_id(env):
    subcontract_moves = env["stock.move"].search([("is_subcontract", "=", True)])
    for move in subcontract_moves:
        if move.move_orig_ids and move.move_orig_ids.production_id:
            move.move_orig_ids.production_id.write(
                {
                    "subcontractor_id": move.picking_id.partner_id.commercial_partner_id.id,
                }
            )


@openupgrade.migrate()
def migrate(env, version):
    _mrp_production_fill_subcontractor_id(env)
