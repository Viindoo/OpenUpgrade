# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from odoo import fields
from odoo.tools import sql

_column_copies = {
    'res_company': [
        ('fiscalyear_last_month', None, None),
    ],
}

_column_renames = {
    'account_move_line': [
        ('user_type_id', None),
    ],
    'account_journal': [
        ('post_at_bank_rec', None),
        ('update_posted', None),
    ],
    'account_reconcile_model': [
        ('second_tax_id', None),
        ('tax_id', None),
    ],
    'account_reconcile_model_template': [
        ('second_tax_id', None),
        ('tax_id', None),
    ],
    'res_company': [
        ('invoice_reference_type', None),
    ],
}

_field_renames = [
    ('account.move', 'account_move', 'amount', 'amount_total'),
]

_field_sale_renames = [
    ('res.company', 'res_company', 'sale_note', 'invoice_terms'),
    ('res.config.settings', 'res_config_settings',
     'use_sale_note', 'use_invoice_terms'),
]

_model_renames = [
    ('account.register.payments', 'account.payment.register'),
]

_table_renames = [
    ('account_register_payments', 'account_payment_register'),
    ('account_analytic_tag_account_reconcile_model_rel',
     'account_reconcile_model_analytic_tag_rel'),
    ('account_invoice_payment_rel', 'old_account_invoice_payment_rel'),
]

_field_adds = [
    ("account_root_id", "account.move.line", "account_move_line", "many2one", False, "account"),
    ("tax_group_id", "account.move.line", "account_move_line", "many2one", False, "account")
]

xmlid_renames_payment_terms = [
    ("account.account_payment_term_net", "account.account_payment_term_30days"),
]


def type_change_account_fiscal_position_zips(env):
    tables = ['account_fiscal_position', 'account_fiscal_position_template']
    zip_fields = ['zip_from', 'zip_to']
    for table in tables:
        for field in zip_fields:
            openupgrade.logged_query(
                env.cr,
                "ALTER TABLE %(table)s "
                "ALTER COLUMN %(field)s "
                "TYPE varchar" % {
                    'table': table,
                    'field': field,
                })
        openupgrade.logged_query(
            env.cr,
            "UPDATE %(table)s "
            "SET zip_from = NULL, zip_to = NULL "
            "WHERE zip_from = '0' AND zip_to = '0'" % {
                'table': table,
            })


def create_account_invoice_amount_tax_company_signed(env):
    if not openupgrade.column_exists(
            env.cr, "account_invoice", "amount_tax_company_signed"):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE account_invoice
            ADD COLUMN amount_tax_company_signed numeric"""
        )
        openupgrade.logged_query(
            env.cr, """
            SELECT ai.id, ai.amount_tax, ai.type, ai.currency_id,
                ai.company_id, rc.currency_id, ai.date_invoice
            FROM account_invoice ai
            JOIN res_company rc ON ai.company_id = rc.id
            WHERE ai.amount_tax != 0.0"""
        )
        for _id, tax, inv_type, curr, company, company_curr, date in \
                env.cr.fetchall():
            company_tax = tax
            if curr != company_curr:
                curr_ = env["res.currency"].browse(curr)
                company_curr_ = env["res.currency"].browse(company_curr)
                company_ = env["res.company"].browse(company)
                company_tax = curr_._convert(
                    company_tax, company_curr_, company_,
                    date or fields.Date.today())
            sign = inv_type in ['in_refund', 'out_refund'] and -1 or 1
            company_tax = company_tax * sign
            env.cr.execute(
                """UPDATE account_invoice
                SET amount_tax_company_signed = %s WHERE id = %s""",
                (company_tax, _id),
            )
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_invoice
            SET amount_tax_company_signed = 0.0
            WHERE amount_tax_company_signed IS NULL""",
        )


def create_account_move_new_columns(env):
    """Faster way, avoid compute"""
    data = {
        'account_move': [
            ('amount_total_signed', 'numeric'),
            ('amount_untaxed', 'numeric'),
            ('amount_untaxed_signed', 'numeric'),
            ('amount_tax', 'numeric'),
            ('amount_tax_signed', 'numeric'),
            ('amount_residual', 'numeric'),
            ('amount_residual_signed', 'numeric'),
            ('invoice_payment_state', 'character varying'),
            ('invoice_partner_display_name', 'character varying'),
        ],
        'account_move_line': [
            ('tax_audit', 'character varying'),
        ]
    }
    for table, column_spec_list in data.items():
        for column, column_type in column_spec_list:
            openupgrade.logged_query(
                env.cr, """
                ALTER TABLE {table}
                ADD COLUMN {column} {column_type}""".format(
                    table=table, column=column, column_type=column_type
                ),
            )


# account.account.root_id of 13.0 (_compute_account_root), from the code of
# the account aa
_ACCOUNT_ROOT = """CASE WHEN COALESCE(aa.code, '') = '' THEN NULL
    ELSE ascii(aa.code) * 1000 + ascii(substr(aa.code, 2, 1)) END"""


def fill_account_move_line(env):
    """Faster way: the new columns of the journal items are written in one
    pass, each update of every line costing minutes on a big database
    (makmur: 2 million lines, 4 to 6 minutes each):
    - parent_state, account_internal_type, move_name (stored related fields,
      move_name was filled by the ORM in SQL) and account_root_id (filled by
      the post-migration from account.account.root_id, computed by the ORM
      later in this module: same formula here, the post-migration only fixes
      a line that would differ);
    - sequence and discount, which the ORM filled with their default on every
      line: the columns get it as default when they are added, PostgreSQL
      gives it to the existing rows without writing them, and it is dropped
      at once (the ORM declares none in the database).
    """
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN parent_state varchar,
        ADD COLUMN account_internal_type varchar,
        ADD COLUMN move_name varchar,
        ADD COLUMN sequence integer DEFAULT 10,
        ADD COLUMN discount numeric DEFAULT '0.00'""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ALTER COLUMN sequence DROP DEFAULT,
        ALTER COLUMN discount DROP DEFAULT""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET parent_state = am.state,
            account_internal_type = aat.type,
            move_name = am.name,
            account_root_id = {root}
        FROM account_move am,
            account_account aa,
            account_account_type aat
        WHERE am.id = aml.move_id
            AND aa.user_type_id = aat.id
            AND aml.account_id = aa.id""".format(root=_ACCOUNT_ROOT),
    )
    # the lines the join above leaves out (account without type) get the
    # values the ORM and the post-migration give them
    env.cr.execute("""
        SELECT aa.id FROM account_account aa
        LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
        WHERE aat.id IS NULL""")
    untyped = tuple(r[0] for r in env.cr.fetchall())
    env.cr.execute(
        "SELECT 1 FROM account_move_line WHERE account_id IS NULL LIMIT 1")
    if untyped or env.cr.fetchone():
        openupgrade.logged_query(
            env.cr, """
            UPDATE account_move_line aml
            SET move_name = am.name,
                account_root_id = (SELECT {root} FROM account_account aa
                                   WHERE aa.id = aml.account_id)
            FROM account_move am
            WHERE am.id = aml.move_id
                AND (aml.account_id IS NULL OR aml.account_id IN %s)
            """.format(root=_ACCOUNT_ROOT), (untyped or (0,),),
        )


def create_res_partner_ranks(env):
    """Faster way"""
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner
        ADD COLUMN customer_rank integer
        DEFAULT 0""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner ALTER COLUMN customer_rank DROP DEFAULT""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner
        ADD COLUMN supplier_rank integer
        DEFAULT 0""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE res_partner ALTER COLUMN supplier_rank DROP DEFAULT""",
    )


def delete_fk_constraints(env):
    """Avoid errors on automatic data removal after updating due to dangling
    references on these old columns.
    """
    openupgrade.lift_constraints(env.cr, "account_tax_template", "account_id")
    openupgrade.lift_constraints(env.cr, "account_tax_template", "cash_basis_account")
    openupgrade.lift_constraints(env.cr, "account_tax_template", "refund_account_id")


def fill_account_move_commercial_partner_id(env):
    """Avoid this heavy ORM computation doing it by SQL.

    Why this is not a related field by the way?
    """
    openupgrade.logged_query(env.cr, "ALTER TABLE account_move ADD commercial_partner_id int4")
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move am
        SET commercial_partner_id = rp.commercial_partner_id
        FROM res_partner rp
        WHERE am.partner_id = rp.id"""
    )


def fill_account_move_invoice_partner_bank_id(env):
    """Avoid the ORM computation of this new stored field for every journal
    entry (makmur: 400,091 entries, 11 minutes): when the module is loaded,
    every entry is of type 'entry' (the invoices become entries of their type
    in the post-migration, which also sets the bank account of the invoices),
    so the computed value is the first bank account (sequence, id) of the
    partner of the company of the entry that belongs to that company.
    """
    if openupgrade.column_exists(
            env.cr, "account_move", "invoice_partner_bank_id"):
        return
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ADD invoice_partner_bank_id int4")
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move am
        SET invoice_partner_bank_id = bank.id
        FROM (
            SELECT DISTINCT ON (rc.id) rc.id AS company_id, rpb.id
            FROM res_company rc
            JOIN res_partner_bank rpb ON rpb.partner_id = rc.partner_id
                AND rpb.company_id = rc.id
            ORDER BY rc.id, rpb.sequence, rpb.id
        ) bank
        WHERE am.company_id = bank.company_id"""
    )


def set_account_move_currency_id_required(env):
    # with this, we avoid calling _get_default_currency during the load
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET currency_id = COALESCE(aj.currency_id, rc.currency_id)
        FROM account_journal aj
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE am.journal_id = aj.id AND am.currency_id IS NULL
        """)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move ALTER COLUMN currency_id SET NOT NULL;
        """)


def add_helper_invoice_move_rel(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move
        ADD COLUMN old_invoice_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_invoice_id = ai.id
        FROM account_invoice ai
        WHERE ai.move_id = am.id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_invoice_id = aml.invoice_id
        FROM account_move_line aml
        WHERE aml.move_id = am.id AND am.old_invoice_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice ai
        SET move_id = am.old_invoice_id
        FROM account_move am
        WHERE am.old_invoice_id = ai.id AND ai.move_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_invoice_line_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_invoice_tax_id integer""",
    )
    # Create index for these columns, as they are going to be accessed frequently
    for table, field in [
        ("account_move", "old_invoice_id"),
        ("account_move_line", "old_invoice_line_id"),
        ("account_move_line", "old_invoice_tax_id"),
    ]:
        index_name = '%s_%s_index' % (table, field)
        sql.create_index(env.cr, index_name, table, ['"%s"' % field])


def add_helper_voucher_move_rel(env):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move
        ADD COLUMN old_voucher_id integer""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET old_voucher_id = av.id
        FROM account_voucher av
        WHERE av.move_id = am.id
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE account_move_line
        ADD COLUMN old_voucher_line_id integer""",
    )


def clear_unwanted_currency_id_account_move_line(env):
    """ Clear unwanted 'currency_id' values from 'account.move.line' which is
    duplicated with the 'company_currency_id' values, in order to add the new
    constraint of 'check_amount_currency_balance_sign'.
    """
    openupgrade.logged_query(env.cr, """
        UPDATE account_move_line SET currency_id = NULL
        WHERE currency_id = company_currency_id AND currency_id IS NOT NULL
    """)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    if openupgrade.table_exists(cr, 'sale_order'):
        openupgrade.rename_fields(env, _field_sale_renames)
        # https://github.com/odoo/odoo/commit/ca25a692bd19fdca2b2600f2054eb419aae28999
        openupgrade.logged_query(
            env.cr, """
            UPDATE ir_config_parameter
            SET key = 'account.use_invoice_terms'
            WHERE key = 'sale.use_sale_note'"""
        )
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames_payment_terms)
    openupgrade.add_fields(env, _field_adds)
    type_change_account_fiscal_position_zips(env)
    create_account_invoice_amount_tax_company_signed(env)
    create_account_move_new_columns(env)
    fill_account_move_line(env)
    create_res_partner_ranks(env)
    delete_fk_constraints(env)
    openupgrade.lift_constraints(env.cr, "account_move", "reverse_entry_id")
    fill_account_move_commercial_partner_id(env)
    fill_account_move_invoice_partner_bank_id(env)
    set_account_move_currency_id_required(env)
    add_helper_invoice_move_rel(env)
    clear_unwanted_currency_id_account_move_line(env)
    if openupgrade.table_exists(cr, 'account_voucher'):
        add_helper_voucher_move_rel(env)
