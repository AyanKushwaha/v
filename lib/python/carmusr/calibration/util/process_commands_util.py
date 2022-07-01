'''
Common stuff for calibration process scripts.

Created on 8 Jul 2020

@author: steham
'''

# Reload handling. Just to simplify development. ##############

try:
    is_being_reloaded  # @UndefinedVariable
    is_being_reloaded = True
except NameError:
    is_being_reloaded = False


import os
import weakref
from tempfile import NamedTemporaryFile
import time

import Errlog
from carmensystems.rave import api as rave
from Localization import MSGR
import Csl
import Cui
import Gui
import Crs
import Cfh
import Dates


parameters_to_set_in_orig_tt_plan = (("studio_calibration_timetable.use_previous_markers", False),
                                     ("calibration_lookback.times_to_use_in_specified_rules",
                                      "calibration_lookback.rule_time_actual_start_actual_end"),
                                     ("studio_calibration.use_lookback_markers", False))

parameters_to_set_in_moved_tt_plan = (("studio_calibration_timetable.use_previous_markers", True),
                                      ("calibration_lookback.times_to_use_in_specified_rules",
                                       "calibration_lookback.rule_time_actual_start_actual_end"),
                                      ("studio_calibration.use_lookback_markers", False))

default_value_for_run_in_background = True


def set_rave_parameters(umh, params_to_change):
    for param_name, new_value in params_to_change:
        try:
            param = rave.param(param_name)
        except rave.UsageError:
            continue
        if new_value != param.value():
            umh.add_message(MSGR("Set rave parameter '{}' to '{}'.").format(param.remark(), new_value))
            if isinstance(param.value(), rave.enumval):
                new_value = rave.enumval(new_value)
            param.setValue(new_value)


def load_rule_set_keep_parameters(path):
    with NamedTemporaryFile() as f:
        try:
            v = rave.param("map_parameter_set_name").value()
        except rave.UsageError:
            v = "Unknown"

        Cui.CuiCrcSaveParameterSet(Cui.gpc_info, None, f.name)
        Cui.CuiCrcLoadRuleset(Cui.gpc_info, path)
        Cui.CuiCrcLoadParameterSet(Cui.gpc_info, f.name)
        try:
            rave.param("map_parameter_set_name").setvalue(v)
        except rave.UsageError:
            pass


lp_top_dir = Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "LocalPlanPath")


class UserMessagesHandler(object):

    log_prefix = "# CALIB USER MESSAGE: "

    def __init__(self, message_file_path):
        self.message_file = NamedTemporaryFile() if message_file_path == "%L" else open(message_file_path, "a")

    def __del__(self):
        self.message_file.close()

    def add_message(self, message, indent_level=1):
        for row in message.split("\n"):
            row = " " * indent_level + row
            Errlog.log(self.log_prefix + row)
            self.message_file.write(row + "\n")
        self.message_file.flush()

    def show_messages(self, title):
        show_file(title, self.message_file.name)


class MySimpleTimer(object):

    def __init__(self):
        self.reset()

    def get_time_as_formatted_string(self):
        return "%0.1fs" % (self._get_current_time() - self.start)

    @staticmethod
    def _get_current_time():
        return time.time()

    def reset(self):
        self.start = self._get_current_time()


class CpsHandler(object):

    def __init__(self, title):
        self.title = title

    def __call__(self, _pid, status, child_data):
        studio_log_file_path = child_data[3]
        user_message_file = child_data[2]
        umh = UserMessagesHandler(user_message_file)
        if status:
            umh.add_message(MSGR("\nThe log file '%s' has been kept.\n") % studio_log_file_path, 0)
        else:
            os.unlink(studio_log_file_path)
        umh.show_messages(self.title + (MSGR(" failed") if status else MSGR(" succeeded")))
        os.unlink(user_message_file)


# Cfh

MAX_LEN_PLAN_NAME_SUFFIX = 8
MAX_LEN_SUB_PLAN_NAME = 200
MAX_LEN_LOCAL_PLAN_NAME = 200


class LocalPlanName(Cfh.PathName):

    def __init__(self, form, name, value):
        super(LocalPlanName, self).__init__(form, name, MAX_LEN_LOCAL_PLAN_NAME, value, 3, 3)

    def check(self, txt):
        txt = txt.replace("  ", "/")
        self.setValue(txt)
        ret = super(LocalPlanName, self).check(txt)
        if ret:
            return ret

        if not os.path.exists(os.path.join(lp_top_dir, txt)):
            return MSGR("There is no local plan with this name")

        if not os.path.exists(os.path.join(lp_top_dir, txt, ".Dated")):
            return MSGR("The local plan is a STANDARD plan. Not supported.")


class RuleSetName(Cfh.String):

    def __init__(self, form, name, value):
        super(RuleSetName, self).__init__(form, name, 0, value)
        self.refresh_menu()
        self.setMandatory(1)
        self.setMenuOnly(1)

    def refresh_menu(self):
        all_rule_sets = [it for it in os.listdir(os.path.expandvars("$CARMTMP/crc/rule_set/GPC/$ARCH")) if not it.startswith(".")]
        rule_set_menu = [MSGR("Rule set")] + sorted(all_rule_sets)
        self.setMenu(rule_set_menu)


class SetDefaultValues(Cfh.Function):

    def __init__(self, *args, **kw):
        Cfh.Function.__init__(self, *args, **kw)
        parent = args[0]
        self.parent = weakref.ref(parent)
        self.default_values = [(name, item.valof()) for name, item in parent.__dict__.iteritems() if hasattr(item, "valof")]

    def action(self):
        parent = self.parent()
        for name, value in self.default_values:
            field = getattr(parent, name)
            field.setValue(field.toString(value))


# Work around for problem reported in Jira STUDIO-19241
def studio_19241_work_around(cfh_form):
    for attr in vars(cfh_form).values():
        if not hasattr(attr, "getMandatory"):
            continue
        if attr.getMandatory():
            continue
        v = attr.getValue()
        if not v:
            continue
        cret = attr.check(v)
        if not cret:
            continue
        attr.setFocus()
        return cret


# Utils

def show_file(title, filepath):
    csl = Csl.Csl()
    csl.evalExpr('csl_show_file("%s","%s")' % (title, filepath))


def close_message_window():
    btype = "NOTICE"
    bid = ""
    byp = {"TYPE": btype,
           "ID": bid,
           "button": "OK"}

    Cui.CuiBypassWrapper("GuiProcessInteraction",
                         Gui.GuiProcessInteraction,
                         (byp, btype, bid))


def get_text_for_sub_plan_comment(operation, plan_name, command):
    return MSGR("{} from '{}'\nby '{}' at {}.\n").format(operation, plan_name, command,
                                                         Dates.FDatInt2DateTime(Dates.FDatUnix2CarmTimeLT(time.time())))


if is_being_reloaded:
    reload(__import__("carmusr.calibration.command_create_single_legs_plan_for_timetable_analysis", fromlist=[None]))
    reload(__import__("carmusr.calibration.command_move_or_refresh_plans", fromlist=[None]))
