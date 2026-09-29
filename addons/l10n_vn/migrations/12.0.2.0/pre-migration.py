# Copyright 2019 Viindoo (David Tran)
# Copyright 2026 Viindoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import csv
import io
import re
import unicodedata

from odoo.modules.module import get_module_resource
from openupgradelib import openupgrade


def _state_key(name):
    """Name of a state without case, accents, punctuation, spacing and the
    prefix of its kind (Tinh, Thanh pho, TP)."""
    text = unicodedata.normalize('NFD', (name or '').strip().casefold())
    text = ''.join(
        ch for ch in text if unicodedata.category(ch) != 'Mn'
    ).replace('đ', 'd')
    text = re.sub(r'^(tinh|thanh pho|tp\.?)\s+', '', text)
    return re.sub(r'[^a-z0-9]+', '', text)


def adopt_existing_states(cr):
    """12.0 starts shipping the states of Vietnam in l10n_vn. A database
    usually has them already: from to_vietnam_states of tvtmaaddons, or
    entered / imported by the company. Loaded as they are, the 63 states would
    be created once more, next to the ones the partners use.

    Each state of the data file takes over the existing state of Vietnam that
    has the same name: it gets the xml id of the data file, so that the load
    updates it instead of creating another one. Among several states of one
    name, the one most partners use is taken.

    The states are matched by name, never by xml id: the __export__ xml ids
    of to_vietnam_states are the ids of the database the module was exported
    from, and another database may well have the same xml ids on other states
    (v3tech: __export__.res_country_state_124 is Ha Noi, not Dak Lak).
    """
    path = get_module_resource('l10n_vn', 'data', 'res.country.state.csv')
    if not path:
        return
    with io.open(path, encoding='utf-8') as csv_file:
        shipped = list(csv.DictReader(csv_file))
    cr.execute("SELECT id FROM res_country WHERE upper(code) = 'VN'")
    country = cr.fetchone()
    if not country:
        return
    cr.execute(
        """
        SELECT s.id, s.name, count(p.id)
        FROM res_country_state s
        LEFT JOIN res_partner p ON p.state_id = s.id
        WHERE s.country_id = %s
        GROUP BY s.id
        """, (country[0], ))
    candidates = {}
    for state_id, name, partners in cr.fetchall():
        candidates.setdefault(_state_key(name), []).append(
            (-partners, state_id))
    cr.execute(
        """
        SELECT name, res_id FROM ir_model_data
        WHERE module = 'l10n_vn' AND model = 'res.country.state'
        """)
    existing = dict(cr.fetchall())
    taken = set(existing.values())
    for line in shipped:
        module, _dot, name = line['id'].rpartition('.')
        if (module or 'l10n_vn') != 'l10n_vn' or name in existing:
            continue
        choices = sorted(
            choice for choice in candidates.get(_state_key(line['name']), [])
            if choice[1] not in taken)
        if not choices:
            # created by the load of the data file
            continue
        state_id = choices[0][1]
        taken.add(state_id)
        openupgrade.logged_query(
            cr,
            """
            INSERT INTO ir_model_data
                (module, name, model, res_id, noupdate,
                 create_uid, write_uid, create_date, write_date,
                 date_init, date_update)
            VALUES
                ('l10n_vn', %s, 'res.country.state', %s, false,
                 1, 1, now() at time zone 'UTC', now() at time zone 'UTC',
                 now() at time zone 'UTC', now() at time zone 'UTC')
            """, (name, state_id))
        # the code of the data file may be the code of another existing
        # state of the country (entered by hand): free it
        cr.execute(
            """
            UPDATE res_country_state SET code = code || '-' || id
            WHERE country_id = %s AND code = %s AND id != %s
            """, (country[0], line['code'], state_id))


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    adopt_existing_states(cr)
