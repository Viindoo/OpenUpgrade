from openupgradelib import openupgrade
from openupgradelib.openupgrade_160 import convert_string_bootstrap_4to5
from psycopg2.extras import Json


def boostrap_5_migration(env):
    """Convert customized blog content to Bootstrap 5."""
    # Find views to convert
    env.cr.execute(
        """
        SELECT p.id, p.content
        FROM blog_post p
        """
    )
    for id_, content_ in env.cr.fetchall():
        new_content = {
            lang: convert_string_bootstrap_4to5(content)
            for lang, content in content_.items()
        }
        if new_content != content_:
            query = "UPDATE blog_post SET content = %s WHERE id = %s"
            query = env.cr.mogrify(query, [Json(new_content), id_]).decode()
            openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    boostrap_5_migration(env)
