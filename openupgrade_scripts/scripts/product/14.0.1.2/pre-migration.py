# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_empty_discount_policy(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_pricelist
        SET discount_policy = 'with_discount'
        WHERE discount_policy is null
        """,
    )


def copy_date_end_date_start_columns(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "product_pricelist_item": [
                ("date_end", None, None),
                ("date_start", None, None),
            ]
        },
    )


def delete_orphan_attribute_line_value_rels(env):
    # Databases upgraded from older versions have no foreign key from this relation
    # to product_template_attribute_line (only the value side has one), so rows of
    # deleted attribute lines stayed behind. 14.0 adds that foreign key and dies on
    # them:
    #   Key (product_template_attribute_line_id)=(450) is not present in table
    #   "product_template_attribute_line".
    # The lines are gone: the rows point at nothing.
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM product_attribute_value_product_template_attribute_line_rel rel
        WHERE NOT EXISTS (
            SELECT 1 FROM product_template_attribute_line ptal
            WHERE ptal.id = rel.product_template_attribute_line_id)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_empty_discount_policy(env)
    copy_date_end_date_start_columns(env)
    delete_orphan_attribute_line_value_rels(env)
