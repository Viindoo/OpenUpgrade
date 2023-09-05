import itertools

from openupgradelib import openupgrade

from odoo.fields import _String
from odoo.tools.translate import _get_translation_upgrade_queries


def _convert_db_column(self, model, column):
    _String._convert_db_column._original_method(self, model, column)
    # update all translatable fields
    # specialized implementation for converting from/to translated fields
    if self.translate or column["udt_name"] == "jsonb":
        for query in itertools.chain.from_iterable(
            _get_translation_upgrade_queries(model._cr, self)
        ):
            openupgrade.logged_query(model._cr, query)


_convert_db_column._original_method = _String._convert_db_column
_String._convert_db_column = _convert_db_column
