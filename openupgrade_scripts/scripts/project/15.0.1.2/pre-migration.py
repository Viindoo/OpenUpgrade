from openupgradelib import openupgrade


def _rename_field_on_filters(cr, model, old_field, new_field):
    # Example of replaced domain: [['field', '=', self], ...]
    # TODO: Rename when the field is part of a submodel (ex. m2one.field)
    cr.execute(
        """
        UPDATE ir_filters
        SET domain = replace(domain, %(old_pattern)s, %(new_pattern)s)
        WHERE model_id = %%s
            AND domain ~ %(old_pattern)s
        """
        % {
            "old_pattern": "'%s'" % old_field,
            "new_pattern": "'%s'" % new_field,
        },
        (model,),
    )
    # Examples of replaced contexts:
    # {'group_by': ['field', 'other_field'], 'other_key':value}
    # {'group_by': ['date_field:month']}
    # {'other_key': value, 'group_by': ['other_field', 'field']}
    # {'group_by': ['other_field'],'col_group_by': ['field']}
    cr.execute(
        r"""
        UPDATE ir_filters
        SET context = regexp_replace(
            context, %(old_pattern)s, %(new_pattern)s
        )
        WHERE model_id = %%s
            AND context ~ %(old_pattern)s
        """
        % {
            "old_pattern": (
                r"""$$('group_by'|'col_group_by'|'graph_groupbys'
                       |'pivot_measures'|'pivot_row_groupby'|'pivot_column_groupby'
                    ):([\s*][^\]]*)"""
                r"'%s(:day|:week|:month|:year){0,1}'(.*?\])$$"
            )
            % old_field,
            "new_pattern": r"$$\1:\2'%s\3'\4$$" % new_field,
        },
        (model,),
    )
    # Examples of replaced contexts:
    # {'graph_measure': 'field'
    cr.execute(
        r"""
        UPDATE ir_filters
        SET context = regexp_replace(
            context, %(old_pattern)s, %(new_pattern)s
        )
        WHERE model_id = %%s
            AND context ~ %(old_pattern)s
        """
        % {
            "old_pattern": (
                r"$$'graph_measure':([\s*])'%s(:day|:week|:month|:year){0,1}'$$"
            )
            % old_field,
            "new_pattern": r"$$'graph_measure':\1'%s\2'$$" % new_field,
        },
        (model,),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE project_project
            ADD COLUMN IF NOT EXISTS last_update_status CHARACTER VARYING;
            UPDATE project_project
            SET last_update_status = 'on_track';
        """,
    )
    _rename_field_on_filters(env.cr, "project.task", "user_id", "user_ids")
