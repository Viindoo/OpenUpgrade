# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import csv
from openupgradelib import openupgrade
from odoo.addons.openupgrade_records.lib import apriori
from odoo.modules.module import get_module_resource

_column_renames = {
    'res_partner': [
        ('birthdate', None),
    ],
}


def ensure_country_state_id_on_existing_records(cr):
    """Suppose you have country states introduced manually.
    This method ensure you don't have problems later in the migration when
    loading the res.country.state.csv"""
    with open(get_module_resource('base', 'res', 'res.country.state.csv'),
              'rb') as country_states_file:
        states = csv.reader(country_states_file, delimiter=',', quotechar='"')
        for row, state in enumerate(states):
            if row == 0:
                continue
            data_name = state[0]
            country_code = state[1]
            name = state[2]
            state_code = state[3]
            # first: query to ensure the existing odoo countries have
            # the code of the csv file, because maybe some code has changed
            cr.execute(
                """
                UPDATE res_country_state rcs
                SET code = '%(state_code)s'
                FROM ir_model_data imd
                WHERE imd.model = 'res.country.state'
                    AND imd.res_id = rcs.id
                    AND imd.name = '%(data_name)s'
                """ % {
                    'state_code': state_code,
                    'data_name': data_name,
                }
            )
            # second: find if csv record exists in ir_model_data
            cr.execute(
                """
                SELECT imd.id
                FROM ir_model_data imd
                INNER JOIN res_country_state rcs ON (
                    imd.model = 'res.country.state' AND imd.res_id = rcs.id)
                LEFT JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd2 ON (
                    rc.id = imd2.res_id AND imd2.model = 'res.country')
                WHERE imd2.name = '%(country_code)s'
                    AND rcs.code = '%(state_code)s'
                    AND imd.name = '%(data_name)s'
                """ % {
                    'country_code': country_code,
                    'state_code': state_code,
                    'data_name': data_name,
                }
            )
            found_id = cr.fetchone()
            if found_id:
                continue
            # third: as csv record not exists in ir_model_data, search for one
            # introduced manually that has same codes
            cr.execute(
                """
                SELECT imd.id
                FROM ir_model_data imd
                INNER JOIN res_country_state rcs ON (
                    imd.model = 'res.country.state' AND imd.res_id = rcs.id)
                LEFT JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd2 ON (
                    rc.id = imd2.res_id AND imd2.model = 'res.country')
                WHERE imd2.name = '%(country_code)s'
                    AND rcs.code = '%(state_code)s'
                ORDER BY imd.id DESC
                LIMIT 1
                """ % {
                    'country_code': country_code,
                    'state_code': state_code,
                }
            )
            found_id = cr.fetchone()
            if found_id:
                # fourth: if found, ensure it has the same xmlid as the csv
                # record
                openupgrade.logged_query(
                    cr,
                    """
                    UPDATE ir_model_data
                    SET name = '%(data_name)s', module = 'base'
                    WHERE id = %(data_id)s AND model = 'res.country.state'
                    """ % {
                        'data_name': data_name,
                        'data_id': found_id[0],
                    }
                )
                cr.execute(
                    """
                    UPDATE res_country_state rcs
                    SET name = $$%(name)s$$
                    FROM ir_model_data imd
                    WHERE imd.id = %(data_id)s
                        AND imd.model = 'res.country.state'
                        AND imd.res_id = rcs.id
                    """ % {
                        'name': name,
                        'data_id': found_id[0],
                    }
                )
            else:
                # if res.country.state was created by hand via Odoo web
                # interface, it won't have any ir_model_data entry
                # -> we create one.
                cr.execute(
                    """
                    SELECT rcs.id
                    FROM res_country_state rcs
                    LEFT JOIN res_country rc ON rc.id=rcs.country_id
                    WHERE rcs.code='%(state_code)s'
                    AND rc.code = '%(country_code)s'
                    LIMIT 1
                    """ % {
                        'country_code': country_code.upper(),
                        'state_code': state_code.upper(),
                    }
                )
                found_id = cr.fetchone()
                if found_id:
                    openupgrade.add_xmlid(
                        cr, 'base', state[0], 'res.country.state', found_id)
        # fifth: search for duplicates, just in case, due to new constraint
        cr.execute(
            """
            SELECT imd.id, imd.name, rcs.code
            FROM ir_model_data imd
            INNER JOIN res_country_state rcs ON (
                imd.model = 'res.country.state' AND imd.res_id = rcs.id)
            ORDER BY imd.id DESC
            """
        )
        rows = []
        for row in cr.fetchall():
            if row in rows:
                # rename old duplicated entries that post-migration will merge
                openupgrade.logged_query(
                    cr,
                    """
                    UPDATE ir_model_data
                    SET name = $$%(data_name)s$$ || '_old_' || res_id
                    WHERE id = %(data_id)s AND model = 'res.country.state'
                    """ % {
                        'data_name': row[1],
                        'data_id': row[0],
                    }
                )
            else:
                rows.append(row)


_STATE_IS_MODULE_DATA = """EXISTS (
    SELECT 1 FROM ir_model_data d
    WHERE d.model = 'res.country.state' AND d.res_id = s.id
        AND d.module NOT IN ('__export__', '__import__'))"""


def unify_codes_of_same_name_country_states(cr):
    """Copies of one state (same country, same name) entered with different
    codes get one code, so that the merge of the post-migration, which works
    by country and code, makes one state of them (Vietnam entered by hand:
    Ha Noi once with code 04, four times with code HN). The code kept is the
    one of a state shipped by a module if there is one, else the one partners
    use most. States shipped by a module never change code.
    """
    cr.execute(
        """
        SELECT s.country_id, btrim(s.name), s.code
        FROM res_country_state s
        LEFT JOIN res_partner p ON p.state_id = s.id
        WHERE s.code IS NOT NULL AND (s.country_id, btrim(s.name)) IN (
            SELECT country_id, btrim(name) FROM res_country_state
            WHERE code IS NOT NULL
            GROUP BY country_id, btrim(name) HAVING count(DISTINCT code) > 1)
        GROUP BY s.country_id, btrim(s.name), s.code
        ORDER BY s.country_id, btrim(s.name),
            bool_or(%s) DESC, count(p.id) DESC, min(s.id)
        """ % _STATE_IS_MODULE_DATA)
    seen = {}
    for country_id, name, code in cr.fetchall():
        if (country_id, name) not in seen:
            seen[(country_id, name)] = code
            continue
        openupgrade.logged_query(
            cr,
            """UPDATE res_country_state s SET code = %%s
            WHERE s.country_id = %%s AND s.code = %%s AND btrim(s.name) = %%s
                AND NOT %s""" % _STATE_IS_MODULE_DATA,
            (seen[(country_id, name)], country_id, code, name))


def disambiguate_country_state_codes(cr):
    """Give different states of a country that share one code a code of their
    own. 10.0 adds unique(country_id, code) and the post-migration merges the
    states that share country and code: fine for copies of one state, wrong
    for different states (Vietnam entered by hand: DN is both Da Nang and
    Dong Nai, partners of the one would move to the other).
    Copies of one state (same name) keep sharing their code and get merged.
    The code stays with the state shipped by a module if there is one, else
    with the name partners use most; the others get the initials of their
    name plus the second letter of the last word, then a number if that is
    taken too. States shipped by a module never change code.
    """
    cr.execute(
        """
        SELECT s.country_id, s.code, btrim(s.name)
        FROM res_country_state s
        LEFT JOIN res_partner p ON p.state_id = s.id
        WHERE (s.country_id, s.code) IN (
            SELECT country_id, code FROM res_country_state
            WHERE code IS NOT NULL
            GROUP BY country_id, code HAVING count(DISTINCT btrim(name)) > 1)
        GROUP BY s.country_id, s.code, btrim(s.name)
        ORDER BY s.country_id, s.code,
            bool_or(%s) DESC, count(p.id) DESC, min(s.id)
        """ % _STATE_IS_MODULE_DATA)
    rows = cr.fetchall()
    if not rows:
        return
    cr.execute("SELECT country_id, code FROM res_country_state")
    used = set(cr.fetchall())
    seen = set()
    for country_id, code, name in rows:
        if (country_id, code) not in seen:
            # first name of the group: keeps the code
            seen.add((country_id, code))
            continue
        words = (name or u'').split()
        base = code
        if words:
            base = u''.join(w[0] for w in words).upper()
            if len(words[-1]) > 1:
                base += words[-1][1].upper()
        new_code, n = base, 1
        while (country_id, new_code) in used:
            n += 1
            new_code = u'%s%d' % (base, n)
        used.add((country_id, new_code))
        openupgrade.logged_query(
            cr,
            """UPDATE res_country_state s SET code = %%s
            WHERE s.country_id = %%s AND s.code = %%s AND btrim(s.name) = %%s
                AND NOT %s""" % _STATE_IS_MODULE_DATA,
            (new_code, country_id, code, name))


def precreate_partner_fields(cr):
    """ Emulate stored computed methods in a single SQL query """
    cr.execute(
        """ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS commercial_company_name VARCHAR,
        ADD COLUMN IF NOT EXISTS partner_share BOOLEAN
        """)
    openupgrade.logged_query(
        cr,
        """UPDATE res_partner rp
        SET commercial_company_name = crp.name
        FROM res_partner crp
        WHERE crp.id = rp.commercial_partner_id
            AND crp.is_company AND COALESCE(crp.name, '') != ''
        """)
    openupgrade.logged_query(
        cr,
        """UPDATE res_partner rp
        SET partner_share = NOT EXISTS (
            SELECT 1 FROM res_users
            WHERE partner_id = rp.id AND active)
        OR EXISTS (
            SELECT 1 FROM res_users
            WHERE partner_id = rp.id AND active AND share)
        """)


_TECHNICAL_MODELS = (
    'ir.actions.act_url', 'ir.actions.act_window', 'ir.actions.client',
    'ir.actions.report', 'ir.actions.report.xml', 'ir.actions.server',
    'ir.actions.todo', 'ir.cron', 'ir.filters', 'ir.model.access',
    'ir.property', 'ir.rule', 'ir.ui.menu', 'ir.ui.view', 'ir.values',
    'mail.template', 'web.tip', 'website.menu',
)


def release_records_of_lost_modules(cr):
    """A module that is removed without a successor is merged into the module
    it extended (apriori.lost_modules), and the update of that module deletes
    the records it no longer finds in the data files, except the noupdate
    ones. Of a module that is gone, a noupdate scheduled action calls a model
    that does not exist, a record rule or a mail template reads fields that
    do not exist: release the technical records, so that they are deleted
    too. Business records (stages, campaigns, products...) stay.
    """
    lost_modules = getattr(apriori, 'lost_modules', [])
    if not lost_modules:
        return
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET noupdate = FALSE
        WHERE noupdate AND module IN %s AND model IN %s
        """, (tuple(lost_modules), _TECHNICAL_MODELS))
    # records of the models that go with the modules: the rows stay in their
    # tables, which no model reads any more; their xml ids would dangle
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data d
        WHERE d.module IN %s AND d.model IN (
            SELECT m.model
            FROM ir_model m
            JOIN ir_model_data md ON md.model = 'ir.model'
                AND md.res_id = m.id AND md.module IN %s
            WHERE NOT EXISTS (
                SELECT 1 FROM ir_model_data o
                WHERE o.model = 'ir.model' AND o.res_id = m.id
                    AND o.module NOT IN %s))
        """, (tuple(lost_modules), ) * 3)


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    release_records_of_lost_modules(cr)
    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )
    openupgrade.rename_columns(cr, _column_renames)
    cr.execute(
        # we rely on the ORM to write this value
        'alter table ir_model_fields add column store boolean'
    )
    openupgrade.copy_columns(cr, {
        'ir_act_window': [
            ('target', None, None),
        ],
    })
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('target'), 'target',
        [
            ('inlineview', 'inline'),
        ],
        table='ir_act_window')
    cr.execute(
        "update ir_ui_view set type='kanban' where type='sales_team_dashboard'"
    )
    cr.execute('update res_currency set symbol=name where symbol is null')
    # create xmlids for installed languages
    cr.execute(
        '''insert into ir_model_data
        (module, name, model, res_id)
        select
        'base',
        'lang_' ||
        case
            when char_length(code) > 2 then
            case
                when upper(substring(code from 1 for 2)) =
                upper(substring(code from 4 for 2)) then
                    substring(code from 1 for 2)
                else
                    code
            end
            else
                code
        end,
        'res.lang', id
        from res_lang''')
    unify_codes_of_same_name_country_states(cr)
    disambiguate_country_state_codes(cr)
    ensure_country_state_id_on_existing_records(cr)
    precreate_partner_fields(cr)
    openupgrade.update_module_names(
        cr, apriori.merged_modules, merge_modules=True,
    )
