from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_slides", "14.0.2.2/noupdate_changes.xml")

    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "mail_template_slide_channel_invite",
            "slide_template_published",
            "slide_template_shared",
        ],
    )
    env["slide.channel.partner"].search([])._recompute_completion()
