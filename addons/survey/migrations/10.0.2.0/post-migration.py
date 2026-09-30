# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'survey', 'migrations/10.0.2.0/noupdate_changes.xml',
    )
    # 9.0 ships the cleaning cron in a noupdate block: it would stay and call
    # do_clean_emptys every day next to the ir.autovacuum hook that replaces
    # it in 10.0, then fail once the method is gone (14.0)
    openupgrade.delete_records_safely_by_xml_id(
        env, ['survey.ir_cron_clean_empty_surveys'])
