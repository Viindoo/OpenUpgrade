# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from collections import defaultdict

from openupgradelib import openupgrade

_deleted_xmlids = []


def pos_category_images(env):
    """
    v19 allows for bigger images, but we can't do better than putting the content of
    image_128 into image_512
    """
    env.cr.execute(
        """
        UPDATE ir_attachment
        SET res_field='image_512'
        WHERE
        res_model='pos.category'
        AND res_field='image_128'
        """
    )


def pos_config_create_sequences(env):
    """
    Create sequences for new fields by calling Odoo's function and deleting what
    already existed
    """
    sequence_fields = (
        "order_seq_id",
        "order_backend_seq_id",
        "order_line_seq_id",
        "device_seq_id",
    )
    to_delete = env["ir.sequence"]
    for pos_config in env["pos.config"].search([]):
        existing_sequences = {
            field_name: pos_config[field_name].id
            for field_name in pos_config._fields
            if field_name in sequence_fields and pos_config[field_name]
        }
        pos_config._create_sequences()
        to_delete += sum(
            (pos_config[field_name] for field_name in existing_sequences),
            env["ir.sequence"],
        )
        pos_config.write(existing_sequences)
    to_delete.unlink()


def pos_order_stock_reference_ids(env):
    """
    Fill pos.order#stock_reference_ids from procurement_group_id
    """
    env.cr.execute(
        """
        INSERT INTO
        stock_reference_pos_order_rel
        (pos_order_id, reference_id)
        SELECT
        id, procurement_group_id
        FROM pos_order
        WHERE procurement_group_id IS NOT NULL
        """
    )


def pos_order_state(env):
    """
    pos.order#state == invoiced has been removed, set orders with this state to 'done'
    as this is what _generate_pos_order_invoice does in v19 when it used 'invoiced' in
    v18
    """
    openupgrade.copy_columns(env.cr, {"pos_order": [("state", None, None)]})
    env.cr.execute("UPDATE pos_order SET state='done' WHERE state='invoiced'")


def uom_uom_is_pos_groupable(env):
    """
    Set uom.uom.is_pos_groupable from former uom category
    """
    env.cr.execute(
        f"""
        UPDATE uom_uom
        SET
        is_pos_groupable=uom_category.is_pos_groupable
        FROM
        uom_category
        WHERE
        uom_uom.{openupgrade.get_legacy_name("category_id")}=uom_category.id
        AND uom_category.is_pos_groupable
        """
    )


def pos_picking_type_sequences(env):
    """
    OpenUpgrade 13.0 (create_pos_picking_types) gives each point of sale an
    operation type of its own, copied from the type they shared, each with a
    new sequence that starts at 1 with the same prefix. The first picking of a
    point of sale then takes a name that exists already ("POS00001": names are
    unique per company), so the order cannot be completed, and the points of
    sale take the same names as each other. The operation types of the points
    of sale with the same prefix, suffix and padding share one sequence, which
    continues after the highest existing picking name of that pattern.
    """
    groups = defaultdict(lambda: env["stock.picking.type"])
    configs = env["pos.config"].with_context(active_test=False).search([])
    for ptype in configs.picking_type_id.with_context(active_test=False):
        seq = ptype.sequence_id
        if not seq or "%(" in (seq.prefix or "") + (seq.suffix or ""):
            continue
        key = (ptype.company_id.id, seq.prefix or "", seq.suffix or "", seq.padding)
        groups[key] |= ptype
    for (company_id, prefix, suffix, _padding), ptypes in groups.items():
        sequences = ptypes.sequence_id
        keep = sequences.sorted("id")[:1]
        pattern = "^%s([0-9]+)%s$" % (re.escape(prefix), re.escape(suffix))
        env.cr.execute(
            """
            SELECT max(substring(name from %s)::bigint) FROM stock_picking
            WHERE company_id IS NOT DISTINCT FROM %s AND name ~ %s
            """,
            (pattern, company_id or None, pattern),
        )
        highest = env.cr.fetchone()[0] or 0
        if len(sequences) > 1:
            ptypes.write({"sequence_id": keep.id})
            (sequences - keep).unlink()
        if highest >= keep.number_next_actual:
            keep.number_next = highest + 1
        openupgrade.logger.info(
            "POS operation types %s share the sequence %s (%s...), next number %s",
            ptypes.ids,
            keep.id,
            prefix,
            keep.number_next_actual,
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "point_of_sale", "19.0.1.0.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    pos_category_images(env)
    pos_config_create_sequences(env)
    pos_order_stock_reference_ids(env)
    pos_order_state(env)
    uom_uom_is_pos_groupable(env)
    pos_picking_type_sequences(env)
