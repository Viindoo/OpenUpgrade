# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree
from openupgradelib import openupgrade

# the fields of the contact form sending an e-mail, and the lead fields that
# take their values (as the "Create an Opportunity" action of the form editor)
FIELD_RENAMES = [("name", "contact_name"), ("company", "partner_name"), ("subject", "name")]
LEAD_FIELDS = {"contact_name", "phone", "email_from", "partner_name", "name", "description"}


def _contactus_form_to_lead(arch):
    """The form of the contact page sending an e-mail, made to create a lead:
    the model, the fields named after the lead (the person in contact_name, the
    company in partner_name, the subject in name, not custom fields appended to
    the description) and no hidden e-mail recipient. None when nothing to do."""
    root = etree.fromstring(arch.encode())
    forms = root.xpath("//form[@id='contactus_form'][@data-model_name='mail.mail']")
    if not forms:
        return None
    form = forms[0]
    form.set("data-model_name", "crm.lead")
    for old, new in FIELD_RENAMES:
        for field in form.xpath(".//*[@name='%s']" % old):
            field.set("name", new)

    def block_of(field):
        blocks = field.xpath(
            "ancestor::div[contains(concat(' ', normalize-space(@class), ' '),"
            " ' s_website_form_field ')][1]"
        )
        return blocks[0] if blocks else None

    for field in form.xpath(".//*[@name]"):
        block = block_of(field)
        if field.get("name") in LEAD_FIELDS and block is not None:
            block.set(
                "class",
                " ".join(
                    c for c in block.get("class").split() if c != "s_website_form_custom"
                ),
            )
    for field in form.xpath(".//input[@name='email_to']"):
        block = block_of(field)
        if block is not None:
            block.getparent().remove(block)
    return etree.tostring(root, encoding="unicode")


def migrate_website_crm_views(env):
    """Up to 14.0 website_crm replaced the form of the contact page with one
    creating an opportunity. 15.0 only fills its default values: the form of
    the page (a website-specific copy since the website migration wrote it)
    sends an e-mail again. Make it create a lead, with the lead fields: the
    sole model change (data-model_name) put the name of the person in the
    subject of the lead and the company and subject in its description."""
    for website in env["website"].search([]):
        website_contactus_view = website.with_context(website_id=website.id).viewref(
            "website.contactus"
        )
        new_arch = _contactus_form_to_lead(website_contactus_view.arch_db)
        if new_arch:
            website_contactus_view.with_context(website_id=website.id).arch = new_arch


@openupgrade.migrate()
def migrate(env, version):
    migrate_website_crm_views(env)
