from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # rating_text is stored computed from rating (>= 5 top, >= 3 ok, >= 1 ko).
    # Mapping the 14.0 keys carries over values stored by older versions with
    # other thresholds (a rating of 2 kept 'not_satisfied', 15.0 computes 'ko'),
    # and the mapping was keyed 'not satisfied', leaving those rows with a key
    # 15.0 does not know. Store what 15.0 computes.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE rating_rating
        SET rating_text = CASE
            WHEN rating >= 5 THEN 'top'
            WHEN rating >= 3 THEN 'ok'
            WHEN rating >= 1 THEN 'ko'
            ELSE 'none' END
        """,
    )
