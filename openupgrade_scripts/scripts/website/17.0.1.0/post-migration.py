# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from openupgradelib import openupgrade


def _convert_custom_asset_path(old_path):
    """
    Convert custom asset path from Odoo 16 format to Odoo 17 format.

    Odoo 16 format: {path_without_extension}.custom.{bundle}.{extension}
    Odoo 17 format: /_custom/{bundle}{original_path_with_extension}

    Example:
    - Old: /website/static/src/scss/options/user_values.custom.web.assets_frontend.scss
    - New: /_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss

    Returns:
        str: new_path or None if conversion fails
    """
    if not old_path or ".custom." not in old_path:
        return None

    # Pattern to match: {path_without_extension}.custom.{bundle}.{extension}
    # Bundle can contain dots (e.g., web.assets_backend)
    pattern = r"^(.+)\.custom\.(.+)\.([^.]+)$"
    match = re.match(pattern, old_path)

    if not match:
        return None

    path_without_extension = match.group(1)
    bundle = match.group(2)
    extension = match.group(3)

    # Reconstruct original path with extension
    original_path = f"{path_without_extension}.{extension}"

    # Ensure original_path starts with /
    if not original_path.startswith("/"):
        original_path = "/" + original_path

    # New format: /_custom/{bundle}{original_path}
    return f"/_custom/{bundle}{original_path}"


def _migrate_custom_assets(env):
    """
    Migrate custom asset paths from Odoo 16 format to Odoo 17 format.
    Updates both ir.asset.path and ir.attachment.url fields.
    """
    Asset = env["ir.asset"]
    Assets = env["web_editor.assets"]  # type: ignore
    old_assets = Asset.search([("path", "like", ".custom.")])

    has_updates = False
    for asset in old_assets:
        old_path = asset.path
        new_path = _convert_custom_asset_path(old_path)
        if not new_path:
            continue

        # Calculate new name based on new_path
        # Format: "{bundle}: replace {filename}"
        new_name = asset.name
        if asset.name and ": replace " in asset.name:
            # Extract bundle from new_path: /_custom/{bundle}/...
            path_parts = new_path.split("/", 3)
            if len(path_parts) >= 3:
                bundle = path_parts[2]
                filename = new_path.split("/")[-1]
                new_name = f"{bundle}: replace {filename}"

        # Update asset path and name
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_asset
            SET name = %s,
                path = %s
            WHERE id = %s
            """,
            (new_name, new_path, asset.id),
        )

        # Find and update related attachment
        custom_attachment = Assets.with_context(
            website_id=asset.website_id.id  # type: ignore
        )._get_custom_attachment(old_path)  # type: ignore

        if custom_attachment:
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE ir_attachment
                SET url = %s
                WHERE id = %s
                """,
                (new_path, custom_attachment.id),
            )

        has_updates = True

    if has_updates:
        env.registry.clear_cache("assets")


@openupgrade.migrate()
def migrate(env, version):
    _migrate_custom_assets(env)
    openupgrade.load_data(env, "website", "17.0.1.0/noupdate_changes.xml")
