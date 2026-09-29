# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    # the menu of the forum in the website changes its xml id: renamed, a
    # second "Forum" menu is not created next to the existing one
    ('website_forum.menu_questions', 'website_forum.menu_website_forums'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
