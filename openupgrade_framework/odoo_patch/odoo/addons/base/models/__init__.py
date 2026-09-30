from . import ir_model

# Not loaded (Viindoo): ir_module marks as to install every auto_install module whose
# dependencies are installed. Migrations do not install modules the database never had
# (as in the 10.0-17.0 forks): on a Viindoo database it pulled in some 120 glue
# modules, and their install hooks run on migrated data (to_hr_timesheet_payroll
# stopped the 17.0 -> 18.0 hop on a duplicate salary rule category).
# from . import ir_module
from . import ir_ui_view
