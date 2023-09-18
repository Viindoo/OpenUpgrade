import logging
import os

from odoo.modules import get_module_path
from odoo.tools import config
from odoo import tools

from . import odoo_patch

if not config.get("upgrade_path"):
    path = get_module_path("openupgrade_scripts", display_warning=False)
    if path:
        logging.getLogger(__name__).info(
            "Setting upgrade_path to the scripts directory inside the module "
            "location of openupgrade_scripts"
        )
        config["upgrade_path"] = os.path.join(path, "scripts")


def post_load():
    global tools
    # to support extended functionality
    # ex. module viin_website_multilingual_multimedia: at
    # https://viindoo.com/apps/app/15.0/viin_website_multilingual_multimedia
    tools.translate.TRANSLATED_ELEMENTS = set(
        list(tools.TRANSLATED_ELEMENTS) + ["a", "div", "img", "video", "iframe"]
    )
