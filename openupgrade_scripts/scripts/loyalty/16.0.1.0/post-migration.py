from openupgradelib import openupgrade


def _move_gift_cart_to_loyalty_card(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
            ADD COLUMN IF NOT EXISTS old_gift_card_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH inserted_loyalty_program AS (
            INSERT INTO loyalty_program (
                company_id,
                currency_id,
                name,
                program_type,
                applies_on,
                trigger,
                portal_visible
            )
            SELECT
                DISTINCT(card.company_id),
                company.currency_id,
                jsonb_object_agg('en_US', 'Gift Cards'),
                'gift_card',
                'future',
                'auto',
                true
            FROM gift_card card
            JOIN res_company company ON company.id = card.company_id
            GROUP BY card.company_id, company.currency_id
            RETURNING id, company_id
        )
        INSERT INTO loyalty_card (
            old_gift_card_id,
            program_id,
            company_id,
            partner_id,
            code,
            expiration_date,
            points,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT
            card.id,
            program.id,
            card.company_id,
            card.partner_id,
            card.code,
            card.expired_date,
            card.initial_amount,
            card.create_uid,
            card.create_date,
            card.write_uid,
            card.write_date
        FROM gift_card card
        JOIN inserted_loyalty_program program ON program.company_id = card.company_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_gift_cart_to_loyalty_card(env)
