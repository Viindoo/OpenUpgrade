from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5
from psycopg2.extras import Json


def boostrap_5_migration(env):
    """Convert customized forum faq to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT f.id, f.faq
        FROM forum_forum f
        """
    )
    for id_, faq_ in env.cr.fetchall():
        new_faq = {
            lang: convert_string_bootstrap_4to5(faq) for lang, faq in faq_.items()
        }
        if new_faq != faq_:
            query = "UPDATE forum_forum SET faq = %s WHERE id = %s"
            query = env.cr.mogrify(query, [Json(new_faq), id_]).decode()
            openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    boostrap_5_migration(env)
