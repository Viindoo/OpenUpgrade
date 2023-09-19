from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5
from psycopg2.extras import Json


def boostrap_5_migration(env):
    """Convert customized website views to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT iuv.id, iuv.arch_db
        FROM ir_ui_view iuv
        WHERE iuv.type = 'qweb'
        """
    )
    for id_, arch_db_ in env.cr.fetchall():
        new_arch = {
            lang: convert_string_bootstrap_4to5(arch_db)
            for lang, arch_db in arch_db_.items()
        }
        if new_arch != arch_db_:
            query = "UPDATE ir_ui_view SET arch_db = %s WHERE id = %s"
            query = env.cr.mogrify(query, [Json(new_arch), id_]).decode()
            openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    boostrap_5_migration(env)
