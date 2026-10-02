from openupgradelib import openupgrade


def convert_assets(env):
    for asset in env["ir.asset"].search([("path", "like", ".custom.")]):
        path_1, extra = asset.path.split(".custom.", 1)
        if extra.count(".") < 2:
            # Not {path_without_extension}.custom.{bundle}.{extension}
            continue
        bundle_1, bundle_2, path_2 = extra.split(".", 2)
        path = f"{path_1}.{path_2}"
        if not path.startswith("/"):
            path = f"/{path}"
        bundle = f"{bundle_1}.{bundle_2}"
        new_path = f"/_custom/{bundle}{path}"
        env["ir.attachment"].search([("url", "=", asset.path)]).write({"url": new_path})
        vals = {"path": new_path}
        if asset.name and ": replace " in asset.name:
            # The name holds the file name of the path
            vals["name"] = f"{bundle}: replace {new_path.split('/')[-1]}"
        asset.write(vals)


@openupgrade.migrate()
def migrate(env, version):
    convert_assets(env)
