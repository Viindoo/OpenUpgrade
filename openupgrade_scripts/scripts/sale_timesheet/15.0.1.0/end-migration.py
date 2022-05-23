from openupgradelib import openupgrade


def _sale_order_line_compute_remaining_hours(env):
    # We need to use ORM because compute remaining_hours requires float_round
    env["sale.order.line"].search([])._compute_remaining_hours()


@openupgrade.migrate()
def migrate(env, version):
    _sale_order_line_compute_remaining_hours(env)
