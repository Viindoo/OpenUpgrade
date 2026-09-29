# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark <http://bloopark.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _replace_transfer_view_template_id(env):
    """The button view of 10.0 is removed. noupdate_changes.xml switches the
    acquirer of the module data to the 11.0 form; the transfer acquirers the
    company created itself still use the removed view, which then cannot be
    deleted (view_template_id is required) and would render the checkout
    button of 10.0: switch them too, as payment_paypal does.
    """
    old_view = env.ref(
        'payment_transfer.transfer_acquirer_button', raise_if_not_found=False)
    new_view = env.ref(
        'payment_transfer.transfer_form', raise_if_not_found=False)
    if not old_view or not new_view:
        return
    openupgrade.logged_query(
        env.cr, """
        UPDATE payment_acquirer
        SET view_template_id = %s
        WHERE view_template_id = %s
        """, (new_view.id, old_view.id),
    )


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.load_data(
        env.cr, 'payment_transfer', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    _replace_transfer_view_template_id(env)
