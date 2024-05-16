from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(env, 'uom', 'uom_uom', 'factor_gt_zero')
    openupgrade.delete_sql_constraint_safely(env, 'uom', 'uom_uom', 'factor_reference_is_one')
    openupgrade.delete_sql_constraint_safely(env, 'uom', 'uom_uom', 'rounding_gt_zero')
