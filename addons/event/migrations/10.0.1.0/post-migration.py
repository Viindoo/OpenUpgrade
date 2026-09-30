# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'event', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
    # noupdate in 9.0, removed from the data in 10.0 (the attendee emails are
    # the event.mail schedulers of the event now): the update keeps it, and it
    # reads event fields removed since (event.event.reply_to in 15.0)
    openupgrade.delete_records_safely_by_xml_id(env, ['event.event_thanks'])
