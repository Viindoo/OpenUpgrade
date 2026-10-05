# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.modules.migration import MigrationManager


def _get_files(self):
    """Turns out Odoo SA sometimes add migration scripts that interfere with
    OpenUpgrade. Those we filter out here"""
    MigrationManager._get_files._original_method(self)
    to_exclude = [("analytic", "1.2")]
    for addon, version in to_exclude:
        self.migrations.get(addon, {}).get("module", {}).pop(version, None)


_get_files._original_method = MigrationManager._get_files
MigrationManager._get_files = _get_files


def migrate_module(self, pkg, stage):
    """The scripts of the upgrade path are forced for the modules being
    installed (see loading.py). The migrations/ and upgrades/ folders of the
    module itself are written for a module that was installed before: on a
    fresh installation, with no installed version, every script of every older
    series kept in the folder would run, on tables the module has just created
    (or has not created yet). Hide them for a module that is not upgraded.
    """
    hidden = {}
    if pkg.load_state != "to upgrade":
        for key in ("module", "module_upgrades"):
            if self.migrations.get(pkg.name, {}).get(key):
                hidden[key] = self.migrations[pkg.name][key]
                self.migrations[pkg.name][key] = {}
    try:
        MigrationManager.migrate_module._original_method(self, pkg, stage)
    finally:
        if hidden:
            self.migrations[pkg.name].update(hidden)


migrate_module._original_method = MigrationManager.migrate_module
MigrationManager.migrate_module = migrate_module
