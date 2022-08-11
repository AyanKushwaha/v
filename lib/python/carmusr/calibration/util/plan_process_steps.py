from __future__ import absolute_import

import os
import six
from tempfile import NamedTemporaryFile
from enum import Enum

# Core imports
from carmensystems.rave import api as rave
import Cui
import Crs
from Localization import MSGR
from __main__ import exception as StudioError  # @UnresolvedImport
import MenuCommandsExt

# Calibration imports
from jcms.calibration import plan


class Product(Enum):
    PAC = 'pac'
    CAS = 'cas'
    TAIL = 'tail'
    UNKNOWN = 'unknown'


class Resource(object):
    @staticmethod
    def default_rule_set():
        return Resource.get_config("CrcDefaultRuleSet")

    @staticmethod
    def product():
        return Resource.get_config("product")

    @staticmethod
    def get_config(resource):
        search_mode = Crs.CrsSearchModuleDef
        return Crs.CrsGetModuleResource('config', search_mode, resource)


def get_product():
    prod = Resource.product()
    prod = prod.lower()
    for enumprod in Product.__members__.values():
        if enumprod.value == prod:
            return enumprod
    return Product.UNKNOWN


current_product = get_product()


class ChainNames(object):
    trips = MSGR('trips')
    legs = MSGR('legs')
    rosters = MSGR('rosters')
    tailrotations = MSGR('assignments')
    tailtrips = MSGR('leg sequences')


class PlanProcessSteps(object):
    def __init__(self, message_handler):
        self.message_handler = message_handler

    def force_open_plan(self, plan_name):
        components = plan_name.split(os.path.sep)
        if components == 3:
            message = MSGR("Load the local plan '{}'.").format(plan_name)
        elif components == 4:
            message = MSGR("Load the sub-plan '{}'.").format(plan_name)
        else:
            message = MSGR("Load the plan '{}'.").format(plan_name)
        self.message_handler.add_message(message)
        plan.open_plan(plan_name, confirm=False, silent=True, force=True)

    def force_save_subplan(self, verbose=True):
        if verbose:
            self.message_handler.add_message(MSGR("Saving sub-plan"))
        plan.save_subplan(confirm=False, silent=True, force=True)

    def save_subplan_as(self, sp_name):
        self.message_handler.add_message(MSGR("Save the sub-plan as '%s'." % sp_name))
        plan.save_subplan(sp_name)

    def set_subplan_comment(self, sp_comment):
        Cui.CuiSetSubPlanComment(Cui.gpc_info, sp_comment)

    def set_rave_parameters(self, params_to_change):
        for param_name, new_value in params_to_change:
            try:
                param = rave.param(param_name)
            except rave.UsageError:
                continue
            if new_value != param.value():
                self.message_handler.add_message(MSGR("Set rave parameter '{}' to '{}'.").format(param.remark(), new_value))
                if isinstance(param.value(), rave.enumval):
                    new_value = rave.enumval(new_value)
                param.setValue(new_value)

    def load_rule_set(self, rule_set):
        self.message_handler.add_message(MSGR("Load the rule set '%s'." % rule_set))
        Cui.CuiCrcLoadRuleset(Cui.gpc_info, rule_set)

    def load_rule_set_keep_parameters(self, rule_set):
        self.message_handler.add_message(MSGR("Load the rule set '%s' (keep parameter settings).") % rule_set)
        with NamedTemporaryFile(mode="wb" if six.PY2 else "wt") as f:
            try:
                v = rave.param("map_parameter_set_name").value()
            except rave.UsageError:
                v = "Unknown"

            Cui.CuiCrcSaveParameterSet(Cui.gpc_info, None, f.name)
            Cui.CuiCrcLoadRuleset(Cui.gpc_info, rule_set)
            Cui.CuiCrcLoadParameterSet(Cui.gpc_info, f.name)
            try:
                rave.param("map_parameter_set_name").setvalue(v)
            except rave.UsageError:
                pass

    def load_parameters_file(self, parameter_file):
        self.message_handler.add_message(MSGR("Load the parameter file '%s'.") % parameter_file)
        Cui.CuiCrcLoadParameterSet(Cui.gpc_info, parameter_file)

    def generate_leg_kpis(self):
        self._generate_kpis([Cui.LegMode], [ChainNames.legs])

    def generate_plan_kpis_exclude_hidden(self, prod=current_product):
        if prod == Product.PAC:
            area_modes = [Cui.CrrMode]
            mode_descriptions = [ChainNames.trips]
        else:
            if prod == Product.TAIL:
                crew_chain_name = ChainNames.tailrotations
                trip_chain_name = ChainNames.tailtrips
            else:
                crew_chain_name = ChainNames.rosters
                trip_chain_name = ChainNames.trips
            area_modes = [Cui.CrewMode, Cui.CrrMode]
            mode_descriptions = [crew_chain_name, trip_chain_name]
        self._generate_kpis(area_modes, mode_descriptions)

    def _generate_kpis(self, area_modes, mode_descriptions):
        msg = MSGR("Generate Custom KPIs for all {} in the loaded sub-plan.").format(MSGR(' and ').join(mode_descriptions))
        self.message_handler.add_message(msg)
        for i, area_mode in enumerate(area_modes):
            area = getattr(Cui, 'CuiArea{}'.format(i))
            if area_mode == Cui.CrrMode:
                MenuCommandsExt.selectTripUsingPlanningAreaBaseFilter(area=area)
            elif area_mode == Cui.CrewMode:
                MenuCommandsExt.selectCrewUsingPlanningAreaBaseFilter(area=area)
            else:
                Cui.CuiDisplayObjects(Cui.gpc_info, area, area_mode, Cui.CuiShowAll)
        try:
            Cui.CuiGenerateKpis(Cui.gpc_info, Cui.CUI_SILENT, "window")
        except StudioError:
            self.message_handler.add_message(MSGR("Warning. Generation of Custom KPIs failed."))

    def add_all_legs_in_lp_to_sp(self):
        Cui.CuiSetSubPlanCrewFilterLeg(Cui.gpc_info, 0)
        self.message_handler.add_message(MSGR("Add all legs in the local plan to the loaded sub-plan."))
        Cui.CuiSelectLegs(Cui.gpc_info, Cui.CuiNoArea, 1 | 32)  # Add all legs from LP silently.
