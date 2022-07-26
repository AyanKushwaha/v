"""
All dependences of the surrounding CARMUSR, which Calibration Python modules
have, are collected in this module.

Indirect dependencies:
* "date_extensions" requires the rave module with the same name
* "bag_handler" requires the rave module "studio_sno".
* There are no indirect dependencies of python modules.
"""

# Python modules
 
from carmstd import translation_type_ext  # @UnusedImport
from carmstd import date_extensions  # @UnusedImport

from carmstd import bag_handler  # @UnusedImport
from carmstd import report_generation  # @UnusedImport
from report_sources.include.studiopalette import studio_palette  # @UnusedImport
from report_sources.include.drawext import DrawExt  # @UnusedImport


# Settings

keep_temporary_sub_plan_in_timetable_analysis_script = False


# Rave levels

LEVEL_LEG = 'levels.leg'
LEVEL_DUTY = 'levels.duty'
LEVEL_DUTY_ATOMIC_ITERATOR_NAME = "iterators.duty_set"
LEVEL_TRIP = 'levels.trip'
LEVEL_TRIP_ATOMIC_ITERATOR_NAME = "iterators.trip_set"


# Definitions in Rave needed in Calibration reports

rave_variable_for_planning_period_start = "fundamental.pp_start"
rave_variable_for_planning_period_end = "fundamental.pp_end"


# Image files used by the Calibration reports (in "CARMUSR/images")

image_file_name_table = "table.jpg"
image_file_name_diagram = "diagram.jpg"
image_file_name_client_logo = "sas_logo.jpg"


# Presentation

LENGTH_SHORT_RULE_LABEL = 20
