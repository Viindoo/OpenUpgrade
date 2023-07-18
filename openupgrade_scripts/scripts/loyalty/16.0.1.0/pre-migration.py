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

_rename_xmlids = [
    ("sale_gift_card.mail_template_gift_card", "loyalty.mail_template_gift_card"),
    ("gift_card.gift_card_product_50", "loyalty.gift_card_product_50"),
]


def _rename_models(env):
    openupgrade.rename_models(env.cr, _model_renames)


def _rename_tables(env):
    openupgrade.rename_tables(env.cr, _table_renameds)


def _rename_fields(env):
    openupgrade.rename_fields(env, _field_renames)


def _create_column(env):
    # Card
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
        ADD COLUMN IF NOT EXISTS company_id INTEGER"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
        ADD COLUMN IF NOT EXISTS expiration_date DATE"""
    )
    
    # Program
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS currency_id INTEGER"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS trigger CHARACTER VARYING"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS date_to DATE"""
    )
    
    # Reward
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS company_id INTEGER"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS program_id INTEGER
        """,
    )

    # Rule
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS code CHARACTER VARYING"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS company_id INTEGER"""
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS mode CHARACTER VARYING"""
    )


# ============================================ Card ======================================

def _fill_loyalty_card_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as program_id, company_id
            FROM loyalty_program
        )

        UPDATE loyalty_card card
        SET company_id = cte.company_id
        FROM cte
        WHERE cte.program_id = card.program_id"""
    )


def _fill_loyalty_card_expiration_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as program_id, validity_duration
            FROM loyalty_program
        )

        UPDATE loyalty_card card
        SET expiration_date = CASE
            WHEN  cte.validity_duration > 0
                THEN card.create_date.date + card.validity_duration
            ELSE 0
            END
        FROM cte
        WHERE cte.program_id = card.program_id"""
    )

# ============================================ Program ======================================

def _fill_loyalty_program_applies_on(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET applies_on = CASE
            WHEN applies_on = 'on_current_order' THEN 'current'
            WHEN applies_on = 'on_next_order' THEN 'future'
            ELSE 'both'
            END"""
    )


def _fill_loyalty_program_currency_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as company_id, currency_id
            FROM res_company
        )

        UPDATE loyalty_program program
        SET currency_id = CASE
            WHEN cte.currency_id IS NOT NULL THEN cte.currency_id
            ELSE NULL
            END
        WHERE program.company_id = cte.company_id"""
    )


def _fill_loyalty_program_date_to(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as rule_id, rule_date_to
            FROM loyalty_rule
        )

        UPDATE loyalty_program program
        SET date_to = cte.rule_date_to.date
        WHERE program.rule_id = cte.rule_id"""
    )


def _fill_loyalty_program_program_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET program_type = 'promotion'
        WHERE program_type IS NULL"""
    )


def _fill_loyalty_program_trigger(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET trigger = CASE
            WHEN program_type = 'coupon' THEN 'with_code'
            ELSE 'auto'
            END"""
    )


# ============================= Reward ==============================


def _fill_loyalty_reward_company_id(env):
    """
        This function needs to run after the program_id column has a value
    """
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as program_id, company_id
            FROM loyalty_program
        )

        UPDATE loyalty_reward reward
        SET company_id = cte.company_id
        FROM cte
        WHERE reward.program_id = cte.program_id"""
    )


def _fill_loyalty_reward_program_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        SELECT reward_id
        FROM loyalty_program
        GROUP BY reward_id
        HAVING COUNT(*)>1
        """,
    )

    for i in env.cr.fetchall():
        openupgrade.logged_query(
            env.cr,
            """
            SELECT id,reward_id
            FROM loyalty_program
            WHERE reward_id = %s
            """,
            (i['reward_id'],),
        )

        for index, row in enumerate(env.cr.fetchall()):
            if row == 0:
                openupgrade.logged_query(
                    env.cr,
                    """
                    UPDATE loyalty_reward
                    SET program_id = %s
                    WHERE id = %s
                    """,
                    (row[index]['id'], row[index]['program_id'],),
                )
            else:
                openupgrade.logged_query(
                    env.cr,
                    """
                    INSERT INTO loyalty_reward (description, reward_type, reward_product_id, reward_product_qty,
                    discount_mode, discount, discount_applicability, discount_max_amount, discount_line_product_id)

                    SELECT description, reward_type, reward_product_id, reward_product_qty,
                    discount_mode, discount, discount_applicability, discount_max_amount, discount_line_product_id
                    FROM loyalty_reward
                    WHERE id = %s
                    RETURNING id;
                    """,
                    (row[index]['reward_id'],),
                )

                new_row_id = env.cr.fetchall()[0][0]

                openupgrade.logged_query(
                    env.cr,
                    """
                    UPDATE loyalty_reward
                    SET program_id = %s
                    WHERE id = %s
                    """,
                    (row[index]['id'], new_row_id,),
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
            END"""
    )


def _fill_loyalty_discount_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET discount_mode = CASE
            WHEN discount_mode = 'fixed_amount' THEN 'per_point'
            ELSE 'percent'
            END"""
    )


def _fill_loyalty_reward_type_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET reward_type = 'discount'
        WHERE reward_type IS NULL"""
    )


# ============================= Rule ==============================


def _fill_loyalty_rule_code(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET code = ''"""
    )


def _fill_loyalty_rule_company_id(env):
    """
        This function needs to run after the program_id column has a value
    """
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte AS (
            SELECT id as program_id, company_id
            FROM loyalty_program
        )

        UPDATE loyalty_rule rule
        SET company_id = cte.company_id
        FROM cte
        WHERE rule.program_id = cte.program_id"""
    )


def _fill_loyalty_rule_minimum_amount_tax_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET minimum_amount_tax_mode = CASE
            WHEN minimum_amount_tax_mode = 'tax_excluded' THEN 'excl'
            ELSE 'incl'"""
    )


def _fill_loyalty_rule_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET mode = 'auto'"""
    )

# ====================================== XML IDS ===============================

def _rename_xmlids(env):
    openupgrade.rename_xmlids(cr, _rename_xmlids)


@openupgrade.migrate()
def migrate(env, version):
    _rename_models(env)
    _rename_tables(env)
    _rename_fields(env)
    _create_column(env)
    _fill_loyalty_card_company_id(env)
    _fill_loyalty_card_expiration_date(env)
    _fill_loyalty_program_applies_on(env)
    _fill_loyalty_program_currency_id(env)
    _fill_loyalty_program_date_to(env)
    _fill_loyalty_program_program_type(env)
    _fill_loyalty_program_trigger(env)
    _fill_loyalty_reward_company_id(env)
    _fill_loyalty_reward_program_id(env)
    _fill_loyalty_discount_applicability(env)
    _fill_loyalty_discount_mode(env)
    _fill_loyalty_reward_type_if_null(env)
    _fill_loyalty_rule_code(env)
    _fill_loyalty_rule_company_id(env)
    _fill_loyalty_rule_minimum_amount_tax_mode(env)
    _fill_loyalty_rule_mode(env)
