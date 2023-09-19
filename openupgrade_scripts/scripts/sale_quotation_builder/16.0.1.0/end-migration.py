from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5
from psycopg2.extras import Json


def boostrap_5_migration(env):
    """Convert customized SO template to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT s.id, s.website_description
        FROM sale_order_template s
        """
    )
    for id_, website_description_ in env.cr.fetchall():
        new_website_description = {
            lang: convert_string_bootstrap_4to5(website_description)
            for lang, website_description in website_description_.items()
        }
        if new_website_description != website_description_:
            query = (
                "UPDATE sale_order_template SET website_description = %s WHERE id = %s"
            )
            query = env.cr.mogrify(query, [Json(new_website_description), id_]).decode()
            openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    boostrap_5_migration(env)
