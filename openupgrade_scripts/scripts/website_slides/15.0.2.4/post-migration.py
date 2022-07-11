from random import randint

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "website_slides", "15.0.2.4/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "mail_template_slide_channel_invite",
            "slide_template_published",
            "slide_template_shared",
            "mail_notification_channel_invite",
        ],
    )
    update_color_for_slide_channel_tag(env)


def update_color_for_slide_channel_tag(env):
    # We need to update the color of the tag because the course page only shows tags with colors
    channel_tags = env["slide.channel.tag"].search([("color", "=", 0)])
    for tag in channel_tags:
        tag.write({"color": randint(1, 11)})
