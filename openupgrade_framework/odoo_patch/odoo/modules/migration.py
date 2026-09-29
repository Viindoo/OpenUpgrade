# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.modules.migration import MigrationManager


def migrate_module(self, pkg, stage):
    """In openupgrade, also run migration scripts upon installation.
    We want to always pass in pre and post migration files and use a new
    argument in the migrate decorator (explained in the docstring)
    to decide if we want to do something if a new module is installed
    during the migration.
    We trick Odoo into running the scripts by temporarily changing the module
    state.

    Only the upgrade path scripts are run for a module being installed: the
    scripts a module ships in its own migrations/ or upgrades/ folder are
    written for a database that already has the module's data (Odoo never runs
    them on installation) and may fail on a fresh install.
    """
    to_install = pkg.state == "to install"
    module_scripts = {}
    if to_install:
        pkg.state = "to upgrade"
        for key in ("module", "module_upgrades"):
            if key in self.migrations[pkg.name]:
                module_scripts[key] = self.migrations[pkg.name][key]
                self.migrations[pkg.name][key] = {}
    if not getattr(pkg, "load_version", pkg.installed_version):
        pkg.installed_version = "16.0.0.0.1"
    try:
        MigrationManager.migrate_module._original_method(self, pkg, stage)
    finally:
        if to_install:
            pkg.state = "to install"
            self.migrations[pkg.name].update(module_scripts)


migrate_module._original_method = MigrationManager.migrate_module
MigrationManager.migrate_module = migrate_module
