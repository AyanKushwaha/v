"""
<rst only="default_jcr">

.. index::
   single: Script; Export base constraints for pairing

.. _export_duty_day_base_constraints:

Export base constraints for pairing
+++++++++++++++++++++++++++++++++++

    This process step creates the base_constraints_duty_days and base_constraints_trip_duty_days etable.

Inclusion of trips
------------------

    Only those trips visible in the current roster window are included in the export. If no rosters are visible the user can
    confirm to use all rosters in the subplan instead.

base_constraints_duty_days etable
.................................

    The rows in the etable are calculated based on the visible rosters (or all rosters if no rosters are
    visible in studio).

    * The active planning period is used to determine which days should be included in the table
    * The active bases are used to determine which bases should be included in the table
    * If the current plan is flight deck, flight deck positions are used in the table (CP, FO). Else cabin crew positions are used (PU, PU + CA)

    The daily availability of crew depends on their employment information and whether they have personal activities in the plan
    The monthly availability also takes into account how many days off the crew should be granted (max of what is granted in the
    current plan and what they should get).

    The calculations are carried out in the rave module `base_constraints_jcr`

Access in Studio
-----------------

    *File > Export > Rostering > Export base constraints*

Technical Details
------------------

    `/carmusr/lib/python/carmusr/rostering/export_duty_day_base_constraints.py`

</rst>
"""

import Cui
import Gui
import Variable
from carmensystems.basics.CancelException import CancelException
import carmstd.bag_handler
import os
import time

import carmensystems.mave.etab as etab
import carmensystems.rave.api as rave
import carmstd.log as log
import carmusr.rostering.get_plan_path as get_plan_path
import shutil as shutil


def get_duty_days_etab_template():
    duty_days_etab_name = rave.eval("base_constraints_common_definitions.%bc_duty_days_table_name_p%")[0]
    duty_days_etab_name = duty_days_etab_name if duty_days_etab_name.endswith(".etab") \
                                       else duty_days_etab_name + ".etab"
    duty_days_etab_template_path = os.path.join(os.environ.get("CARMUSR"), 'crc', 'etable', 'SpLocal', duty_days_etab_name)
    return duty_days_etab_name, duty_days_etab_template_path


def get_trip_duty_days_etab_template():
    trip_duty_days_etab_name = rave.eval("base_constraints_common_definitions.%bc_trip_duty_days_table_name_p%")[0]
    trip_duty_days_etab_name = trip_duty_days_etab_name if trip_duty_days_etab_name.endswith(".etab") \
                                            else trip_duty_days_etab_name + ".etab"
    trip_duty_days_etab_template_path = os.path.join(os.environ.get("CARMUSR"), 'crc', 'etable', 'SpLocal', trip_duty_days_etab_name)
    return trip_duty_days_etab_name, trip_duty_days_etab_template_path


class ExportForPairing():

    def __init__(self):
        self.timestamp = time.strftime("%04Y-%02m-%02d_%02H%02M")
        self.ctf_file = None
        self.ctf_file_path = None
        self.duty_days_etab = None
        self.duty_days_etab_name, self.duty_days_etab_template_path = get_duty_days_etab_template()
        self.trip_duty_days_etab_name, self.trip_duty_days_etab_template_path = get_trip_duty_days_etab_template()
        self.roster_bag_handler = None
        self.trip_bag_handler = None
        self.plan_is_flight_deck = rave.eval("fundamental.%flight_crew%")[0]
        
        # Max trip duty days calculation
        # 5 is hardcoded for long haul trips in rules_indust_ccp_fc module
        self.max_trip_duty_days = max(rave.eval("rules_indust_ccp.%max_days_in_trip_lh%")[0], rave.eval("rules_indust_ccp.%max_days_in_trip_sh%")[0])
        self.limits = {}

    def exportBaseconstraints(self):
        
        basePath = self._get_etab_base_path()
        path = get_plan_path.get_and_create_path_to_export(basePath)
        if path is None:
            Gui.GuiMessage("Could not find proper path to base constraint export.")
            return

        log.debug(path)
        duty_days_path = path + self.duty_days_etab_name
        
        trip_duty_days_path = path + self.trip_duty_days_etab_name

        success = self.get_bag_handlers()
        if not success:
            Gui.GuiMessage("No crew in window 1. Please filter crew in window 1 to export base constraints")
            return
        self.make_base_constraints_duty_days_table()
        try:
            self.duty_days_etab.save(duty_days_path)
            Gui.GuiMessage("Export completed successfully. Export: %s" % duty_days_path)
        except ValueError:
            Gui.GuiMessage("Failed to save exported file: %s" % duty_days_path)
        try:
            self.trip_duty_days_etab.save(trip_duty_days_path)
            Gui.GuiMessage("Export completed successfully. Export: %s" % trip_duty_days_path)
        except ValueError:
            Gui.GuiMessage("Failed to save exported file: %s" % trip_duty_days_path)

    def _get_etab_base_path(self):
        '''
        Tries to get the resource TeamingFilesPath, if that does not succeed None
        '''
        path = os.environ['CARMDATA'] + '/BASECONSTRAINTS/'
        return path

    def get_bag_handlers(self):
        """
        Sets up self.roster_bag_handler for the data to be exported
        """
        # Iterate all visible crews
        try:
            self.roster_bag_handler = carmstd.bag_handler.WindowChains()
        except AttributeError:
            return 0
        return 1

    def confirm_use_all_rosters(self):
        return Gui.GuiContinue("continue_no_roster_window_pairing_ctf",
                               "No rosters in any window. Continue with "
                               "all plan rosters?") != 0

    def make_base_constraints_duty_days_table(self):
        active_roster_bag = self.roster_bag_handler.bag
        bases = set()
        positions = set()
        for roster in active_roster_bag.iterators.roster_set():
            rank = roster.crew.rank()
            bases.add(roster.crew.homebase())
            if rank == "AS":
                continue
            positions.add(rank)

        self.duty_days_etab = etab.load(etab.Session(), self.duty_days_etab_template_path)
        self.duty_days_etab.clear()
        self.trip_duty_days_etab = etab.load(etab.Session(), self.trip_duty_days_etab_template_path)
        self.trip_duty_days_etab.clear()
        self.limits = {}
        
        # Sort for reproducibility
        for base in sorted(bases):
            for position in positions:
                self.append_rows_days(base, position)
                self.append_rows_month(base, position)

    def append_rows_days(self, base, position):
        roster_bag = self.roster_bag_handler.bag
        number_of_days_to_export = roster_bag.base_constraints_jcr.base_constraints_table_number_of_days_to_export()

        for day_num in xrange(1, number_of_days_to_export + 1):
            rd = {}
            rd["base"] = base
            rd["position"] = position
            rd["valid_from_date_hb"] = roster_bag.base_constraints_jcr.day_start_hb(day_num)
            rd["valid_to_date_hb"] = rd["valid_from_date_hb"]
            rd["type"] = roster_bag.base_constraints_jcr.base_constraints_duty_days_maxdayprod_type()
            limit = roster_bag.base_constraints_jcr.position_at_base_available_on_day(day_num, position, base)
            variable_limit = roster_bag.base_constraints_jcr.variable_group_position_at_base_available_on_day(day_num, position, base)
            fixed_limit = roster_bag.base_constraints_jcr.fixed_group_position_at_base_available_on_day(day_num, position, base)
            rd["limit"] = limit
            rd["excess_cost"] = roster_bag.base_constraints_jcr.base_constraints_duty_days_table_excess_cost(rd["limit"])
            self.duty_days_etab.append(rd)
            if(base, position) in self.limits:
                self.limits[(base, position)][0] += variable_limit
                self.limits[(base, position)][1] += fixed_limit
            else:
                self.limits[(base, position)] = [variable_limit, fixed_limit]

            if not self.max_trip_duty_days:
                continue
            rd_trip = {}
            rd_trip["base"] = base
            rd_trip["position"] = position
            rd_trip["valid_from_date_hb"] = roster_bag.base_constraints_jcr.day_start_hb(day_num)
            rd_trip["valid_to_date_hb"] = rd_trip["valid_from_date_hb"]
            rd_trip["type"] = roster_bag.base_constraints_jcr.base_constraints_trip_duty_days_maxtripstotal_type()
            rd_trip["excess_cost"] = roster_bag.base_constraints_jcr.base_constraints_trip_duty_days_table_excess_cost(rd["limit"])
            limit = 0
            crew_day_dict = {}
            where = '(crew.%homestation% = "{}" and base_constraints_jcr.%crew_code_matches%("{}"))'.format(base, position)
            for crew in roster_bag.iterators.roster_set(where=where):
                
                for trip_duty_days in range(self.max_trip_duty_days, 0, -1):
                    day_num_temp = day_num
                    crew_available_count = 0
                    for trip_duty_day in range(1, trip_duty_days + 1):
                        crew_available = crew.base_constraints_jcr.available_on_day(day_num_temp)
                        if crew_available:
                            crew_available_count += 1
                            day_num_temp = day_num + trip_duty_day
                        else:
                            break
                    
                    if crew_available_count == trip_duty_days:
                        for trip_duty_day in range(1, trip_duty_days + 1):
                            if trip_duty_day not in crew_day_dict:
                                crew_day_dict[trip_duty_day] = 0
                            crew_day_dict[trip_duty_day] += 1
                        break
                    
            for trip_duty_days in crew_day_dict:
                rd_trip["trip_duty_days"] = trip_duty_days
                limit = crew_day_dict[trip_duty_days]
                rd_trip["limit"] = limit
                self.trip_duty_days_etab.append(rd_trip)

    def append_rows_month(self, base, position):
        roster_bag = self.roster_bag_handler.bag

        variable_limit = self.limits[(base, position)][0]
        fixed_limit = self.limits[(base, position)][1]
        variable_limit_reduction = int(float(variable_limit) * roster_bag.base_constraints_jcr.base_monthly_availability_scale_percent_p() / 100.0)
        limit = variable_limit_reduction + fixed_limit

        rd = {}
        rd["base"] = base
        rd["position"] = position
        rd["valid_from_date_hb"] = roster_bag.fundamental.pp_start_day()
        rd["valid_to_date_hb"] = roster_bag.fundamental.pp_end_day()
        rd["type"] = roster_bag.base_constraints_jcr.base_constraints_duty_days_maxprodtotal_type()
        rd["limit"] = limit
        rd["excess_cost"] = roster_bag.base_constraints_jcr.base_constraints_duty_days_table_excess_cost(rd["limit"])
        self.duty_days_etab.append(rd)

    def importBaseConstraints(self):

        basePath = self._get_etab_base_path()
        try:
            new_path = Variable.Variable("")
            rval = Cui.CuiSelectFileManager(Cui.gpc_info, new_path, basePath, None, ".etab")
        except CancelException as error:
            return

        destination = get_sub_plan_shadow_path()
        source_path = basePath + new_path.value
        dest = shutil.copy(source_path, destination) 


def get_sub_plan_shadow_path():
    path_var = Variable.Variable("")
    Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, path_var)
    splocal_path_var = path_var.value
    return splocal_path_var


def do_export():
    exppar = ExportForPairing()
    exppar.exportBaseconstraints()


def do_import():
    exppar = ExportForPairing()
    exppar.importBaseConstraints()


def edit_duty_days_table():
    suffix = None
    duty_days_etab_name, duty_days_etab_template_path = get_duty_days_etab_template()
    etab_dir = get_sub_plan_shadow_path()
    path = os.path.join(etab_dir, duty_days_etab_name)
    if not os.path.isfile(path):
        shutil.copy(duty_days_etab_template_path, etab_dir)
    Cui.CuiEditExternalTable(path, suffix, Cui.CUI_EDIT_ETAB_KILL_ON_EXIT)


def edit_trip_duty_days_table():
    suffix = None
    trip_duty_days_etab_name, trip_duty_days_etab_template_path = get_trip_duty_days_etab_template()
    etab_dir = get_sub_plan_shadow_path()
    path = os.path.join(etab_dir, trip_duty_days_etab_name)
    if not os.path.isfile(path):
        shutil.copy(trip_duty_days_etab_template_path, etab_dir)
    Cui.CuiEditExternalTable(path, suffix, Cui.CUI_EDIT_ETAB_KILL_ON_EXIT)
