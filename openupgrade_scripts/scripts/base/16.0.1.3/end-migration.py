import itertools

from openupgradelib import openupgrade

from odoo import tools
from odoo.tools.translate import _get_translation_upgrade_queries


def _migrate_translations_to_jsonb(env):
    # In Odoo 16, translated fields no longer use the model ir.translation.
    # Instead they store all their values into jsonb columns
    # in the model's table.
    # See https://github.com/odoo/odoo/pull/97692 for more details.
    # Odoo provides a method _get_translation_upgrade_queries returning queries
    # to execute to migrate all the translations of a particular field.
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_translation
        WHERE (src IS NULL OR src = '') AND (value IS NULL OR value = '')
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_translation
            SET value = src
        WHERE value IS NULL OR value = ''
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_translation
            SET state = 'translated'
        WHERE state != 'translated'
        """,
    )
    openupgrade.rename_tables(env.cr, [("ir_translation", "_ir_translation")])
    # update all translatable fields
    # specialized implementation for converting from/to translated fields

    for model_name in env.registry.models.keys():
        if (
            model_name not in env
            or not env[model_name]._auto
            or not env[model_name]._fields
        ):
            continue

        all_columns = tools.table_columns(env.cr, env[model_name]._table)

        for field in sorted(
            env[model_name]._fields.values(), key=lambda f: f.column_order
        ):
            if not field.translate:
                continue

            column = all_columns.get(field.name)
            if not column or column["udt_name"] != "jsonb":
                continue

            for query in itertools.chain.from_iterable(
                _get_translation_upgrade_queries(env.cr, field)
            ):
                # We want to take the translation value instead
                query = query.replace(
                    't.value || m."%s"' % field.name,
                    'm."%s" || t.value' % field.name,
                )
                openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    """Call disable_invalid_filters in every edition of openupgrade"""
    _migrate_translations_to_jsonb(env)
    openupgrade.disable_invalid_filters(env)
