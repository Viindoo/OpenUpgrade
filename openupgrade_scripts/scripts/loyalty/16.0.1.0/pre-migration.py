from openupgradelib import openupgrade

_model_renames = [
    ("coupon.coupon", "loyalty.card"),
    ("coupon.program", "loyalty.program"),
    ("coupon.reward", "loyalty.reward"),
    ("coupon.rule", "loyalty.rule"),
]

_table_renameds = [
    ("coupon_coupon", "loyalty_card"),
    ("coupon_program", "loyalty_program"),
    ("coupon_reward", "loyalty_reward"),
    ("coupon_rule", "loyalty_rule"),
]

_field_renames = [
    (
        "loyalty.program",
        "loyalty_program",
        "promo_applicability",
        "applies_on",
    ),
    (
        "loyalty.program",
        "loyalty_program",
        "max_usage",
        "maximum_use_number",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "reward_description",
        "description",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "discount_percentage",
        "discount",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "discount_apply_on",
        "discount_applicability",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "discount_type",
        "discount_mode",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "discount_specific_product_ids",
        "discount_product_ids",
    ),
    (
        "loyalty.reward",
        "loyalty_reward",
        "reward_product_quantity",
        "reward_product_qty",
    ),
    (
        "loyalty.rule",
        "loyalty_rule",
        "rule_minimum_amount",
        "minimum_amount",
    ),
    (
        "loyalty.rule",
        "loyalty_rule",
        "rule_minimum_amount_tax_inclusion",
        "minimum_amount_tax_mode",
    ),
    (
        "loyalty.rule",
        "loyalty_rule",
        "rule_min_quantity",
        "minimum_qty",
    ),
    (
        "loyalty.rule",
        "loyalty_rule",
        "rule_products_domain",
        "product_domain",
    ),
]

_xmlid_renames = [
    ("sale_gift_card.mail_template_gift_card", "loyalty.mail_template_gift_card"),
    ("gift_card.gift_card_product_50", "loyalty.gift_card_product_50"),
]


def _rename_models(env):
    openupgrade.rename_models(env.cr, _model_renames)


def _rename_tables(env):
    openupgrade.rename_tables(env.cr, _table_renameds)


def _rename_fields(env):
    openupgrade.rename_fields(env, _field_renames)


# =========================== Card ==============================


def _fill_loyalty_card_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
          ADD COLUMN IF NOT EXISTS company_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_card card
           SET company_id = program.company_id
        FROM loyalty_program program
        WHERE program.id = card.program_id""",
    )


def _fill_loyalty_card_expiration_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
          ADD COLUMN IF NOT EXISTS expiration_date DATE""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_card card
            SET expiration_date =
            (card.create_date::date + INTERVAL '1 day' * program.validity_duration)::date
        FROM loyalty_program program
        WHERE program.validity_duration > 0 AND program.id = card.program_id
        """,
    )


# ========================= Program ==============================
def _map_loyalty_program_program_type(env):
    # 1. if reward_product_id is not null then program_type = 'buy_x_get_y'
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program program
           SET program_type = 'buy_x_get_y'
        FROM loyalty_reward reward
        WHERE reward.reward_product_id IS NOT NULL AND program.reward_id = reward.id
        """,
    )
    # 2. if promo_applicability = 'on_next_order' then program_type = 'next_order_coupons'
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
           SET program_type = 'next_order_coupons'
        WHERE promo_applicability = 'on_next_order'
        """,
    )
    # 3. if promo_code_usage = 'code_needed' then program_type = 'promo_code'
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
           SET program_type = 'promo_code'
        WHERE promo_code_usage = 'code_needed'
        """,
    )


def _fill_loyalty_program_applies_on(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
           SET applies_on = CASE
            WHEN program_type IN ('coupons', 'promotion', 'promo_code', 'buy_x_get_y')
                THEN 'current'
            WHEN program_type IN ('gift_card', 'ewallet', 'next_order_coupons')
                THEN 'future'
            WHEN program_type = 'loyalty' THEN 'both'
           END
        WHERE applies_on IN (
            'coupons', 'promotion', 'gift_card', 'loyalty', 'ewallet', 'promo_code',
            'buy_x_get_y', 'next_order_coupons'
        )
        """,
    )


def _fill_loyalty_program_trigger(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
          ADD COLUMN IF NOT EXISTS trigger CHARACTER VARYING""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
           SET trigger = CASE
               WHEN program_type IN ('coupons', 'promo_code') THEN 'with_code'
               ELSE 'auto'
           END
        WHERE program_type in (
            'coupons', 'promotion', 'gift_card', 'loyalty', 'ewallet', 'promo_code',
            'buy_x_get_y', 'next_order_coupons'
        )
        """,
    )


def _fill_loyalty_program_currency_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
          ADD COLUMN IF NOT EXISTS currency_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program program
            SET currency_id = company.currency_id
        FROM res_company company
        WHERE program.company_id = company.id""",
    )


def _fill_loyalty_program_date_to(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
          ADD COLUMN IF NOT EXISTS date_to DATE""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program program
            SET date_to = rule.rule_date_to::date
        FROM loyalty_rule rule
        WHERE rule.rule_date_to IS NOT NULL AND program.rule_id = rule.id
        """,
    )


# ========================= Reward ==============================
def _fill_loyalty_reward_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
          ADD COLUMN IF NOT EXISTS company_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward reward
            SET company_id = program.company_id
        FROM loyalty_program program
        WHERE reward.program_id = program.id""",
    )


def _fill_loyalty_reward_program_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
          ADD COLUMN IF NOT EXISTS program_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward reward
            SET program_id = prog.reward_id
        FROM loyalty_program prog
        WHERE reward.id = prog.reward_id
        """,
    )


def _fill_loyalty_discount_applicability(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
           SET discount_applicability = CASE
            WHEN discount_applicability = 'specific_products' THEN 'specific'
            WHEN discount_applicability = 'cheapest_product' THEN 'cheapest'
            ELSE 'order'
           END
        WHERE discount_applicability IN (
            'on_order', 'specific_products', 'cheapest_product'
        )
        """,
    )


def _map_loyalty_reward_discount_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
           SET discount_mode = CASE
            WHEN discount_mode = 'fixed_amount' THEN 'per_point'
            ELSE 'percent'
           END
        WHERE discount_mode IN ('fixed_amount', 'percentage')
        """,
    )


# =========================== Rule ==============================


def _fill_loyalty_rule_code(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
          ADD COLUMN IF NOT EXISTS code CHARACTER VARYING""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule rule
            SET code = program.promo_code
        FROM loyalty_program program
        WHERE program.promo_code IS NOT NULL AND program.id = rule.program_id
        """,
    )


def _fill_loyalty_rule_program_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
          ADD COLUMN IF NOT EXISTS program_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule rule
            SET program_id = prog.rule_id
        FROM loyalty_program prog
        WHERE rule.id = prog.rule_id
        """,
    )


def _fill_loyalty_rule_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
          ADD COLUMN IF NOT EXISTS company_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule rule
           SET company_id = program.company_id
        FROM loyalty_program program
        WHERE rule.program_id = program.id""",
    )


def _fill_loyalty_rule_minimum_amount_tax_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
           SET minimum_amount_tax_mode = CASE
            WHEN minimum_amount_tax_mode = 'tax_excluded' THEN 'excl'
            ELSE 'incl'
           END
        WHERE minimum_amount_tax_mode IN ('tax_included', 'tax_excluded')
        """,
    )


def _fill_loyalty_rule_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
          ADD COLUMN IF NOT EXISTS mode CHARACTER VARYING""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule rule
            SET code = CASE
               WHEN program.promo_code IS NOT NULL THEN 'with_code'
               ELSE 'auto'
            END
        FROM loyalty_program program
        WHERE program.id = rule.program_id
        """,
    )


def _fill_loyalty_rule_reward_point_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
          ADD COLUMN IF NOT EXISTS reward_point_mode CHARACTER VARYING
      DEFAULT 'order'""",
    )


# =============================== Migrate ===============================


@openupgrade.migrate()
def migrate(env, version):
    _rename_models(env)
    _rename_tables(env)

    _map_loyalty_program_program_type(env)
    _rename_fields(env)

    _fill_loyalty_rule_program_id(env)
    _fill_loyalty_reward_program_id(env)

    _fill_loyalty_program_applies_on(env)
    _fill_loyalty_program_trigger(env)
    _fill_loyalty_program_currency_id(env)
    _fill_loyalty_program_date_to(env)

    _fill_loyalty_card_company_id(env)
    _fill_loyalty_card_expiration_date(env)

    _fill_loyalty_reward_company_id(env)
    _fill_loyalty_discount_applicability(env)
    _map_loyalty_reward_discount_mode(env)
    _fill_loyalty_rule_code(env)
    _fill_loyalty_rule_minimum_amount_tax_mode(env)
    _fill_loyalty_rule_company_id(env)
    _fill_loyalty_rule_mode(env)
    _fill_loyalty_rule_reward_point_mode(env)

    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "loyalty",
        [
            "gift_card_product_50",
        ],
        False,
    )
