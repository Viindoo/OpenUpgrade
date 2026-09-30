# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

from odoo import Command

_logger = logging.getLogger(__name__)


def _checkout_lang(env, company):
    """The language the buyers of the company see the checkout in.

    The default language of its first website (in SQL: payment_custom is
    migrated before the website module is loaded), else the company's one.
    """
    if openupgrade.table_exists(env.cr, "website"):
        env.cr.execute(
            """SELECT l.code FROM website w
            JOIN res_lang l ON l.id = w.default_lang_id
            WHERE w.company_id = %s ORDER BY w.sequence, w.id LIMIT 1""",
            (company.id,),
        )
        row = env.cr.fetchone()
        if row:
            return row[0]
    return company.partner_id.lang or env.lang or "en_US"


def _split_custom_providers_methods(env):
    """Give each custom provider of a company but one a payment method of its own.

    Up to 16.0 the checkout lists the providers: a company can offer several
    custom ones (a bank transfer, cash at the counter, a phone card...), each
    under its own name with its own payment instructions. From 17.0 the checkout
    lists payment methods, each with one of its providers: on the single wire
    transfer method, the custom providers of a company show as one option, with
    the instructions of one of them. The provider of the module data (or else the
    first one) keeps the wire transfer method; each other one gets a copy of it,
    named as the provider was on the checkout. The copies keep the code
    'wire_transfer': enabling the provider again activates its method.
    """
    wire_transfer = env.ref("payment_custom.payment_method_wire_transfer")
    standard = env.ref("payment.payment_provider_transfer", raise_if_not_found=False)
    providers = (
        env["payment.provider"]
        .with_context(active_test=False)
        .search([("code", "=", "custom")], order="sequence, id")
    )
    for company in providers.company_id:
        company_providers = providers.filtered_domain([("company_id", "=", company.id)])
        if len(company_providers) < 2:
            continue
        keep = standard if standard in company_providers else company_providers[:1]
        lang = _checkout_lang(env, company)
        for provider in company_providers - keep:
            method = wire_transfer.copy(
                {
                    "name": provider.with_context(lang=lang).name,
                    "active": True,
                    "provider_ids": [Command.set(provider.ids)],
                }
            )
            provider.payment_method_ids = [Command.set(method.ids)]
            _logger.info(
                "custom payment provider %s: payment method %s (%s) of its own",
                provider.id,
                method.id,
                method.name,
            )


@openupgrade.migrate()
def migrate(env, version):
    # Instead of loading noupdate_changes we apply method_ids on all payment.provider
    # with custom code (since in multi-company scenario, they can get duplicated)
    env["payment.provider"].search([("code", "=", "custom")]).write(
        {
            "payment_method_ids": [
                Command.set([env.ref("payment_custom.payment_method_wire_transfer").id])
            ],
        }
    )
    _split_custom_providers_methods(env)
