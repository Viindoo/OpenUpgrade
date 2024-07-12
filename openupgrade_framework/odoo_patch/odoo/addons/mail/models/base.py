from odoo.tools import groupby

from odoo.addons.base.models.ir_model import IrModelFields
from odoo.addons.mail.models.ir_model_fields import IrModelField as IrModelFieldMail
from odoo.addons.mail.models.models import BaseModel

# TODO: delete this as there is a solution from PR: https://github.com/odoo/odoo/pull/172881


def _mail_track_get_field_sequence(self, field):
    if isinstance(field, IrModelFields):
        sequence = getattr(field, "tracking", getattr(field, "track_sequence", 100))
    else:
        sequence = getattr(
            self._fields[field],
            "tracking",
            getattr(self._fields[field], "track_sequence", 100),
        )
    if sequence is True:
        sequence = 100
    return sequence


def unlink(self):
    tracked = self.filtered("tracking")
    if tracked:
        tracking_values = self.env["mail.tracking.value"].search(
            [("field_id", "in", tracked.ids)]
        )
        field_to_trackings = groupby(tracking_values, lambda track: track.field_id)
        for field, trackings in field_to_trackings:
            self.env["mail.tracking.value"].concat(*trackings).write(
                {
                    "field_info": {
                        "desc": field.field_description,
                        "name": field.name,
                        "sequence": self.env[
                            field.model_id.model
                        ]._mail_track_get_field_sequence(field),
                        "type": field.ttype,
                    }
                }
            )
    return super(IrModelFieldMail, self).unlink()


_mail_track_get_field_sequence._original_method = (
    BaseModel._mail_track_get_field_sequence
)
BaseModel._mail_track_get_field_sequence = _mail_track_get_field_sequence

unlink._original_method = IrModelFieldMail.unlink
IrModelFieldMail.unlink = unlink
