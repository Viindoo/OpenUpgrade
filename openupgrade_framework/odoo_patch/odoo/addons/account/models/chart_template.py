# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account.models.chart_template import AccountChartTemplate


def ref(self, xmlid, raise_if_not_found=True):
    """Don't raise if record is not found which are common during migration."""
    return AccountChartTemplate.ref._original_method(
        self, xmlid, raise_if_not_found=False
    )


ref._original_method = AccountChartTemplate.ref
AccountChartTemplate.ref = ref
