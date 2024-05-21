# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_tag
            ALTER COLUMN color TYPE VARCHAR USING color::VARCHAR;
        UPDATE product_tag SET color = '#3C3C3C';
        """,
    )
