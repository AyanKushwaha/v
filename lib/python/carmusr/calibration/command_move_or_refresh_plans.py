"""
Created on 10 Jun 2020

@author: steham
"""


from __future__ import absolute_import
from six.moves import map
from six.moves import zip
import os
import traceback
import re

import Cfh
import Cui
import Gui
import Cps
import Errlog
from Localization import MSGR
import Crs
from jcms.calibration import move_subplan
from jcms.calibration import plan

from jcms.calibration.utils import process_commands_util as pcu
from carmusr.calibration.util import plan_process_steps
from jcms.calibration import form_util
from jcms.calibration.form_util import CachedProperty, FormCheckFailure

crc_param_dir = Crs.CrsGetModuleResource("default", Crs.CrsSearchModuleDef, "CRC_PARAMETERS_DIR")


class LABELS(object):
    from_lp = MSGR("From local plan")
    to_lp = MSGR("To local plan")
    sub_plans = MSGR("Sub-plans to process")
    rule_set_name = MSGR("Name of rule set to apply after move")
    param_file_for_orig_plans = MSGR("Optional parameter file to load for original sub-plans")
    param_file_for_moved_plans = MSGR("Optional parameter file to load for moved sub-plans")
    suffix_for_orig_plans = MSGR("Suffix to add to original sub-plans")
    suffix_for_moved_plans = MSGR("Suffix to add to moved sub-plans")


class LABELSNoToPlan(LABELS):
    from_lp = MSGR("Local plan")
    param_file_for_orig_plans = MSGR("Optional parameter file to load")
    suffix_for_orig_plans = MSGR("Suffix to add to sub-plans")


def get_form_class(variant):
    return {TT: TTMoveRefresh,
            LB: LBMoveRefresh,
            PA: PAMoveRefresh}[variant]


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
        return LABELS if cls.allow_to_plan else LABELSNoToPlan

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

    retcode = form_util.run_form(get_form_class(variant), do_it_ok)
    return retcode


def do_it_ok(form):
    variant = form.variant
    vals = form.return_values()
    only_refesh_plans = form.variant.allow_only_refresh_plans and vals.ACTION == MyAction.only_refresh_plans_value
    args = ("%L",
            variant.key,
            only_refesh_plans,
            vals.FROM_LOCAL_PLAN,
            vals.get('TO_LOCAL_PLAN', None),
            vals.get('RULE_SET_NAME', None),
            vals.get('PARAM_SET_ORIG', None),
            vals.get('PARAM_SET_MOVED', None))

    if only_refesh_plans:
        args += (form.sub_plans_to_refresh_orig_lp_as_string,
                 form.sub_plans_to_refresh_moved_lp_as_string)
    else:
        args += (form.sub_plans_to_move_as_string,
                 vals.ORIG_SUFFIX,
                 vals.get('MOVED_SUFFIX', ''))

    if vals.RUN_IN_BACKGROUND:
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
        self.pps = plan_process_steps.PlanProcessSteps(self.umh)
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
            self.pps.force_open_plan(source_plan_full_name)
            self.pps.save_subplan_as(sp_new_from_full_name)
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
        sp_names_orig = [s for s in sub_plans_to_refresh_orig_lp_as_string.split(",") if s]
        sp_names_moved = [s for s in sub_plans_to_refresh_moved_lp_as_string.split(",") if s]
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
        pps = self.pps

        full_sub_plan_name = os.path.join(self.to_local_plan if has_been_moved else self.from_local_plan, sub_plan_name)
        pps.force_open_plan(full_sub_plan_name)

        if has_been_moved:
            pps.load_rule_set_keep_parameters(self.rule_set_name)

        parameter_file = self.param_set_for_moved_plans if has_been_moved else self.param_set_for_orig_plans
        if parameter_file:
            pps.load_parameters_file(parameter_file)

        if self.variant.set_tt_params:
            if has_been_moved:
                pps.set_rave_parameters(pcu.parameters_to_set_in_moved_tt_plan)
            else:
                pps.set_rave_parameters(pcu.parameters_to_set_in_orig_tt_plan)

        try:
            pps.force_save_subplan(verbose=False)
        except Exception:
            Errlog.log(traceback.format_exc())
            self.umh.add_message(MSGR("Warning. The loaded sub-plan can't be saved. No Custom KPIs are generated."))
            self.umh.add_message("")
            return

        pps.generate_plan_kpis_exclude_hidden()

        if sp_comment:
            pps.set_subplan_comment(sp_comment)

        pps.force_save_subplan()

        msg = MSGR("'{}' is now ready to be analysed. Duration {}.").format(full_sub_plan_name,
                                                                            self.plan_timer.get_time_as_formatted_string())
        self.umh.add_message(msg)
        self.umh.add_message("")


class _MoveRefreshForm(form_util.RememberedForm):
    width = 70

    @property
    def name(self):
        return self.variant.form_name()

    @property
    def title(self):
        return self.variant.title

    def add_elements(self):
        variant = self.variant
        labels = variant.labels()
        self.add(form_util.LocalPlanExisting(self, 'FROM_LOCAL_PLAN'), labels.from_lp)
        self.add_string('SUBPLANS', labels.sub_plans, pcu.MAX_LEN_SUB_PLAN_NAME)

        if variant.allow_regex:
            widget = MySubPlanMatchingMethod(self, 'MATCHING_METHOD',
                                             MySubPlanMatchingMethod.comma_separated_value)
            self.add(widget, MSGR("   matching method"))
        if variant.allow_to_plan:
            self.add(form_util.LocalPlanExisting(self, 'TO_LOCAL_PLAN'), labels.to_lp, mandatory=False)
            default_rule_set = os.path.basename(Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "CrcDefaultRuleSet"))
            self.add_rule_set_name('RULE_SET_NAME', labels.rule_set_name, default_rule_set)
        if variant.use_param_sets:
            widget = MyParamSet(self, "PARAM_SET_ORIG", "")
            self.add(widget, labels.param_file_for_orig_plans, mandatory=False)
            if variant.allow_to_plan:
                widget = MyParamSet(self, "PARAM_SET_MOVED", "")
                self.add(widget, labels.param_file_for_moved_plans, mandatory=False)
        self.add_filename('ORIG_SUFFIX', labels.suffix_for_orig_plans,
                          pcu.MAX_LEN_PLAN_NAME_SUFFIX, initial_value='_p')
        if variant.allow_to_plan:
            self.add_filename('MOVED_SUFFIX', labels.suffix_for_moved_plans,
                              pcu.MAX_LEN_PLAN_NAME_SUFFIX, initial_value=variant.moved_suffix_default)

        if variant.allow_only_refresh_plans:
            widget = MyAction(self, "ACTION", MyAction.create_new_plans_value)
            self.add_empty()
            self.add(widget, "ACTION", MSGR("Action"))
        self.add_empty()
        self.add_toggle('RUN_IN_BACKGROUND', MSGR("Run in background"), pcu.default_value_for_run_in_background)
        self.add_ok()
        self.add_cancel()
        self.add_reset()
        self.add_default()

    def refresh_lists(self):
        if hasattr(self, "RULE_SET_NAME"):
            self.RULE_SET_NAME.refresh_menu()

    class LazyCachedValues(object):
        def __init__(self, form):
            self.form = form

        @CachedProperty
        def from_lp_name(self):
            return self.form.FROM_LOCAL_PLAN.getValue()

        @CachedProperty
        def to_lp_name(self):
            return self.form.TO_LOCAL_PLAN.getValue() if hasattr(self.form, "TO_LOCAL_PLAN") else ""

        @CachedProperty
        def orig_suffix(self):
            return self.form.ORIG_SUFFIX.getValue()

        @CachedProperty
        def moved_suffix(self):
            return self.form.MOVED_SUFFIX.getValue() if hasattr(self.form, "MOVED_SUFFIX") else ""

        @CachedProperty
        def sp_value(self):
            return self.form.SUBPLANS.getValue()

        @CachedProperty
        def use_regex(self):
            form = self.form
            return form.variant.allow_regex and form.MATCHING_METHOD.getValue() == MySubPlanMatchingMethod.regex_value

        @CachedProperty
        def only_refresh_plans(self):
            return self.form.variant.allow_only_refresh_plans and self.form.ACTION.getValue() == MyAction.only_refresh_plans_value

        @CachedProperty
        def all_sub_plans_of_from_lp(self):
            return set(Cui.CuiSubPlanList(self.from_lp_name))

    def check(self, arg):
        v = self.LazyCachedValues(self)
        if v.from_lp_name == v.to_lp_name:
            self.TO_LOCAL_PLAN.setFocus()
            return MSGR("The local plans can't be the same")
        try:
            if v.only_refresh_plans:
                self._check_before_refresh(v)
            else:
                self._check_before_move(v)
        except FormCheckFailure as f:
            msg = f.args[0]
            return msg
        return super(_MoveRefreshForm, self).check(arg)

    def _check_compile_re(self, re_string, field):
        try:
            return re.compile(re_string)
        except Exception as ex:
            field.setFocus()
            raise FormCheckFailure(MSGR("Invalid regular expression: {}").format(str(ex)))

    def _check_before_refresh(self, v):
        labels = self.variant.labels()
        if not v.use_regex:
            sp_set = self._sp_set_no_regexp(v.sp_value)
            sp_names_orig = sorted([name + v.orig_suffix for name in sp_set])
            self._check_sp_exists(self.SUBPLANS, labels.from_lp, v.from_lp_name, sp_names_orig)
            self._check_no_opt_solutions(self.SUBPLANS, labels.from_lp, v.from_lp_name, sp_names_orig)
            if v.to_lp_name:
                sp_names_moved = sorted([name + v.moved_suffix for name in sp_set])
                self._check_sp_exists(self.SUBPLANS, labels.to_lp, v.to_lp_name, sp_names_moved)
                self._check_no_opt_solutions(self.SUBPLANS, labels.to_lp, v.to_lp_name, sp_names_moved)
            else:
                sp_names_moved = []
        else:
            sp_regex = self._check_compile_re(v.sp_value, self.SUBPLANS)
            all_sub_plans_of_to_lp = set(Cui.CuiSubPlanList(v.to_lp_name))
            sp_names_orig = self._matching_subplans_without_solutions(v.from_lp_name,
                                                                      v.all_sub_plans_of_from_lp,
                                                                      v.orig_suffix,
                                                                      sp_regex)
            if v.to_lp_name:
                sp_names_moved = self._matching_subplans_without_solutions(v.to_lp_name,
                                                                           all_sub_plans_of_to_lp,
                                                                           v.moved_suffix,
                                                                           sp_regex)
            else:
                sp_names_moved = []
            if not (sp_names_orig or sp_names_moved):
                self.SUBPLANS.setFocus()
                raise FormCheckFailure(MSGR("No sub-plans without solutions match regular expression and suffix"))
        msg = get_refresh_plans_message(sp_names_orig, sp_names_moved, self.variant)
        self._check_gui_verify_plans_continue(msg)
        self.sub_plans_to_refresh_orig_lp_as_string = ",".join(sp_names_orig)
        self.sub_plans_to_refresh_moved_lp_as_string = ",".join(sp_names_moved)

    def _check_before_move(self, v):
        labels = self.variant.labels()
        if v.use_regex:
            sp_regex = self._check_compile_re(v.sp_value, self.SUBPLANS)
            sp_set = set(x for x in v.all_sub_plans_of_from_lp if sp_regex.search(x))
            if not sp_set:
                self.SUBPLANS.setFocus()
                raise FormCheckFailure(MSGR("No existing sub-plans match the regular expression"))
        else:
            sp_set = self._sp_set_no_regexp(v.sp_value)
            self._check_sp_exists(self.SUBPLANS, labels.from_lp, v.from_lp_name, sp_set)
        self._check_sp_not_exists(self.ORIG_SUFFIX, labels.from_lp, v.from_lp_name,
                                  subplans=set(name + v.orig_suffix for name in sp_set),
                                  existing_subplans=v.all_sub_plans_of_from_lp)
        if v.to_lp_name:
            self._check_sp_not_exists(self.MOVED_SUFFIX, labels.to_lp, v.to_lp_name,
                                      subplans=set(name + v.moved_suffix for name in sp_set),
                                      existing_subplans=v.all_sub_plans_of_from_lp)
            msg = get_move_plans_message(sp_set, v.orig_suffix, v.moved_suffix, self.variant)
        else:
            msg = get_create_kpi_plans_message(sp_set, v.orig_suffix, self.variant)
        self._check_gui_verify_plans_continue(msg)
        self.sub_plans_to_move_as_string = ",".join(sorted(sp_set))

    def _sp_set_no_regexp(self, sp_value):
        return set(sp for sp in (x.strip() for x in sp_value.split(',')) if sp)

    def _check_gui_verify_plans_continue(self, msg):
        msg += MSGR("\n\nContinue?")
        if not Gui.GuiYesNo("VERIFY_PLANS", msg):
            self.SUBPLANS.setFocus()
            raise FormCheckFailure(MSGR("You pressed No"))

    def _check_sp_exists(self, focus_widget, lp_label, lp_name, sp_names):
        lp_sps = set(Cui.CuiSubPlanList(lp_name))
        not_existing = set(sp_names) - lp_sps
        if not_existing:
            focus_widget.setFocus()
            if len(not_existing) == 1:
                msg = MSGR("There is no sub-plan named '{}' under <{}>")
            else:
                msg = MSGR("There are no sub-plans named '{}' under <{}>")
            raise FormCheckFailure(msg.format("' or '".join(sorted(not_existing)), lp_label))

    def _check_no_opt_solutions(self, focus_widget, lp_label, lp_name, sp_names):
        plans_with_opt = [sp for sp in sp_names if sub_plan_has_opt_solutions(lp_name, sp)]
        if plans_with_opt:
            focus_widget.setFocus()
            if len(plans_with_opt) == 1:
                msg = MSGR("The sub-plan '{}' under <{}> has solutions")
            else:
                msg = MSGR("The sub-plans '{}' under <{}> have solutions")
            raise FormCheckFailure(msg.format("' and '".join(sorted(plans_with_opt)), lp_label))

    def _matching_subplans_without_solutions(self, lp_name, subplans, suffix, regexp):
        return sorted(sp for sp in subplans
                      if sp.endswith(suffix) and
                      regexp.search(sp[:-len(suffix)]) and
                      not sub_plan_has_opt_solutions(lp_name, sp))

    def _check_sp_not_exists(self, focus_widget, lp_label, lp_name, subplans, existing_subplans):
        already_existing = existing_subplans & subplans
        if already_existing:
            focus_widget.setFocus()
            if len(already_existing) == 1:
                msg = MSGR("The sub-plan '{}' already exists under <{}>")
            else:
                msg = MSGR("The sub-plans '{}' already exist under <{}>")
            msg = msg.format(MSGR("' and '").join(sorted(already_existing)), lp_label)
            raise FormCheckFailure(msg)


class TTMoveRefresh(_MoveRefreshForm):
    variant = TT


class LBMoveRefresh(_MoveRefreshForm):
    variant = LB


class PAMoveRefresh(_MoveRefreshForm):
    variant = PA


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
    max_lens = list(map(max, zip(map(len, titles), [max_sp_len + len(x) for x in ("", orig_suffix, moved_suffix)])))
    fms = "{0[0]:{1[0]}}  {0[1]:{1[1]}}  {0[2]:{1[2]}}"
    msg += "\n %s\n" % fms.format(titles, max_lens)
    msg += "\n".join(" " + fms.format((x, x + orig_suffix, x + moved_suffix), max_lens) for x in sorted(sp_names))
    return msg


def get_create_kpi_plans_message(sp_names, orig_suffix, variant):
    msg = MSGR("The following sub-plans will be used or created:\n ")
    max_sp_len = max(map(len, sp_names))
    titles = [MSGR("Source sub-plan under <%s>") % variant.labels().from_lp,
              MSGR("Result of copy under <%s>") % variant.labels().from_lp]
    max_lens = list(map(max, zip(map(len, titles), [max_sp_len + len(x) for x in ("", orig_suffix)])))
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
