'''
Created on 10 Jun 2020

@author: steham
'''

from tempfile import NamedTemporaryFile
from tempfile import mktemp
import os
import traceback

import Cfh
import Cui
import Cps
import Gui
import Errlog
from Localization import MSGR
import Crs
from jcms.calibration import move_subplan
from jcms.calibration import plan
from __main__ import exception as StudioError  # @UnresolvedImport

import carmusr.calibration.util.process_commands_util as pcu
import carmusr.calibration.mappings as mappings


TITLE = MSGR("Create Single Legs Sub-plan for Timetable Analysis")


class LABELS:
    from_lp = MSGR("From local plan")
    to_lp = MSGR("To local plan")
    sp_name = MSGR("Name of created sub-plan")
    rule_set_name = MSGR("Use this rule set in created sub-plan")
    master_sp = MSGR("Sub-plan to get e-tables and parameters from")


def do_it_with_gui():
    """
    This is the only "exported" function.
    Call it with bypass-wrapper if you need a silent version.
    Return values similar to Cui functions to allow adequate bypassing.
    """
    Cui.CuiPlanManager(Cui.gpc_info, 0)
    # Ask for plan names
    form = MyForm()
    form.show(1)
    if form.loop() != Cfh.CfhOk:
        return 1

    current_params_full_file_name = NamedTemporaryFile(delete=False).name
    Cui.CuiCrcSaveParameterSet(Cui.gpc_info, None, current_params_full_file_name)
    # Add the magic required first line 'SECTION rules' to make it possible to use the file as a subplanRules file.
    os.system("sed -i '1i SECTION rules' %s" % current_params_full_file_name)

    args = ("%L",
            form.from_local_plan.valof(),
            form.to_local_plan.valof(),
            form.sub_plan_name.valof(),
            form.master_sub_plan.valof(),
            form.rule_set_name.valof(),
            current_params_full_file_name)

    if form.run_in_background.valof() if hasattr(form, "run_in_background") else True:
        cmd = "".join(['$CARMSYS/bin/studio -l %E -d -p ',
                       '"PythonEvalExpr(\\"__import__(\\\\\\"%s\\\\\\",' % __name__,
                       'fromlist=[None])._do_it_in_batch(',
                       ','.join(['\\\\\\"%s\\\\\\"' % arg if isinstance(arg, str) else repr(arg) for arg in args]),
                       ')\\")"'])

        return min(0, Cps.Spawn(cmd, TITLE, "s", pcu.CpsHandler(TITLE)))
    else:
        if plan.local_plan_is_loaded() and not Gui.GuiYesNo("TT_WARNING",
                                                            MSGR("The currently loaded plans will silently be closed by the command. Continue?")):
            return 1
        return _do_it(*args)


def _do_it_in_batch(*args):
    ret = _do_it(*args)
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT | Cui.CUI_EXIT_ERROR if ret else Cui.CUI_EXIT_SILENT)


def _do_it(user_messages_file_path, from_local_plan, to_local_plan, sub_plan_name, master_sub_plan,
           rule_set_name, current_params_full_file_name):

    umh = pcu.UserMessagesHandler(user_messages_file_path)
    try:
        all_timer = pcu.MySimpleTimer()
        from_sub_plan_full_path = mktemp("", sub_plan_name + "_tmp_", os.path.join(pcu.lp_top_dir, from_local_plan))
        from_sub_plan_name = os.path.basename(from_sub_plan_full_path)
        from_sub_plan_full_name = os.path.join(from_local_plan, from_sub_plan_name)
        to_sub_plan_full_name = os.path.join(to_local_plan, sub_plan_name)
        len_longest_label = max(len(v) for n, v in LABELS.__dict__.items() if not n.startswith("__"))

        def my_padded_label(label):
            return label + "." * (len_longest_label - len(label))

        umh.add_message(MSGR("Parameters:"), 0)
        umh.add_message("%s: %s" % (my_padded_label(LABELS.from_lp), from_local_plan))
        umh.add_message("%s: %s" % (my_padded_label(LABELS.to_lp), to_local_plan or "-"))
        umh.add_message("%s: %s" % (my_padded_label(LABELS.sp_name), sub_plan_name))
        umh.add_message("%s: %s" % (my_padded_label(LABELS.rule_set_name), rule_set_name or "-"))
        umh.add_message("%s: %s" % (my_padded_label(LABELS.master_sp), master_sub_plan or "-"))
        umh.add_message("", 0)
        umh.add_message(MSGR("Log:"), 0)

        umh.add_message(MSGR("Load the local plan '%s'.") % from_local_plan)
        plan.open_plan(from_local_plan, confirm=False, silent=True, force=True)

        umh.add_message(MSGR("Create an empty sub-plan."))
        if master_sub_plan:
            sp_comment_ext = MSGR("E-tables and Rave parameters have been copied from the sub-plan\n'{}'.").format(master_sub_plan)
        else:
            sp_comment_ext = ""
        sp_comment = pcu.get_text_for_sub_plan_comment(MSGR("Created"), from_local_plan, TITLE) + sp_comment_ext
        byp = [("FORM", "SUB_PLAN_FORM"),
               ("SUB_PLAN_HEADER_NAME", from_sub_plan_name),
               ("SUB_PLAN_HEADER_COMMENT", sp_comment),
               ("OK", "")]
        Cui.CuiInitEmptySubPlan(byp, Cui.gpc_info)
        umh.add_message(MSGR("Load the rule set '%s'." % rule_set_name))
        Cui.CuiCrcLoadRuleset(Cui.gpc_info, rule_set_name)
        add_all_legs_in_lp_to_sp(umh)
        umh.add_message(MSGR("Save this (temporary) sub-plan as '%s'.") % from_sub_plan_full_name)

        plan.save_subplan()
        Cui.CuiUnloadPlans(Cui.gpc_info, 1)

        # Copy e-tables and Rave parameters from master sub-plan if we have any.
        # NOTE: Etables below SpLocal/.BaseDefinitions and SpLocal/.BaseConstraints are handled by the Studio kernel and must be kept unchanged.
        if master_sub_plan:
            umh.add_message(MSGR("Copy e-tables and Rave parameters from sub-plan '%s' to the temporary sub-plan.") % master_sub_plan)
            master_sub_plan_path = os.path.join(pcu.lp_top_dir, master_sub_plan)
            cmds = ("gtar cf - --exclude .BaseDefinitions --exclude .BaseConstraints -C %s/etable . | gtar xf - -C %s/etable" % (master_sub_plan_path,
                                                                                                                                 from_sub_plan_full_path),
                    "cp %s/subplanRules %s/subplanRules" % (master_sub_plan_path, from_sub_plan_full_path))
        else:
            umh.add_message(MSGR("Copy currently used Rave parameters to the temporary sub-plan."))
            cmds = ("cp %s %s/subplanRules" % (current_params_full_file_name, from_sub_plan_full_path),)

        for cmd in cmds:
            ret = os.system(cmd)
            if ret:
                raise Exception("cmd '%s' returned %s" % (cmd, ret))

        umh.add_message(MSGR("Create another sub-plan '{}' from '{}' using Calibration's 'Move to new version'.").format(to_sub_plan_full_name,
                                                                                                                         from_sub_plan_full_name))
        move_subplan.do_move_to_new_version(from_sub_plan_full_name, to_sub_plan_full_name, False)

        if not mappings.keep_temporary_sub_plan_in_timetable_analysis_script:
            umh.add_message(MSGR("Remove the temporary sub-plan '%s'") % from_sub_plan_full_name)
            cmd = "rm -rf %s" % from_sub_plan_full_path
            ret = os.system(cmd)
            if ret:
                raise Exception("cmd '%s' returned %s" % (cmd, ret))

        sp_comment = pcu.get_text_for_sub_plan_comment(MSGR("Created and moved"), from_local_plan, TITLE) + sp_comment_ext
        open_sp_add_legs_set_params_create_kpis_and_save(to_sub_plan_full_name, pcu.parameters_to_set_in_moved_tt_plan, umh, sp_comment)
        umh.add_message(MSGR("Ready. Duration %s.") % all_timer.get_time_as_formatted_string())
        ret = 0
    except Exception:
        Errlog.log(traceback.format_exc())
        umh.add_message(MSGR("Something unexpected happened. Process STOPPED. See the log file."))
        ret = -1

    os.unlink(current_params_full_file_name)
    pcu.close_message_window()
    umh.show_messages(TITLE + (MSGR(" failed") if ret else MSGR(" succeeded")))

    return ret


def add_all_legs_in_lp_to_sp(umh):
    Cui.CuiSetSubPlanCrewFilterLeg(Cui.gpc_info, 0)
    umh.add_message(MSGR("Add all legs in the local plan to the loaded sub-plan."))
    Cui.CuiSelectLegs(Cui.gpc_info, Cui.CuiNoArea, 1 | 32)  # Add all legs from LP silently.


def open_sp_add_legs_set_params_create_kpis_and_save(sub_plan_name, params_to_change, umh, sp_comment=None):
    umh.add_message(MSGR("Load the sub-plan '%s'.") % sub_plan_name)
    plan.open_plan(sub_plan_name, silent=True)
    pcu.set_rave_parameters(umh, params_to_change)
    add_all_legs_in_lp_to_sp(umh)
    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.LegMode, Cui.CuiShowAll)
    umh.add_message(MSGR("Generate Custom KPIs for all legs in the loaded sub-plan."))
    try:
        Cui.CuiGenerateKpis(Cui.gpc_info, Cui.CUI_SILENT, "window")
    except StudioError:
        umh.add_message(MSGR("Warning. Generation of Custom KPIs failed."))

    if sp_comment:
        Cui.CuiSetSubPlanComment(Cui.gpc_info, sp_comment)

    umh.add_message(MSGR("Save the sub-plan."))
    plan.save_subplan()
    msg = MSGR("'{}' is now ready to be analysed.").format(sub_plan_name)
    umh.add_message(msg)
    umh.add_message("")


class MyForm(Cfh.Box):

    the_instance = None

    def __new__(cls):
        if cls.the_instance is None:
            cls.the_instance = Cfh.Box.__new__(cls)
            cls._my_init(cls.the_instance)
        else:
            cls.the_instance.rule_set_name.refresh_menu()
        return cls.the_instance

    def __init__(self):
        pass

    def _my_init(self):
        form_name = "TTA_PROCESS_FORM"
        super(MyForm, self).__init__(form_name)

        layout = ["FORM;%s;%s" % (form_name, TITLE),
                  "COLUMN;70"]

        self.from_local_plan = pcu.LocalPlanName(self, "FROM_LOCAL_PLAN", "")
        self.from_local_plan.setMandatory(1)
        layout.append("FIELD;FROM_LOCAL_PLAN;%s" % LABELS.from_lp)

        self.to_local_plan = pcu.LocalPlanName(self, "TO_LOCAL_PLAN", "")
        self.to_local_plan.setMandatory(1)
        layout.append("FIELD;TO_LOCAL_PLAN;%s" % LABELS.to_lp)

        self.sub_plan_name = Cfh.FileName(self, "SUBPLAN_NAME", pcu.MAX_LEN_SUB_PLAN_NAME, "timetable_analysis")
        self.sub_plan_name.setMandatory(1)
        layout.append("FIELD;SUBPLAN_NAME;%s" % LABELS.sp_name)

        default_rule_set = os.path.basename(Crs.CrsGetModuleResource("config", Crs.CrsSearchModuleDef, "CrcDefaultRuleSet"))
        self.rule_set_name = pcu.RuleSetName(self, "RULE_SET_NAME", default_rule_set)
        layout.append("FIELD;RULE_SET_NAME;%s" % LABELS.rule_set_name)

        self.master_sub_plan = MySubPlanFullName(self, "MASTER_SUBPLAN", "")
        layout.append("FIELD;MASTER_SUBPLAN;%s" % LABELS.master_sp)

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
        to_lp_name = self.to_local_plan.getValue()
        sp_name = self.sub_plan_name.getValue()

        if from_lp_name == to_lp_name:
            self.to_local_plan.setFocus()
            return MSGR("The local plans can't be the same")

        sp_to_full_name = os.path.join(to_lp_name, sp_name)
        if os.path.exists(os.path.join(pcu.lp_top_dir, sp_to_full_name)):
            self.sub_plan_name.setFocus()
            return MSGR("The sub-plan '%s' already exists") % sp_to_full_name

        msg = MSGR("\nThe following sub-plan under <%s> will be created:\n ") % LABELS.to_lp
        msg += " %s\n" % sp_name

        msg += "\n\nContinue?"
        if not Gui.GuiYesNo("VERIFY_PLANS", msg):
            return MSGR("You pressed No")


class MySubPlanFullName(Cfh.PathName):

    def __init__(self, form, name, value):
        super(MySubPlanFullName, self).__init__(form, name, pcu.MAX_LEN_LOCAL_PLAN_NAME + pcu.MAX_LEN_SUB_PLAN_NAME, value, 4, 4)

    def check(self, txt):
        txt = txt.replace("  ", "/")
        self.setValue(txt)
        ret = super(MySubPlanFullName, self).check(txt)
        if ret:
            return ret

        if not os.path.exists(os.path.join(pcu.lp_top_dir, txt)):
            return MSGR("There is no sub-plan with this name")


if __name__ == "__main__":
    reload(pcu)
    import carmusr.calibration.command_create_single_legs_plan_for_timetable_analysis as me  # @UnresolvedImport
    me.do_it_with_gui()
