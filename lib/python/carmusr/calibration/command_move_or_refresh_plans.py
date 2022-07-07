'''
Created on 10 Jun 2020

@author: steham

'''

from tempfile import NamedTemporaryFile
import os
import traceback
import re

import Cfh
import Cui
import Gui
import MenuCommandsExt
import Cps
import Errlog
from Localization import MSGR
import Crs
from jcms.calibration import move_subplan
from jcms.calibration import plan
from __main__ import exception as StudioError  # @UnresolvedImport

import carmusr.calibration.util.process_commands_util as pcu


crc_param_dir = Crs.CrsGetModuleResource("default", Crs.CrsSearchModuleDef, "CRC_PARAMETERS_DIR")


class LABELS:
    from_lp = MSGR("From local plan")
    to_lp = MSGR("To local plan")
    sub_plans = MSGR("Sub-plans to process")
    rule_set_name = MSGR("Name of rule set to apply after move")
    param_file_for_orig_plans = MSGR("Optional parameter file to load for original sub-plans")
    param_file_for_moved_plans = MSGR("Optional parameter file to load for moved sub-plans")
    suffix_for_orig_plans = MSGR("Suffix to add to original sub-plans")
    suffix_for_moved_plans = MSGR("Suffix to add to moved sub-plans")


class LABELS_WHEN_NO_TO_PLAN(LABELS):
    from_lp = MSGR("Local plan")
    param_file_for_orig_plans = MSGR("Optional parameter file to load")
    suffix_for_orig_plans = MSGR("Suffix to add to sub-plans")


class Variant(object):
    key = None  # define in sub-class
    title = None  # define in sub-class
    allow_to_plan = True
    allow_regex = True
    use_param_sets = True
    allow_only_refresh_plans = True
    set_tt_params = False

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def get_from_key(cls, key):
        return {PA.key: PA,
                LB.key: LB,
                TT.key: TT}[key]

    @classmethod
    def labels(cls):
        return LABELS if cls.allow_to_plan else LABELS_WHEN_NO_TO_PLAN

    @classmethod
    def form_name(cls):
        return "CALIB_MOVE_PLANS_" + cls.key.upper()


class TT(Variant):
    key = "tt"
    title = MSGR("Move Sub-plans for Timetable Analysis")
    allow_only_refresh_plans = False
    allow_regex = False
    use_param_sets = False
    moved_suffix_default = "_m"
    set_tt_params = True


class LB(Variant):
    key = "lb"
    title = MSGR("Move or Refresh Sub-plans for Lookback Analysis")
    moved_suffix_default = "_lb"


class PA(Variant):
    key = "pa"
    title = MSGR("Create or Refresh KPI Sub-plans")
    allow_to_plan = False


def do_it_with_gui(variant_key):
    """
    This is the only "exported" function.
    Call it with bypass-wrapper if you need a silent version.
    Return values similar to Cui functions to allow adequate bypassing.
    """
    variant = Variant.get_from_key(variant_key)
    Cui.CuiPlanManager(Cui.gpc_info, 0)
    if variant.use_param_sets:
        Cui.CFM("CFM_ParameterSets")

    # Ask for plan names
    form = MyForm(variant)
    form.show(1)
    if form.loop() != Cfh.CfhOk:
        return 1

    only_refesh_plans = variant.allow_only_refresh_plans and form.action.valof() == MyAction.only_refresh_plans_value
    args = ("%L",
            variant_key,
            only_refesh_plans,
            form.from_local_plan.valof(),
            form.to_local_plan.valof() if hasattr(form, "to_local_plan") else None,
            form.rule_set_name.valof() if hasattr(form, "rule_set_name") else None,
            form.param_set_for_orig_plans.valof() if hasattr(form, "param_set_for_orig_plans") else None,
            form.param_set_for_moved_plans.valof() if hasattr(form, "param_set_for_moved_plans") else None)

    if only_refesh_plans:
        args += (form.sub_plans_to_refresh_orig_lp_as_string,
                 form.sub_plans_to_refresh_moved_lp_as_string)
    else:
        args += (form.sub_plans_to_move_as_string,
                 form.orig_suffix.valof(),
                 form.moved_suffix.valof() if hasattr(form, "moved_suffix") else "")

    if form.run_in_background.valof() if hasattr(form, "run_in_background") else True:
        cmd = "".join(['$CARMSYS/bin/studio -l %E -d -p',
                       '"PythonEvalExpr(\\"__import__(\\\\\\"%s\\\\\\",' % __name__,
                       'fromlist=[None])._do_it_in_batch(',
                       ','.join(['\\\\\\"%s\\\\\\"' % arg if isinstance(arg, str) else repr(arg) for arg in args]),
                       ')\\")"'])

        return min(0, Cps.Spawn(cmd, variant.title, "s", pcu.CpsHandler(variant.title)))
    else:
        if plan.local_plan_is_loaded() and not Gui.GuiYesNo("TT_WARNING",
                                                            MSGR("The currently loaded plans will silently be closed by the command. Continue?")):
            return 1
        return DoIt()(*args)


def _do_it_in_batch(*args):

    ret = DoIt()(*args)
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT | Cui.CUI_EXIT_ERROR if ret else Cui.CUI_EXIT_SILENT)


class DoIt(object):

    def __call__(self, user_messages_file_path, *args):
        self.umh = pcu.UserMessagesHandler(user_messages_file_path)
        try:
            self.all_timer = pcu.MySimpleTimer()
            self.plan_timer = pcu.MySimpleTimer()
            (variant_key, only_refesh_plans, self.from_local_plan, self.to_local_plan,
             self.rule_set_name, self.param_set_for_orig_plans, self.param_set_for_moved_plans) = args[:7]

            self.variant = Variant.get_from_key(variant_key)
            if only_refesh_plans:
                self._refesh_plans(*args[7:])
            else:
                self._move_plans(*args[7:])
            self.umh.add_message(MSGR("Ready. Total duration %s.") % self.all_timer.get_time_as_formatted_string())
            ret = 0
        except Exception:
            Errlog.log(traceback.format_exc())
            self.umh.add_message(MSGR("Something unexpected happened. Process STOPPED. See the log file."))
            ret = -1

        pcu.close_message_window()
        self.umh.show_messages(self.variant.title + (MSGR(" failed") if ret else MSGR(" succeeded")))
        return ret

    def _move_plans(self, sub_plans_to_move_as_string, orig_suffix, moved_suffix):
        sp_names = sub_plans_to_move_as_string.split(",")
        self._log_common_params()
        if self.to_local_plan:
            self.umh.add_message(get_move_plans_message(sp_names, orig_suffix, moved_suffix, self.variant))
        else:
            self.umh.add_message(get_create_kpi_plans_message(sp_names, orig_suffix, self.variant))
        self.umh.add_message("", 0)
        self.umh.add_message(MSGR("Log:"), 0)
        for sp in sp_names:
            self.plan_timer.reset()
            source_plan_full_name = os.path.join(self.from_local_plan, sp)

            best_solution_file_path = os.path.join(pcu.lp_top_dir, source_plan_full_name, "APC_FILES", "best_solution")
            if os.path.exists(best_solution_file_path):
                source_plan_full_name = os.path.join(source_plan_full_name, "best_solution")
            sp_new_from_full_name = os.path.join(self.from_local_plan, sp + orig_suffix)
            self.umh.add_message(MSGR("Load the sub-plan '%s'." % source_plan_full_name))
            plan.open_plan(source_plan_full_name, confirm=False, silent=True, force=True)
            self.umh.add_message(MSGR("Save the sub-plan as '%s'." % sp_new_from_full_name))
            plan.save_subplan(sp_new_from_full_name)
            sp_comment = pcu.get_text_for_sub_plan_comment(MSGR("Copied"), source_plan_full_name, self.variant.title)
            self.finalize_sp(sp + orig_suffix, False, sp_comment)

            if self.to_local_plan:
                self.plan_timer.reset()
                sp_new_to_full_name = os.path.join(self.to_local_plan, sp + moved_suffix)
                self.umh.add_message(MSGR("Create the sub-plan '{}' from '{}' using Calibration's 'Move to new version'.").format(sp_new_to_full_name,
                                                                                                                                  sp_new_from_full_name))
                move_subplan.do_move_to_new_version(sp_new_from_full_name, sp_new_to_full_name, False)
                sp_comment = pcu.get_text_for_sub_plan_comment(MSGR("Moved"), sp_new_from_full_name, self.variant.title)
                self.finalize_sp(sp + moved_suffix, True, sp_comment)

    def _refesh_plans(self, sub_plans_to_refresh_orig_lp_as_string, sub_plans_to_refresh_moved_lp_as_string):
        sp_names_orig = filter(None, sub_plans_to_refresh_orig_lp_as_string.split(","))
        sp_names_moved = filter(None, sub_plans_to_refresh_moved_lp_as_string.split(","))
        self._log_common_params()
        self.umh.add_message(get_refresh_plans_message(sp_names_orig, sp_names_moved, self.variant))
        self.umh.add_message("", 0)
        self.umh.add_message(MSGR("Log:"), 0)
        for sp_name in sp_names_orig:
            self.plan_timer.reset()
            self.finalize_sp(sp_name, False)
        for sp_name in sp_names_moved:
            self.plan_timer.reset()
            self.finalize_sp(sp_name, True)

    def _log_common_params(self):
        self.umh.add_message(MSGR("Parameters:"), 0)
        to_show = ((self.variant.labels().from_lp, self.from_local_plan),)
        if self.variant.allow_to_plan:
            to_show += ((self.variant.labels().to_lp, self.to_local_plan or "-"),)
        if self.to_local_plan:
            to_show += ((self.variant.labels().rule_set_name, self.rule_set_name or "-"),)
        if self.variant.use_param_sets:
            to_show += ((self.variant.labels().param_file_for_orig_plans, self.param_set_for_orig_plans or "-"),)
            if self.to_local_plan:
                to_show += ((self.variant.labels().param_file_for_moved_plans, self.param_set_for_moved_plans or "-"),)

        longest_label = max(len(label) for label, _ in to_show)
        for label, value in to_show:
            self.umh.add_message("%s%s: %s" % (label, "." * (longest_label - len(label)), value))
        self.umh.add_message("", 0)

    def finalize_sp(self, sub_plan_name, has_been_moved, sp_comment=None):
        full_sub_plan_name = os.path.join(self.to_local_plan if has_been_moved else self.from_local_plan, sub_plan_name)
        self.umh.add_message(MSGR("Load the sub-plan '%s'.") % full_sub_plan_name)
        plan.open_plan(full_sub_plan_name, silent=True, confirm=False, force=True)

        if has_been_moved:
            self.umh.add_message(MSGR("Load the rule set '%s' (keep parameter settings).") % self.rule_set_name)
            pcu.load_rule_set_keep_parameters(self.rule_set_name)

        parameter_file = self.param_set_for_moved_plans if has_been_moved else self.param_set_for_orig_plans
        if parameter_file:
            self.umh.add_message(MSGR("Load the parameter file '%s'.") % parameter_file)
            Cui.CuiCrcLoadParameterSet(Cui.gpc_info, parameter_file)

        if self.variant.set_tt_params:
            if has_been_moved:
                pcu.set_rave_parameters(self.umh, pcu.parameters_to_set_in_moved_tt_plan)
            else:
                pcu.set_rave_parameters(self.umh, pcu.parameters_to_set_in_orig_tt_plan)

        try:
            plan.save_subplan(silent=True, confirm=False, force=True)
        except Exception:
            Errlog.log(traceback.format_exc())
            self.umh.add_message(MSGR("Warning. The loaded sub-plan can't be saved. No Custom KPIs are generated."))
            self.umh.add_message("")
            return

        MenuCommandsExt.selectTripUsingPlanningAreaBaseFilter(area=Cui.CuiArea0)

        self.umh.add_message(MSGR("Generate Custom KPIs for visible trips in the loaded sub-plan."))
        try:
            Cui.CuiGenerateKpis(Cui.gpc_info, Cui.CUI_SILENT, "window")
        except StudioError:
            self.umh.add_message(MSGR("Warning. Generation of Custom KPIs failed."))

        if sp_comment:
            Cui.CuiSetSubPlanComment(Cui.gpc_info, sp_comment)

        self.umh.add_message(MSGR("Save the sub-plan."))
        plan.save_subplan(silent=True, confirm=False, force=True)

        msg = MSGR("'{}' is now ready to be analysed. Duration {}.").format(full_sub_plan_name,
                                                                            self.plan_timer.get_time_as_formatted_string())
        self.umh.add_message(msg)
        self.umh.add_message("")


class MyForm(Cfh.Box):

    the_instances = {}

    def __new__(cls, variant):
        if variant.key not in cls.the_instances:
            cls.the_instances[variant.key] = Cfh.Box.__new__(cls)
            cls._my_init(cls.the_instances[variant.key], variant)
        else:
            cls.the_instances[variant.key].refresh_form()
        return cls.the_instances[variant.key]

    def __init__(self, *args, **kw):
        pass

    def refresh_form(self):
        if hasattr(self, "rule_set_name"):
            self.rule_set_name.refresh_menu()

    def _my_init(self, variant):
        self.variant = variant
        form_name = variant.form_name()
        super(MyForm, self).__init__(form_name)

        layout = ["FORM;%s;%s" % (form_name, variant.title),
                  "COLUMN;70"]

        self.from_local_plan = pcu.LocalPlanName(self, "FROM_LOCAL_PLAN", "")
        self.from_local_plan.setMandatory(1)
        layout.append("FIELD;FROM_LOCAL_PLAN;%s" % self.variant.labels().from_lp)

        self.subplans = Cfh.String(self, "SUBPLANS", pcu.MAX_LEN_SUB_PLAN_NAME, "")
        self.subplans.setMandatory(1)
        layout.append("FIELD;SUBPLANS;%s" % self.variant.labels().sub_plans)

        if variant.allow_regex:
            self.matching_method = MySubPlanMatchingMethod(self, "MATCHING_METHOD", MySubPlanMatchingMethod.comma_separated_value)
            layout.append("FIELD;MATCHING_METHOD;%s" % MSGR("   matching method"))

        if variant.allow_to_plan:
            self.to_local_plan = pcu.LocalPlanName(self, "TO_LOCAL_PLAN", "")
            layout.append("FIELD;TO_LOCAL_PLAN;%s" % self.variant.labels().to_lp)

            default_rule_set = os.path.basename(Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "CrcDefaultRuleSet"))
            self.rule_set_name = pcu.RuleSetName(self, "RULE_SET_NAME", default_rule_set)
            layout.append("FIELD;RULE_SET_NAME;%s" % self.variant.labels().rule_set_name)

        if variant.use_param_sets:
            self.param_set_for_orig_plans = MyParamSet(self, "PARAM_SET_ORIG", "")
            layout.append("FIELD;PARAM_SET_ORIG;%s" % self.variant.labels().param_file_for_orig_plans)

            if variant.allow_to_plan:
                self.param_set_for_moved_plans = MyParamSet(self, "PARAM_SET_MOVED", "")
                layout.append("FIELD;PARAM_SET_MOVED;%s" % self.variant.labels().param_file_for_moved_plans)

        self.orig_suffix = Cfh.FileName(self, "ORIG_SUFFIX", pcu.MAX_LEN_PLAN_NAME_SUFFIX, "_p")
        self.orig_suffix.setMandatory(1)
        layout.append("FIELD;ORIG_SUFFIX;%s" % self.variant.labels().suffix_for_orig_plans)

        if variant.allow_to_plan:
            self.moved_suffix = Cfh.FileName(self, "MOVED_SUFFIX", pcu.MAX_LEN_PLAN_NAME_SUFFIX, variant.moved_suffix_default)
            self.moved_suffix.setMandatory(1)
            layout.append("FIELD;MOVED_SUFFIX;%s" % self.variant.labels().suffix_for_moved_plans)

        if variant.allow_only_refresh_plans:
            self.action = MyAction(self, "ACTION", MyAction.create_new_plans_value)
            layout.append("EMPTY")
            layout.append("FIELD;ACTION;%s" % MSGR("Action"))

        layout.append("EMPTY")
        self.run_in_background = Cfh.Toggle(self, "RUN_IN_BACKGROUND", pcu.default_value_for_run_in_background)
        layout.append("FIELD;RUN_IN_BACKGROUND;%s" % MSGR("Run in background"))

        self.done = Cfh.Done(self, "OK")
        layout.append("BUTTON;OK;%s;%s" % (MSGR("OK"), MSGR("_Ok")))

        self.cancel = Cfh.Cancel(self, "CANCEL")
        layout.append("BUTTON;CANCEL;%s;%s" % (MSGR("Cancel"), MSGR("_Cancel")))

        self.reset = Cfh.Reset(self, "RESET")
        layout.append("BUTTON;RESET;%s;%s" % (MSGR("Reset"), MSGR("_Reset")))

        self.default = pcu.SetDefaultValues(self, "DEFAULT")
        layout.append("BUTTON;DEFAULT;%s;%s" % (MSGR("Default"), MSGR("_Default")))

        with NamedTemporaryFile() as f:
            f.write("\n".join(layout))
            f.flush()
            self.load(f.name)

    def check(self, *_args):
        ret = pcu.studio_19241_work_around(self)
        if ret:
            return ret
        from_lp_name = self.from_local_plan.getValue()
        to_lp_name = self.to_local_plan.getValue() if hasattr(self, "to_local_plan") else ""
        if from_lp_name == to_lp_name:
            self.to_local_plan.setFocus()
            return MSGR("The local plans can't be the same")
        use_regex = self.variant.allow_regex and self.matching_method.getValue() == MySubPlanMatchingMethod.regex_value
        orig_suffix = self.orig_suffix.getValue()
        moved_suffix = self.moved_suffix.getValue() if hasattr(self, "moved_suffix") else ""
        sp_value = self.subplans.getValue()
        only_refresh_plans = self.variant.allow_only_refresh_plans and self.action.getValue() == MyAction.only_refresh_plans_value
        all_sub_plans_of_from_lp = set(Cui.CuiSubPlanList(from_lp_name))
        if to_lp_name:
            all_sub_plans_of_to_lp = set(Cui.CuiSubPlanList(to_lp_name))
        if not use_regex:
            sp_set = set(sp for sp in (x.strip() for x in sp_value.split(',')) if sp)

        if only_refresh_plans:
            if not use_regex:
                sp_names_orig = sorted([name + orig_suffix for name in sp_set])
                not_existing_orig_plans = set(sp_names_orig) - all_sub_plans_of_from_lp
                if not_existing_orig_plans:
                    self.subplans.setFocus()
                    if len(not_existing_orig_plans) == 1:
                        msg = MSGR("There is no sub-plan named '%%s' under <%s>") % self.variant.labels().from_lp
                    else:
                        msg = MSGR("There are no sub-plans named '%%s' under <%s>") % self.variant.labels().from_lp
                    return msg % "' or '".join(not_existing_orig_plans)
                orig_plans_with_opt = [sp for sp in sp_names_orig if sub_plan_has_opt_solutions(from_lp_name, sp)]
                if orig_plans_with_opt:
                    self.subplans.setFocus()
                    if len(orig_plans_with_opt) == 1:
                        msg = MSGR("The sub-plan '%%s' under <%s> has solutions") % self.variant.labels().from_lp
                    else:
                        msg = MSGR("The sub-plans '%%s' under <%s> have solutions") % self.variant.labels().from_lp
                    return msg % "' and '".join(orig_plans_with_opt)
                sp_names_moved = sorted([name + moved_suffix for name in sp_set]) if to_lp_name else []
                if to_lp_name:
                    not_existing_moved_plans = set(sp_names_moved) - all_sub_plans_of_to_lp
                    if not_existing_moved_plans:
                        self.subplans.setFocus()
                        if len(not_existing_moved_plans) == 1:
                            msg = MSGR("There is no sub-plan named '%%s' under <%s>") % self.variant.labels().to_lp
                        else:
                            msg = MSGR("There are no sub-plans named '%%s' under <%s>") % self.variant.labels().to_lp
                        return msg % MSGR("' or '").join(not_existing_moved_plans)
                    moved_plans_with_opt = [sp for sp in sp_names_moved if sub_plan_has_opt_solutions(to_lp_name, sp)]
                    if moved_plans_with_opt:
                        self.subplans.setFocus()
                        if len(moved_plans_with_opt) == 1:
                            msg = MSGR("The sub-plan '%%s' under <%s> has solutions") % self.variant.labels().to_lp
                        else:
                            msg = MSGR("The sub-plans '%%s' under <%s> have solutions") % self.variant.labels().to_lp
                        return msg % "' and '".join(moved_plans_with_opt)
            else:  # regex used
                sp_names_orig = sorted(x for x in all_sub_plans_of_from_lp
                                       if x.endswith(orig_suffix) and
                                       re.search(sp_value, x[:-len(orig_suffix)]) and
                                       not sub_plan_has_opt_solutions(from_lp_name, x))
                if to_lp_name:
                    sp_names_moved = sorted(x for x in all_sub_plans_of_to_lp
                                            if x.endswith(moved_suffix) and
                                            re.search(sp_value, x[:-len(moved_suffix)]) and
                                            not sub_plan_has_opt_solutions(to_lp_name, x))
                else:
                    sp_names_moved = []
                if not (sp_names_orig or sp_names_moved):
                    self.subplans.setFocus()
                    return MSGR("No sub-plans without solutions match regular expression and suffix")
            msg = get_refresh_plans_message(sp_names_orig, sp_names_moved, self.variant)
            msg += MSGR("\n\nContinue?")
            if not Gui.GuiYesNo("VERIFY_PLANS", msg):
                self.subplans.setFocus()
                return MSGR("You pressed No")
            self.sub_plans_to_refresh_orig_lp_as_string = ",".join(sp_names_orig)
            self.sub_plans_to_refresh_moved_lp_as_string = ",".join(sp_names_moved)
            return

        # plan creation
        if use_regex:
            sp_set = set(x for x in all_sub_plans_of_from_lp if re.search(sp_value, x))
            if not sp_set:
                self.subplans.setFocus()
                return MSGR("No existing sub-plans match the regular expression")
        else:
            not_existing_start_plans = sp_set - all_sub_plans_of_from_lp
            if not_existing_start_plans:
                self.subplans.setFocus()
                if len(not_existing_start_plans) == 1:
                    msg = MSGR("There is no sub-plan named '%%s' under <%s>") % self.variant.labels().from_lp
                else:
                    msg = MSGR("There are no sub-plans named '%%s' under <%s>") % self.variant.labels().from_lp
                return msg % MSGR("' or '").join(sorted(not_existing_start_plans))
        existing_orig_plans = all_sub_plans_of_from_lp & set(name + orig_suffix for name in sp_set)
        if existing_orig_plans:
            self.orig_suffix.setFocus()
            if len(existing_orig_plans) == 1:
                msg = MSGR("The sub-plan '%%s' already exists under <%s>") % self.variant.labels().from_lp
            else:
                msg = MSGR("The sub-plans '%%s' already exist under <%s>") % self.variant.labels().from_lp
            return msg % MSGR("' and '").join(sorted(existing_orig_plans))
        if to_lp_name:
            existing_move_plans = all_sub_plans_of_to_lp & set(name + moved_suffix for name in sp_set)
            if existing_move_plans:
                self.moved_suffix.setFocus()
                if len(existing_move_plans) == 1:
                    msg = MSGR("The sub-plan '%%s' already exists under <%s>") % self.variant.labels().to_lp
                else:
                    msg = MSGR("The sub-plans '%%s' already exist under <%s>") % self.variant.labels().to_lp
                return msg % MSGR("' and '").join(sorted(existing_move_plans))
            msg = get_move_plans_message(sp_set, orig_suffix, moved_suffix, self.variant)
        else:
            msg = get_create_kpi_plans_message(sp_set, orig_suffix, self.variant)
        msg += MSGR("\n\nContinue?")
        if not Gui.GuiYesNo("VERIFY_PLANS", msg):
            self.subplans.setFocus()
            return MSGR("You pressed No")
        self.sub_plans_to_move_as_string = ",".join(sorted(sp_set))


def sub_plan_has_opt_solutions(lp_name, sp_name):
    return os.path.exists(os.path.join(pcu.lp_top_dir, lp_name, sp_name, "APC_FILES"))


def get_refresh_plans_message(sp_names_orig, sp_names_moved, variant):
    msg = ""
    if sp_names_orig:
        msg += MSGR("The following sub-plan(s) under <%s> will be refreshed:\n ") % variant.labels().from_lp
        msg += "\n ".join(sp_names_orig)
    if sp_names_moved:
        msg += MSGR("\n\nThe following sub-plan(s) under <%s> will be refreshed:\n ") % variant.labels().to_lp
        msg += "\n ".join(sp_names_moved)
    return msg


def get_move_plans_message(sp_names, orig_suffix, moved_suffix, variant):
    msg = MSGR("The following sub-plans will be used or created:\n ")
    max_sp_len = max(map(len, sp_names))
    titles = [MSGR("Source sub-plan under <%s>") % variant.labels().from_lp,
              MSGR("Result of copy under <%s>") % variant.labels().from_lp,
              MSGR("Result of move under <%s>") % variant.labels().to_lp]
    max_lens = map(max, zip(map(len, titles), map(lambda x: max_sp_len + len(x), ("", orig_suffix, moved_suffix))))
    fms = "{0[0]:{1[0]}}  {0[1]:{1[1]}}  {0[2]:{1[2]}}"
    msg += "\n %s\n" % fms.format(titles, max_lens)
    msg += "\n".join(" " + fms.format((x, x + orig_suffix, x + moved_suffix), max_lens) for x in sorted(sp_names))
    return msg


def get_create_kpi_plans_message(sp_names, orig_suffix, variant):
    msg = MSGR("The following sub-plans will be used or created:\n ")
    max_sp_len = max(map(len, sp_names))
    titles = [MSGR("Source sub-plan under <%s>") % variant.labels().from_lp,
              MSGR("Result of copy under <%s>") % variant.labels().from_lp]
    max_lens = map(max, zip(map(len, titles), map(lambda x: max_sp_len + len(x), ("", orig_suffix))))
    fms = "{0[0]:{1[0]}}  {0[1]:{1[1]}}"
    msg += "\n %s\n" % fms.format(titles, max_lens)
    msg += "\n".join(" " + fms.format((x, x + orig_suffix), max_lens) for x in sorted(sp_names))
    return msg


class MyParamSet(Cfh.PathName):

    def __init__(self, form, name, value):
        super(MyParamSet, self).__init__(form, name, 70, value, 2, 2)

    def check(self, txt):
        ret = super(MyParamSet, self).check(txt)
        if ret:
            return ret

        if not os.path.exists(os.path.join(crc_param_dir, txt)):
            return MSGR("There is not parameter set with this name")


class MyAction(Cfh.String):

    only_refresh_plans_value = MSGR("Only refresh plans")
    create_new_plans_value = MSGR("Create new plans")

    def __init__(self, form, name, value):
        Cfh.String.__init__(self, form, name, 0, value)
        self.setMenu(["", self.create_new_plans_value, self.only_refresh_plans_value])
        self.setMandatory(1)
        self.setStyle(Cfh.CfhSChoiceToggle)


class MySubPlanMatchingMethod(Cfh.String):

    regex_value = MSGR("regular expression")
    comma_separated_value = MSGR("comma-separated list of exact names")

    def __init__(self, form, name, value):
        Cfh.String.__init__(self, form, name, 0, value)
        self.setMenu(["", self.comma_separated_value, self.regex_value])
        self.setMandatory(1)
        self.setStyle(Cfh.CfhSChoiceToggle)


if __name__ == "__main__":
    reload(pcu)
    import carmusr.calibration.command_move_or_refresh_plans as me  # @UnresolvedImport
    me.do_it_with_gui("lb")
