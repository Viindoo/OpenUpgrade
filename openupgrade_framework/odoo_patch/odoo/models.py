# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from uuid import uuid4

from odoo.models import BaseModel

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

_logger = logging.getLogger(__name__)

NEED_UPDATED_VIEWS_KEYS = ["website.record_cover"]


def unlink(self):
    """Don't break on unlink of obsolete records
    when called from ir.model::_process_end()

    This only adapts the base unlink method. If overrides of this method
    on individual models give problems, add patches for those as well.
    """
    if not self.env.context.get(MODULE_UNINSTALL_FLAG):
        return BaseModel.unlink._original_method(self)
    savepoint = str(uuid4())
    try:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'SAVEPOINT "%s"' % savepoint
        )
        result = BaseModel.unlink._original_method(self)
        # release it: a savepoint left open per deleted record keeps a
        # transactionid lock until the end of the update, enough to exhaust
        # the lock table of the cluster on a large update
        self.env.cr.execute(  # pylint: disable=sql-injection
            'RELEASE SAVEPOINT "%s"' % savepoint
        )
        return result
    except Exception as e:
        self.env.cr.execute(  # pylint: disable=sql-injection
            'ROLLBACK TO SAVEPOINT "%s"' % savepoint
        )
        self.env.cr.execute(  # pylint: disable=sql-injection
            'RELEASE SAVEPOINT "%s"' % savepoint
        )
        _logger.warning(
            "Could not delete obsolete record with ids %s of model %s: %s",
            self.ids,
            self._name,
            e,
        )
    return False


unlink._original_method = BaseModel.unlink
BaseModel.unlink = unlink


def _load_records(self, data_list, update=False):
    for vals in data_list:
        xml_id = vals.get("xml_id", False)
        original_record = self.env.ref(xml_id, raise_if_not_found=False)
        arch_db = (vals.get("values") or {}).get("arch", False)
        customize_show = (vals.get("values") or {}).get("customize_show", False)
        if (
            xml_id
            and original_record
            and hasattr(original_record, "_name")
            and original_record._name == "ir.ui.view"
        ):
            # Update custom_show because some modules have removed it from the
            # data file. E.g. v15 customize_show = "True" -> v16: removed instead
            # of customize_show = "False"
            if (
                "customize_show" in original_record._fields
                and original_record.customize_show != customize_show
            ):
                customize_show_views = (
                    self.env["ir.ui.view"]
                    .with_context(active_test=False)
                    .search(
                        [
                            ("type", "=", "qweb"),
                            ("key", "=", original_record.key),
                        ]
                    )
                )
                customize_show_views.customize_show = customize_show
            if arch_db and "website_id" in original_record._fields:
                related_records = self.env["ir.ui.view"].search(
                    [
                        ("id", "!=", original_record.id),
                        ("type", "=", "qweb"),
                        ("website_id", "!=", False),
                        ("key", "=", original_record.key),
                        "|",
                        ("key", "in", NEED_UPDATED_VIEWS_KEYS),
                        "&",
                        ("arch_db", "=", original_record.arch_db),
                        ("inherit_id", "!=", False),
                    ]
                )
                for rec in related_records:
                    if not rec.model_data_id and not rec.xml_id:
                        rec.arch_db = arch_db
    return BaseModel._load_records._original_method(self, data_list, update)


_load_records._original_method = BaseModel._load_records
BaseModel._load_records = _load_records
