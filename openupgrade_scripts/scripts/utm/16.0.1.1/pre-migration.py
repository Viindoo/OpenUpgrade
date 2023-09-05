from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # pre-migration of module base converted name column from utm_campaign
    # into jsonb, hence it suffices to copy the name column into title.
    if not openupgrade.column_exists(env.cr, "utm_campaign", "title"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE utm_campaign
            ADD COLUMN IF NOT EXISTS title jsonb;
            """,
        )
        query = """
            WITH t AS (
                SELECT it.res_id as res_id,
                    jsonb_object_agg(it.lang, it.value) AS value,
                    bool_or(imd.noupdate) AS noupdate
                  FROM _ir_translation it
             LEFT JOIN ir_model_data imd
                    ON imd.model = 'utm_campaign' AND imd.res_id = it.res_id
                 WHERE it.type = 'model' AND it.name = 'utm.campaign,name'
                     AND it.state = 'translated'
              GROUP BY it.res_id
            )
            UPDATE utm_campaign m
               SET title = CASE
                   WHEN t.noupdate
                   THEN t.value || jsonb_build_object('en_US', m.name::varchar)
                   ELSE t.value || jsonb_build_object('en_US', m.name::varchar)
                END
              FROM t
             WHERE t.res_id = m.id
        """
        openupgrade.logged_query(env.cr, query)
        openupgrade.logged_query(
            env.cr,
            """UPDATE utm_campaign
               SET title = jsonb_build_object('en_US', name::varchar)
             WHERE title IS NULL
            """,
        )
