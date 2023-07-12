from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, ["website.website_menu"])
    openupgrade.load_data(env.cr, "website", "16.0.1.0/noupdate_changes.xml")
