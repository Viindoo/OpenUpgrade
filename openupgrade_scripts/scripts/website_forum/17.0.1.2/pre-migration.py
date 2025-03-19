# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("website", "website", "forums_count", "forum_count"),
    ("forum.post", "forum_post", "bump_date", "last_activity_date"),
]


def map_forum_forum_default_order(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE forum_forum
        SET default_order = 'last_activity_date desc'
        WHERE default_order = 'write_date desc'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    map_forum_forum_default_order(env)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE forum_post
        SET last_activity_date = create_date
        WHERE last_activity_date IS NULL
        """,
    )
