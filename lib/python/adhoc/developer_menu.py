
# [acosta:08/322@13:03] Developer extensions to the menu system.

"""
This menu, called "Developer", contains "the best of" from the Special menu.
Most of the original code for that menu was written by S. Hammar and or P.
Bergsten.

It also adds some other goodies, that I have found being useful.
The basic idea is to have everything in one place, to make it easy to transfer
the menus to a customer's system.

This module also makes use of dynamic menus which makes it possible to activate
it when needed or to change and modify the menus on-the-fly.
"""

import __main__

import os
import re
import stat
import sys
import traceback
import weakref

import Cfh
import Csl
import Crs
import Cui
import Errlog
import Gui

import carmensystems.publisher.api as prt
import carmensystems.rave.api as rave
import utils.mnu # Needed
import utils.mnu as mnu

from subprocess import Popen
from tempfile import mkstemp
from xml.dom.minidom import parse as xml_parse

from __main__ import exception as StudioError
from AbsTime import AbsTime
from BSIRAP import getNameOfTag
from carmstd import cfhExtensions
from Variable import Variable
from tm import TM


object_menus = [
    'LeftDat24CrewCompMode1', 
    'LeftDat24CrewDataMode1', 
    'MainDat24AcCompMode1',
    'MainDat24CrewCompMode1',
    'MainDat24CrewDataMode1',
    'MainDat24CrrMode1',
    'MainDat24LegMode1',
    'MainDat24LegSetCompMode1',
    'MainDat24RtdMode1',
]

general_menus = [
    'LeftDat24CrewCompMode2', 
    'LeftDat24CrewDataMode2', 
    'MainDat24AcCompMode2',
    'MainDat24CrewCompMode2',
    'MainDat24CrewDataMode2',
    'MainDat24CrrMode2',
    'MainDat24LegMode2',
    'MainDat24LegSetCompMode2',
    'MainDat24RtdMode2',
]

editor = 'vim'
geditor = 'gvim'
this_module = 'adhoc.developer_menu'
the_reload_module_name = 'ZZReload'
#menu_file = os.path.join(os.environ['HOME'], 'lib', 'python', 'acotest', 'developer_menu.py')
menu_file = os.path.join(os.environ['CARMUSR'], 'lib', 'python', 'adhoc', 'developer_menu.py')

csl = Csl.Csl()
csl_evaluator = None
python_evaluator = None
rave_evaluator = None


# User supplied additions ================================================{{{1
try:
    from adhoc.ZZmenus import AdditionalObjectMenu
except:
    class AdditionalObjectMenu(mnu.Menu):
        def __init__(self):
            mnu.Menu.__init__(self, 'DEV_MENU_OBJ_ADDITIONAL', (
                    mnu.Title('Additional Stuff'),
                    ), title='Additional Stuff', mnemonic="_A", 
                    tooltip="User supplied menus")


# Menus =================================================================={{{1

# DeveloperMenu ----------------------------------------------------------{{{2
class DeveloperMenu(mnu.Menu):
    """Main menu."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_MENU',
            [
                mnu.Button(title='Log File', action=self.action_logfile,
                    mnemonic="_L", tooltip="View Studio log file"),
                mnu.Button(title='Compile', action=self.action_compile, 
                    accelerator="Ctrl<Key>9", mnemonic="_o", 
                    tooltip="Compile and reload rule set, keep parameters."),
                mnu.Button(title='Reload', action=self.action_reload, 
                    mnemonic="_R", tooltip="Reload rule set, keep parameters."),
                mnu.Separator(),
                RaveMenu('Rave'),
                PythonMenu('Python'),
                CSLMenu('CSL'),
                DataMenu('Data'),
                SearchMenu('Search'),
                MiscMenu('Misc'),
                HelpMenu('Help'),
                MenuMenu('Menus'),
                mnu.Separator(),
                mnu.Button(title='Set Time', action=set_time,
                    mnemonic="_T", accelerator="Ctrl<Key>T", 
                    tooltip="Set value of fundamental.%now% by clicking",
                    potency=Gui.POT_REDO, opacity=Gui.OPA_TRANS),
                mnu.Button(title='Exit Abruptly', action=self.exit_abruptly, mnemonic="_x",
                    tooltip="Exit quickly without saving any data"),
            ], title=title, mnemonic='_v', tooltip="Developer's Tool-box")

    def action_compile(self):
        """Compile current ruleset"""
        from Variable import Variable
        rule_set = Variable("", 100)
        Cui.CuiCrcGetRulesetName(rule_set)
        rule_set = os.path.basename(rule_set.value)
        csl.evalExpr('csl_run_file("compile_rules.csl", "%s", "%s")' % (
            os.path.join(os.environ['CARMUSR'], 'crc', 'source', rule_set),
            rule_set))

    def action_logfile(self):
        #xterm('-title', "Log File", '-e', editor, '-R', '-m', '-n', self.get_log_file_name())
        xterm('-title', "Log File", '-e', editor, '-R', '-m', '-n', self.get_log_file_name(),
                '-c', 'map\ <Leader>F\ :view!<CR>GLO:redraw<CR>:file<CR>:sleep 1<CR><Leader>F', 
                '-c', ':execute "normal" . mapleader . "F"')

    def action_reload(self):
        """Reload stuff"""
        Crs.CrsUpdate()
        csl_exec([
            'CuiApuInit()',
            'CuiReloadTables()',
            'csl_local_string("rule_set", 1000)',
            'csl_local_string("param_file", 1000)',
            'csl_tempnam(param_file)',
            'csl_save_rule_set_parameter_values(param_file)',
            'csl_store_current_rule_set_name(rule_set)',
            'csl_load_rule_set_by_name(rule_set)',
            'csl_read_rule_set_parameter_values(param_file)',
            'csl_unlink(param_file)',
            'CuiRedrawAllAreas(gpc_info, CuiDumpAll)',
            'csl_exit_file(0)',
        ])

    def get_log_file_name(self):
        return os.environ.get('LOG_FILE', 
            os.path.join(os.environ.get('LOG_DIR', os.path.join(os.environ['CARMTMP'], 'logfiles')), 
                "errors.%s.%s" % (os.environ['USER'], os.environ['HOST'])))

    def exit_abruptly(self):
        Cui.CuiExit(Cui.gpc_info, 1)


# DevMenuObject ----------------------------------------------------------{{{2
class DevMenuObject(mnu.Menu):
    """A Menu that is attached to the different object menus."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_MENU_OBJECT', [
            mnu.Button('Show Rule Values...', action=self.rule_values,
                mnemonic="_S", tooltip="Show rule values"),
            mnu.Button('Rave Explorer...', action=self.rave_explorer,
                mnemonic="_R", tooltip="Explore Rave code using Rave IDE"),
            mnu.Button('Rave Evaluator...', action=self.rave_evaluator,
                mnemonic="_E", tooltip="Examine values of rave variables"),
            mnu.Button('Generate Report...', action=self.generate_report,
                mnemonic="_G", tooltip="Generate PRT or CRG report"),
            DynamicReports(),
            AdditionalObjectMenu(),
            ], title=title, mnemonic="_D", tooltip="Developer's tools")

    def rule_values(self):
        Cui.CuiCrcShowValues(Cui.gpc_info, 1)

    def rave_explorer(self):
        PythonRunFile("carmensystems/rave/private/RaveExplorer.py", "0")

    def rave_evaluator(self):
        RaveEvaluator.init_rave_evaluator()

    def generate_report(self):
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        mode = Cui.CuiGetAreaMode(Cui.gpc_info, area)
        d = {
            Cui.NoMode: None,
            Cui.LegMode: 'leg_window_object',
            Cui.RtdMode: 'rtd_window_object',
            Cui.CrrMode: 'crr_window_object',
            Cui.CrewMode: 'crew_window_object',
            Cui.LegSetMode: 'legset_window_object',
            Cui.AcRotMode: 'acrot_window_object',
        }
        dir = d.get(mode, Cui.NoMode)
        if dir == Cui.NoMode:
            cfhExtensions.show("This area has no mode.")
        else: 
            csl.evalExpr('CRG("%s")' % dir)


# DevMenuGeneral ---------------------------------------------------------{{{2
class DevMenuGeneral(mnu.Menu):
    """A Menu that is attached to the different general menus."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_MENU_GENERAL', [
            mnu.Button('Generate Report...', action=self.generate_report,
                mnemonic="_G", tooltip="Generate PRT or CRG report"),
            mnu.Button('Rave Explorer...', action=self.rave_explorer,
                mnemonic="_E", tooltip="Explore Rave code using Rave IDE"),
            mnu.Button('Respect Rave Trips', action=self.respect_rave,
                mnemonic="_R", tooltip='Redraw trip indicators based on Rave'),
            mnu.Menu('DEV_MENU_GEN_ADDITIONAL', (
                mnu.Title('Additional Stuff'),
                    mnu.Button('Non Core Illegalities', action=self.non_core),
                    mnu.Button('Sort after now', action=self.sort_after_now),
                ), title='Additional Stuff', mnemonic="_A", 
                tooltip="User supplied menus"),
            ], title=title, mnemonic="_D", tooltip="Developer's tools")

    def non_core(self):
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiWhichArea, 'WINDOW', 'ZZNonCoreLegalityInfo.py', 0)

    def generate_report(self):
        area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
        mode = Cui.CuiGetAreaMode(Cui.gpc_info, area)
        d = {
            Cui.NoMode: None,
            Cui.LegMode: 'leg_window_general',
            Cui.RtdMode: 'rtd_window_general',
            Cui.CrrMode: 'crr_window_general',
            Cui.CrewMode: 'crew_window_general',
            Cui.LegSetMode: 'legset_window_general',
            Cui.AcRotMode: 'acrot_window_general',
        }
        dir = d.get(mode, Cui.NoMode)
        if dir == Cui.NoMode:
            cfhExtensions.show("This area has no mode.")
        else: 
            csl.evalExpr('CRG("%s")' % dir)

    def rave_explorer(self):
        PythonRunFile("carmensystems/rave/private/RaveExplorer.py", "32")

    def respect_rave(self):
        Cui.CuiUpdateLevelsAccordingToRaveAreaId(Cui.gpc_info, Cui.CuiWhichArea)

    def sort_after_now(self):
        sort_('report_crewlists.%test_sort_after_now%')


# SearchMenu -------------------------------------------------------------{{{2
class SearchMenu(mnu.Menu):
    """Search for code/Selections in plan."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_SEARCH_MENU', [
            mnu.Button('Source Code', action=self.search_code,
                mnemonic="_S", tooltip="Search source code for strings"),
            mnu.Button('Select by Rave Expression...', action=self.search_rave,
                mnemonic="_R", tooltip="Locate objects in plan using Rave"),
            mnu.Button('Select Rule Failures...', action=self.search_rules,
                mnemonic="_F", tooltip="Locate objects in plan that breaks specific rule"),
            ], title=title, mnemonic="_S", 
            tooltip="Search for various objects/strings")

    def search_code(self):
        CodeSearch()

    def search_rave(self):
        RaveSearchBox()

    def search_rules(self):
        RuleFailureBox()


# MiscMenu ---------------------------------------------------------------{{{2
class MiscMenu(mnu.Menu):
    """Menu entries that don't fit elsewhere."""
    class trace:
        def __init__(self, tracelevel):
            self.tracelevel = tracelevel

        def __call__(self):
            return Cui.CuiSetTraceLevel(self.tracelevel)


    def __init__(self, title):
        trace_buttons = [mnu.Button("%d" % x, action=self.trace(x))
                for x in xrange(9)]
        mnu.Menu.__init__(self, 'DEV_MISC_MENU', [
            mnu.Button("Xterm", action=self.xterm, mnemonic="_X",
                tooltip="Open Xterm command window"),
            mnu.Button("Process Manager", action=self.proc_mgr, mnemonic="_P",
                tooltip="View and control background processes"),
            mnu.Button("SGE qmon", action=self.qmon, mnemonic="_q",
                tooltip="View and control SGE (Sun Grid Engine) jobs"),
            mnu.Button("Show Colours", action=self.show_colors, mnemonic="_C",
                tooltip="List available Studio colors"),
            mnu.Button("Show Environment", action=self.show_env, mnemonic="_E",
                tooltip="Show Studio's environment"),
            mnu.Menu('DEV_MISC_TRACE_MENU', trace_buttons, title="Set Tracelevel",
                mnemonic="_T", 
                tooltip="Set Studio tracelevel. NOTE: a large value means excessive logging"),
            ], title=title, mnemonic="_i", tooltip="Miscellaneous functions")

    def xterm(self):
        xterm('-title', "XTerm - (%s) %s" % (
            os.environ.get('CarmRelease', 'Unknown Release'),
            os.environ.get('CARMUSR', 'Unknown CARMUSR')))

    def show_env(self):
        xterm('-title', 'Environment', '-e', "env | sort | %s -" % editor)

    def gen_report(self, title):
        csl.evalExpr('CRG("%s")' % title)

    def qmon(self):
        Popen(['qmon'])

    def proc_mgr(self):
        csl.evalExpr("xcps_childs_info()")

    def show_colors(self):
        sf = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef, "PRTReportFormat")
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", "PDF", "")
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiNoArea, 'plan', 'developer_menu.py')
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", sf, "")


# RaveMenu ---------------------------------------------------------------{{{2
class RaveMenu(mnu.Menu):
    """Rave code/rule sets."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_RAVE_MENU', [
            mnu.Button('Rave Evaluator...', action=self.rave_evaluator,
                mnemonic="_E", tooltip="Examine values of rave variables"),
            mnu.Button('Rule Source Manager...', action=self.rave_manager,
                mnemonic="_S", tooltip="Recompile/View/Edit rule sets"),
            mnu.Button('Rule Set Manager...', action=self.ruleset_manager,
                mnemonic="_e", tooltip="Choose rule set"),
            mnu.Button('Rave IDE', action=self.rave_ide,
                mnemonic="_I", 
                tooltip="Edit Rave source using Integrated Development Environment"),
            mnu.Button('Rave KPI', action=self.rave_kpi, 
                mnemonic="_K",
                tooltip="Run Rave Key Performance Index measurements", 
                menuMode='RuleSetLoaded'),
            mnu.Button('Quick reload', action=self.quick_reload, 
                mnemonic="_Q",
                tooltip="Run Rave Key Performance Index measurements", 
                menuMode='RuleSetLoaded'),
            mnu.Menu('DEV_RAVE_PROFILER_MENU', [
                mnu.Button('Start', menuMode="RaveProfilerRunnable",
                    action=self.prof_start, 
                    mnemonic="_t",
                    tooltip="Start profiling or resume profiling after Stop"),
                mnu.Button('Stop', menuMode="RaveProfilerRunning",
                    mnemonic="_o", action=self.prof_stop, 
                    tooltip="Stop profiling"),
                mnu.Button('Save', menuMode="RaveProfilerStopped", 
                    mnemonic="_S", action=self.prof_save, 
                    tooltip="Save profile data on file with default name"),
                mnu.Button('Save as...', menuMode="RaveProfilerStopped",
                    mnemonic="_a", action=self.prof_save_as, 
                    tooltip="Save profile data on file"),
                mnu.Button('Reset', menuMode="RaveProfilerResettable",
                    mnemonic="_R", action=self.prof_reset, 
                    tooltip="Reset profiler discarding unsaved data"),
                ], title='Rave Profiler', mnemonic="_P", tooltip="Rave profiling",
                    menuMode="RaveProfilerAvailable"),
            ], title=title, mnemonic="_v", tooltip="Rave tools")

    def quick_reload(self):
        Crs.CrsUpdate()
        csl_exec([
            'csl_local_string("rule_set", 1000)',
            'csl_local_string("param_file", 1000)',
            'csl_tempnam(param_file)',
            'csl_save_rule_set_parameter_values(param_file)',
            'csl_store_current_rule_set_name(rule_set)',
            'csl_load_rule_set_by_name(rule_set)',
            'csl_read_rule_set_parameter_values(param_file)',
            'csl_unlink(param_file)',
            'csl_exit_file(0)',
        ])

    def prof_reset(self):
        # These functions don't seem to be available from module Cui...
        csl.evalExpr('CuiRaveProfilerReset()')

    def prof_save(self):
        csl.evalExpr('CuiRaveProfilerSave()')

    def prof_save_as(self):
        csl.evalExpr('CuiRaveProfilerSave(3, "", 1)')

    def prof_start(self):
        csl.evalExpr('CuiRaveProfilerResume()')

    def prof_stop(self):
        csl.evalExpr('CuiRaveProfilerPause()')

    def rave_ide(self):
        PythonRunFile("carmensystems/rave/private/raveide.py")

    def rave_kpi(self):
        Cui.CuiRaveKPI(Cui.gpc_info, 1, 6)

    def rave_manager(self):
        fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.cfm')
        l = open(os.path.expandvars("$CARMSYS/data/form/CFM_RuleFiles")).read()
        of = os.fdopen(fd, "w")
        l = l.replace("LPIR", "LECDPNIR", 1)
        of.write(l)
        of.close()
        Cui.CFM(fn)
        os.unlink(fn)

    def rave_evaluator(self):
        RaveEvaluator.init_rave_evaluator()

    def ruleset_manager(self):
        Cui.CFM("CFM_RuleSets")


# CSLMenu ----------------------------------------------------------------{{{2
class CSLMenu(mnu.Menu):
    """Run/handle CSL scripts."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_CSL_MENU', [
            mnu.Button('CSL Manager...', action=self.csl_manager,
                mnemonic="_M", tooltip="Manage CSL code"),
            mnu.Button('CSL Evaluator...', action=self.csl_evaluator,
                mnemonic="_E", tooltip="Run CSL commands"),
            ], title=title, mnemonic="_C", 
            tooltip="Carmen Script Language tools")

    def csl_manager(self):
        fd, fn = mkstemp()
        f = os.fdopen(fd, "w")
        layout = (
                'CSL Manager;LENCDIPRR;',
                'CARMUSR/menu_scripts;$CARMUSR/menu_scripts;DIR_EXEC_FUNC;csl_run_file("%F")',
                'CARMUSR/bin(Shell);;$CARMUSR/bin;DIR_EXEC;%F;Run',
                'EXEC_BUTTON;Run;Make executable',
                """DEFAULT_EXEC_DISABLE;DEFAULT_EXEC_FUNC;PythonEvalExpr("%s.make_executable('%%F')")""" % (
                    this_module),
                )
        print >>f, '\n'.join(layout)
        f.close()
        try:
            Cui.CFM(fn)
            os.unlink(fn)
        except:
            pass

    def csl_evaluator(self):
        global csl_evaluator
        if csl_evaluator is None:
            csl_evaluator = CSLEvaluator()
        csl_evaluator.show(True)


# PythonMenu -------------------------------------------------------------{{{2
class PythonMenu(mnu.Menu):
    """Run/handle Python scripts."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_PYTHON_MENU', [
            mnu.Button('Python Manager...', action=self.python_manager,
                mnemonic="_M", tooltip="Reload/Run/Edit/View Python code"),
            mnu.Button('Python Evaluator...', action=self.python_evaluator,
                mnemonic="_E", tooltip="Run Python commands"),
            mnu.Button('Reload Modules', action=python_reload,
                accelerator="Ctrl<Key>R", opacity=Gui.OPA_TRANS,
                potency=Gui.POT_DO, mnemonic="_R", 
                tooltip="Reload Python modules from the reload list"),
            mnu.Button('Edit Reload List', action=self.python_reload_list,
                mnemonic="_E", tooltip="Edit the reload list"),
            ], title=title, mnemonic="_P", tooltip="Python tools")

    def python_manager(self):
        PythonCodeManager().run()

    def python_evaluator(self):
        global python_evaluator
        if python_evaluator is None:
            python_evaluator = PythonEvaluator()
        python_evaluator.show(True)

    def python_reload_list(self):
        reload_file = os.path.join(os.environ['CARMUSR'], 'lib', 'python', the_reload_module_name + '.py')
        if not os.path.exists(reload_file):
            f = open(reload_file, "w")
            print >>f, "modlist = ["
            print >>f, "]"
            f.close()
        xterm('-e', editor, reload_file)


# HelpMenu ---------------------------------------------------------------{{{2
class HelpMenu(mnu.Menu):
    """Some man pages/help files."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_HELP_MENU', [
            mnu.Button('Keywords etc.', action=self.keywords, mnemonic="_K", 
                tooltip="Rave keywords, contexts, transforms, etc."),
            mnu.Button('API man Pages', action=self.api_man, mnemonic="_A",
                tooltip="Show some of the API Documentation"),
            mnu.Button('DAVE man Pages', action=self.dave_man, mnemonic="_D",
                tooltip="Show DAVE API Documentation"),
            ], title=title, mnemonic="_H", tooltip="Show help developer's help files")

    def keywords(self):
        PythonRunFile("ConfigHelp.py")

    def api_man(self):
        self.open_browser(os.path.expandvars(
            "file://$CARMUSR/current_carmsys_cas/data/doc/apidoc/index.html"
        ))

    def dave_man(self):
        self.open_browser(os.path.expandvars(
            "file://$CARMUSR/current_carmsys_cct/data/doc/dave/apidocs/index.html"
        ))

    def open_browser(self, url):
        Popen(['firefox', '--display', os.path.expandvars("$DISPLAY"), url])


# DataMenu ---------------------------------------------------------------{{{2
class DataMenu(mnu.Menu):
    """Database/Model"""
    fn = os.path.join(os.environ['CARMTMP'], 'dev_menu_entities.tmp')

    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_DATA_MENU', [
            mnu.Button('TableManager', action=self.tablemanager,
                mnemonic="_T", tooltip="Start model table manager"),
            mnu.Button('SQL Commands', action=self.sql_queries, mnemonic="_S",
                tooltip="Open command window where SQL commands can be entered"),
            ], title=title, mnemonic="_D", tooltip="Data storage tools")

    def tablemanager(self):
        import StartTableEditor
        StartTableEditor.StartTableEditor([])

    def sql_queries(self):
        from tm import TM
        fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.sql')
        f = os.fdopen(fd, "w")
        srvname = TM.getConnStr().split('/')[-1]
        schema = TM.getSchemaStr()
        f.write("-- dbext:type=ORA:user=%s:passwd=%s:srvname=%s\n" % (schema, schema, srvname))
        f.close()
        xterm('-e', editor, fn)


# MenuMenu ---------------------------------------------------------------{{{2
class MenuMenu(mnu.Menu):
    """Menu handling."""
    def __init__(self, title):
        mnu.Menu.__init__(self, 'DEV_MENU_MENU', [
            mnu.Button('Reload this Menu', action=self.reload,
                mnemonic="_R", tooltip="Reload this menu"),
            mnu.Button('Edit this Menu', action=self.edit,
                mnemonic="_E", tooltip="Edit the developer's menu"),
            mnu.Button('Add Debug Menus', action=self.add_debug_menus,
                mnemonic="_D", tooltip="Add additional Studio debug menus"),
            mnu.Button('Show Menus', action=self.show_menus,
                mnemonic="_S", tooltip="Show available Studio menus"),
            mnu.Button('Show Menustates', action=self.show_menustates,
                mnemonic="_M", tooltip="Show available states for context sensitive menus"),
            ], title=title, mnemonic="_M", tooltip="Menu system maintentance")
        self.menufile = menu_file

    def add_debug_menus(self):
        import utils.mnu
        import adhoc.debug_menu

    def edit(self):
        xterm('-e', editor, self.menufile)

    def reload(self):
        do_reload(this_module)
        PythonRunFile(self.menufile)

    def show_menus(self):
        csl_exec([
            'csl_local_string("menu_file", 100, "")',
            'csl_local_string("top_text", 100, "")',
            'csl_tempnam(menu_file)',
            'csl_sprintf(top_text, "Carmen Menues from %s", menu_file)',
            'csl_print_menus(menu_file)',
            'csl_show_file(top_text, menu_file, 0)',
            'csl_unlink(menu_file)',
            'end:',
            'csl_exit_file(0)',
            ])

    def show_menustates(self):
        fd, fn = mkstemp(dir=os.environ['CARMTMP'])
        f = os.fdopen(fd, "w")
        import MenuState
        sm = MenuState.theStateManager
        f.write("\n".join(["%-25s: %s" % s for s in
            sorted(list(sm.menuStateDict.items()))]))
        f.close()
        cfhExtensions.showFile(fn, "Menustates")
        os.unlink(fn)


# Report ================================================================={{{1
class Report(prt.Report):
    def create(self):
        d = {}
        for colorname in [Gui.GuiColorNumber2Name(i) for i in xrange(Gui.C_MAX_COLORS)]:
            colorcode = Gui.GuiColorName2ColorCode(colorname)
            d[colorname] = colorcode
        self.setpaper(orientation=prt.LANDSCAPE)
        self.set(font=prt.font(size=12, weight=prt.BOLD))
        u = {}
        for usage, colorname in self.color_resources('default') + self.color_resources('gpc'):
            if colorname in u:
                u[colorname].append(usage)
            else:
                u[colorname] = [usage]
        for colorname in d:
            try:
                ut = ", ".join(u[colorname])
            except KeyError:
                ut = "-"
            self.add(prt.Row(
                prt.Text(colorname, colour=d[colorname], background=d["White"]),
                prt.Text(colorname, colour=d[colorname], background=d["Black"]),
                prt.Text(colorname, colour=d["White"], background=d[colorname]),
                prt.Text(colorname, colour=d["Black"], background=d[colorname]),
                prt.Text(d[colorname], font=prt.font(size=9), background=d["Yellow"]),
                prt.Text(ut, width=400, font=prt.font(size=8)), border=prt.border_frame()))
            self.page()
        self.add("")
        self.add(prt.Text("Note: The colours are the hard coded default ones.",
            "The X-resources are not considered. Bug in Studio.",
            font=prt.font(size=10)))

    def color_resources(self, application):
        z = []
        r = Crs.CrsGetFirstResourceInfo()
        while r:
            if (r.module == "colours" and r.application == application):
                z.append((p.name, p.rawValue))
            r = Crs.CrsGetNextResourceInfo()
        return z


# ABox ==================================================================={{{1
class ABox(Cfh.Box):
    def __init__(self, cfh_id, *a, **k):
        self.__cfh_id = cfh_id
        self.__cfh_id_num = 0
        Cfh.Box.__init__(self, cfh_id, *a, **k)

    def _cfh_id(self):
        self.__cfh_id_num += 1
        return "%s-%d" % (self.__cfh_id, self.__cfh_id_num)


# Buttons ================================================================{{{1
class Buttons:
    """Some common buttons"""
    class Expression(Cfh.String):
        """Let user enter expression."""
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 1000, '')
            self.parent = weakref.ref(parent)
            try:
                self.parent().__class__.menustring
            except:
                self.parent().__class__.menustring = 'Expressions;'
            self.setMenuString(self.parent().__class__.menustring)
            self.setMandatory(True)

        def pushStringOnMenu(self, xpr):
            xpr_s = [x.strip() for x in xpr.split(';')]
            p = self.parent()
            M = p.expr.getMenuString().split(';')
            L = [M[0]] + xpr_s
            L.extend([x for x in M[1:] if x.strip() not in xpr_s])
            menustring = ';'.join(L)
            p.__class__.menustring = menustring
            self.setMenuString(menustring)


    class Area(Cfh.String):
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 0, '1')
            self.parent = weakref.ref(parent)
            self.setMenu(["Window", "1", "2", "3", "4"])
            self.setMenuOnly(True)


    class Mode(Cfh.String):
        mapping = {
            "Trip": ("sp_crrs", Cui.CrrMode),
            "Crew": ("sp_crew", Cui.CrewMode),
            "Duty": ("sp_crew_chains", Cui.RtdMode),  # Slow
            "Leg": ("sp_free_legs", Cui.LegMode),
            "LegSet": ("lp_activity", Cui.LegSetMode),
            "Rotation": ("ac_rotations", Cui.AcRotMode)
        }
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 0, 'Crew')
            self.parent = weakref.ref(parent)
            self.setMenu(["Mode", "Crew", "Trip", "Duty", "Leg", "LegSet", "Rotation"])
            self.setMenuOnly(True)

        def context_and_mode(self):
            return self.mapping[self.getValue()]


    class Mark(Cfh.String):
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 0, 'NONE')
            self.parent = weakref.ref(parent)
            self.setMenu(["Mark", "NONE", "LEG"])
            self.setMenuOnly(True)


    class Method(Cfh.String):
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 0, 'REPLACE')
            self.parent = weakref.ref(parent)
            self.setMenu(["Method", "REPLACE", "SUBSELECT", "ADD"])
            self.setMenuOnly(True)


# Evaluator =============================================================={{{1
class Evaluator(ABox):
    """Form for executing a CSL commands."""

    key_fields = ('opac', 'pot', 'tag', 'code')
    dv = ("OPAQUE", "DO", "Command", "")
    opac_d = {
            "OPAQUE": Gui.OPA_OPAQUE,
            "TRANS": Gui.OPA_TRANS
            }
    pot_d = {
            "DO" : Gui.POT_DO,
            "REDO": Gui.POT_REDO,
            "UNDO": Gui.POT_UNDO,
            "REPEAT": Gui.POT_REPEAT
            }


    class Clean(Cfh.Function):
        """Button to set default values in all fields."""
        def __init__(self, parent, *args):
            Cfh.Function.__init__(self, parent, *args)
            self.parent = weakref.ref(parent) 

        def action(self):
            p = self.parent()
            p.reset_form()


    class PrevNext(Cfh.Function):
        """Button to display next already executed command."""
        def __init__(self, direction, parent, *args):
            Cfh.Function.__init__(self, parent, *args)
            self.direction = direction
            self.parent = weakref.ref(parent) 
            self.setEnable(False)

        def action(self):
            p = self.parent()
            p.stack_pos += self.direction
            k = p.executed[p.stack_pos]
            p.set_values(k)
            p.np()


    class Evaluate(Cfh.Function):
        def __init__(self, parent, *args):
            Cfh.Function.__init__(self, parent, *args)
            self.parent = weakref.ref(parent)

        def action(self):
            p = self.parent()
            byp = {"WRAPPER" : Cui.CUI_WRAPPER_NO_EXCEPTION} 
            opac, pot, tag, code = k = p.get_values()
            opacity = p.opac_d.get(opac, Gui.OPA_OPAQUE)
            potency = p.pot_d.get(pot, Gui.POT_REDO)
            code = p.code.getValue()
            flags = (Cui.CUI_EXECUTE_FUNCTION_WAIT_CURSOR |
                    Cui.CUI_EXECUTE_FUNCTION_HONOUR_LOCK)

            r = self.execute_function(byp, code, tag, potency, opacity,
                    flags)
            if r: 
                p.message("Error - See log file", 1)
            else:
                p.message("Ok")
            if k in p.executed:
                p.executed.remove(k)
            p.executed.append(k)
            p.stack_pos = len(p.executed) - 1
            p.np()

        def execute_function(self, byp, code, tag, potency, opacity, flags):
            return Cui.CuiExecuteFunctionWithLock(byp, code.strip(), tag, potency,
                    opacity, flags)


    class String(Cfh.String):
        def __init__(self, parent, *args):
            Cfh.String.__init__(self, parent, *args)
            self.parent = weakref.ref(parent)

        def compute(self):
            Cfh.String.compute(self)
            p = self.parent()
            if p.get_values() not in p.executed:
                p.np()

        def verify(self, code):
            Cfh.String.verify(self, code)
            p = self.parent()
            cv = tuple([self == obj and code.value or obj.getValue() 
                for obj in [getattr(p, x) for x in p.key_fields]])
            if cv not in p.executed:
                p.np()


    def __init__(self, title, heading):
        ABox.__init__(self, title, heading)
        o, p, t, c = self.dv
        self.opac = self.String(self, self._cfh_id(), 
                Cfh.Area(Cfh.Loc(0, 1)), 0, o)
        self.opac.setMenu(["Opacity"] + self.opac_d.keys())
        self.pot = self.String(self, self._cfh_id(), 
                Cfh.Area(Cfh.Loc(0, 10)), 0, p)
        self.pot.setMenu(["Potency"] + self.pot_d.keys())
        self.tag_label = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 19)), "Label")
        self.tag = self.String(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 24)), 25, t)
        self.code = self.String(self, self._cfh_id(),
                Cfh.Area(Cfh.Dim(60, 8), Cfh.Loc(1, 1)), 0, c)
        self.code.setStyle(Cfh.CfhSChoiceText)
        self.close = Cfh.Cancel(self, self._cfh_id(),
                Cfh.Area(), "Close", "_C")
        self.eval = self.Evaluate(self, self._cfh_id(), 
                Cfh.Area(), "Run", "_R")
        self.prev = self.PrevNext(-1, self, self._cfh_id(),
                Cfh.Area(), "Previous", "_P")
        self.next = self.PrevNext(1, self, self._cfh_id(),
                Cfh.Area(), "Next", "_N")
        self.clean = self.Clean(self, self._cfh_id(),
                Cfh.Area(), "Default", "_l")
        self.executed = [self.dv]
        self.stack_pos = 0
        self.build()

    def get_values(self):
        return (self.opac.getValue(), self.pot.getValue(),
                self.tag.getValue(), self.code.getValue())

    def set_values(self, k):
        o, p, t, c = k
        self.opac.setValue(o)
        self.pot.setValue(p)    
        self.tag.setValue(t)
        self.code.setValue(c)

    def reset_form(self):
        self.set_values(self.dv)
        self.executed.remove(self.dv)
        self.executed.append(self.dv)
        self.stack_pos = len(self.executed) - 1
        self.np()

    def np(self):
        """Enable/Disable buttons"""
        self.clean.setEnable(bool(self.get_values() != self.dv))
        self.eval.setEnable(bool(self.code.getValue()))
        try:
            self.executed[self.stack_pos + 1]
            self.next.setEnable(True)
        except:
            self.next.setEnable(False)
        if self.stack_pos < 1:
            self.prev.setEnable(False)
        else:
            try:
                self.executed[self.stack_pos - 1]
                self.prev.setEnable(True)
            except:
                self.prev.setEnable(False)


# CSLEvaluator ==========================================================={{{1
class CSLEvaluator(Evaluator):
    """Form for executing a CSL commands."""
    def __init__(self):
        Evaluator.__init__(self, "DEV_CSL_EVALUATOR", "Run CSL commands")


# PythonEvaluator ========================================================{{{1
class PythonEvaluator(Evaluator):
    """Form for executing a Python commands."""

    dv = ("OPAQUE", "DO", "Python code", "")

    class Evaluate(Evaluator.Evaluate):
        def execute_function(self, byp, code, tag, potency, opacity, flags):
            fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.py')
            f = os.fdopen(fd, 'w')
            f.write(code)
            f.close()
            csl_code = 'PythonRunFile("%s")' % (fn,)
            rc = Cui.CuiExecuteFunctionWithLock(byp, csl_code, tag, potency,
                    opacity, flags)
            os.unlink(fn)
            return rc


    def __init__(self):
        Evaluator.__init__(self, "DEV_PY_EVALUATOR", "Run Python commands")


# PythonCodeManager ======================================================{{{1
class PythonCodeManager:
    dont_show = ('CVS', 'i386_linux', 'parisc_2_0', 'x86_64_solaris',
            'manpower', 'x86_64_linux', 'powerpc', 'ia64_hpux', 'sparc',
            'sparc_64')
    groups = (
        ("$CARMUSR/lib/python", "<USR>"),
        ("$CARMUSR/menu_scripts/python", "$CARMUSR/menu_scripts/python"),
        ("$CARMUSR/matador_scripts", "$CARMUSR/matador_scripts"),
        ("$CARMSYS/lib/python", "<SYS>"),
    )
    def __init__(self, groups=None):
        if groups is not None:
            self.groups = groups

    def run(self):
        fd, fn = mkstemp()
        f = os.fdopen(fd, "w")
        layout = (
            'Python Manager;LENCDIPRR;',
            'EXEC_BUTTON;Run;Reload',
            """DEFAULT_EXEC_FUNC;PythonRunFile("%%F");DEFAULT_EXEC_FUNC;PythonEvalExpr("%s.reload_python_file('%%F')")""" % (
                this_module),
            )
        print >>f, '\n'.join(layout)
        for dir, caption in self.dir_list():
            print >>f, "%s;%s;DIR_GROUP;1" % (caption, dir)
        f.close()
        try:
            Cui.CFM(fn)
            os.unlink(fn)
        except:
            pass

    def dir_list(self):
        X = []
        for dir, caption in self.groups:
            L = []
            dir_exp = os.path.expandvars(dir)
            for root, dirnames, filenames in os.walk(dir_exp):
                for d in dirnames:
                    if d in self.dont_show:
                        dirnames.remove(d)
                dir_name = root.replace(dir_exp, caption, 1)
                L.append((root, dir_name))
            X.extend([x for x in sorted(L)])
        return X


# RaveEvaluator =========================================================={{{1
class RaveEvaluator(ABox):
    """Form for evaluating Rave expressions."""
    # Keep this between runs
    class Expression(Buttons.Expression):
        def verify(self, str):
            # any action in this field disables the message box
            self.parent().mesg.setEnable(False)
            return None

        def compute(self):
            # any action in this field disables the message box
            self.parent().mesg.setEnable(False)
            return None


    class Scope(Cfh.String):
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 0, 'Object')
            self.parent = weakref.ref(parent)
            self.setMenuString("Scope;None;Object;Chain;Window;Plan")
            self.setMandatory(True)
            self.setMenuOnly(True)

        def verify(self, str):
            # any action in this field disables the message box
            self.parent().mesg.setEnable(False)
            return None

        def compute(self):
            # any action in this field disables the message box
            self.parent().mesg.setEnable(False)
            return None


    class Message(Cfh.String):
        """Box with output, or, Error message."""
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 1000, '')
            self.parent = weakref.ref(parent)
            self.setStyle(Cfh.CfhSChoiceText)
            self.setEditable(False)
            self.setEnable(False)


    class Evaluate(Cfh.Function):
        """Call Rave."""
        def __init__(self, parent, name):
            Cfh.Function.__init__(self, parent, name,
                    Cfh.CfhArea(), "Eval", "E", True, True, -1)
            #                                   Check Dflt  Return
            self.parent = weakref.ref(parent)

        def eval_expr(self, x):
            scope = self.parent().scope.getValue()
            if scope == 'Chain':
                try:
                    val, = rave.eval(rave.selected(rave.Level.chain()), x)
                    if val is None:
                        typ = 'VOID'
                    else:
                        regexp = re.compile(r"""<(type|class) '(BSIRAP\.)?([^']+)'>""")
                        t = str(type(val))
                        m = regexp.match(t)
                        if m:
                            typ = m.groups()[2]
                        else:
                            typ = t
                except:
                    typ = '?'
                    val = 'FAILED'
            else:
                val = Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiWhichArea, self.parent().scope.getValue(), x)
                typ = getNameOfTag(val.getTag())
            return (typ, val)

        def action(self):
            # Fetch value from expression field and push it to menu
            xprs = self.parent().expr.getValue()
            self.parent().expr.pushStringOnMenu(xprs)
            # fetch value from type field call Rave, package output in an
            # object that knows about string representations
            L = []
            message = 'Ok'
            fault = False
            for x in xprs.split(';'):
                try:
                    t, b = self.eval_expr(x)
                    if t == 'String':
                        L.append('%s -> %s: "%s"\n\n' % (x, t, str(b)))
                    else:
                        L.append("%s -> %s: %s\n\n" % (x, t, str(b)))
                except Exception, e:
                    message = 'Evaluation Failed'
                    fault = True
                    errmsgs = str(e).split('\n')
                    L.extend(['\n', '\n'.join(errmsgs[3:])])
            s = ''.join(L)
            Errlog.log("Rave Evaluator: "+ s)  # To make it possible to copy the result with the mouse.
            self.parent().mesg.setValue(s)
            self.parent().message(message, fault)
            self.parent().mesg.setEnable(True)


    class Cancel(Cfh.Cancel):
        """Cancel and set invisible."""
        def __init__(self, parent, name):
            Cfh.Cancel.__init__(self, parent, name, Cfh.CfhArea(), 'Close',
                    'C')
            self.parent = weakref.ref(parent)

        def compute(self, *args):
            self.parent().is_visible = False
            Cfh.Cancel.compute(self,*args)


    def __init__(self, cfh_id="DEV_RAVE_EVALUATOR"):
        ABox.__init__(self, cfh_id, 'Evaluate Rave Expression')
        self.setDim(Cfh.CfhDim(60, 10))
        self.scope = self.Scope(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhDim(10, 1), Cfh.CfhLoc(0, 0)))
        self.expr = Buttons.Expression(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhDim(58, 1), Cfh.CfhLoc(1, 0)))
        self.mesg = self.Message(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhDim(60, 8), Cfh.CfhLoc(2, 0)))
        self.eval = self.Evaluate(self, self._cfh_id())
        self.close = self.Cancel(self, self._cfh_id())
        self.is_visible = False
        self.build()

    def visualize(self):
        self.show(True)
        self.is_visible = True

    def listener(self):
        if self.is_visible and len(self.expr.getValue()):
            return self.eval.compute()

    @staticmethod
    def init_rave_evaluator():
        global rave_evaluator
        #if rave_evaluator is None:
        if True:
            exec('import %s' % this_module)
            rave_evaluator = RaveEvaluator()
            setattr(sys.modules[this_module], 'rave_evaluator', rave_evaluator)
            Gui.GuiCreateListener('PythonEvalExpr("%s.rave_evaluator.listener()")' % this_module,
                    Gui.MotionListener, "")
        rave_evaluator.visualize()


# RaveSearchBox =========================================================={{{1
class RaveSearchBox(ABox):
    """Search for objects matching Rave Expression in plan."""
    Expression = Buttons.Expression
    Area = Buttons.Area
    Mark = Buttons.Mark
    Method = Buttons.Method
    Mode = Buttons.Mode

    class SearchButton(Cfh.Function):
        err_fmt = 'Rave Search: %s'
        def __init__(self, parent, name):
            Cfh.Function.__init__(self, parent, name,
                    Cfh.CfhArea(), "Search", "S", 0, 0, -1)
            self.parent = weakref.ref(parent)

        def action(self):
            from Variable import Variable
            p = self.parent()
            xprs = p.expr.getValue()
            self.parent().expr.pushStringOnMenu(xprs)
            message = 'Ok'
            try:
                e = rave.expr(xprs)
            except rave.ParseError, re:
                p.message('Invalid expression', True)
                Errlog.log(self.err_fmt % re)
                return
            except rave.UsageError, ue:
                p.message('Impossible. Probably no loaded Rule set', True)
                Errlog.log(self.err_fmt % ue)
                return
            # Check that a subplan is loaded. 
            try: 
                Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, Variable())
            except StudioError, se:
                p.message("Impossible. You must load a sub plan first", True)
                Errlog.log(self.err_fmt % se)
                return
            # Find an iterator to use.
            iter = None
            for it in ("leg_set", "iterators.leg_set", "gpc_iterators.leg_set"):
                try:
                    rave.iterator(it)
                    iter = it
                except rave.UsageError:
                    pass
            if iter is None:
                p.message('Leg set iterator missing.', True)
                Errlog.log(self.err_fmt % 'no valid leg_set iterator found in rule set.')
                return
            # Check that the expression is a boolean.
            try:
                rave.iter(iter, where=xprs)
            except rave.UsageError, ue:
                p.message("The expression must be boolean", True)
                Errlog.log(self.err_fmt % ue)
                return

            # Get other entered values   
            areaid = int(p.area.getValue()) - 1
            context, mode = p.mode.context_and_mode()
            mark = p.mark.getValue()
            meth = p.method.getValue()

            # Use "CuiExecuteFunction" to get macro recording and undo handling
            command = """PythonEvalExpr("%s.select_by_rave_expression%s")""" % (
                    this_module,
                    (context, areaid, mode, mangle(xprs), iter, meth, int(mark == "LEG")),)
            Cui.CuiExecuteFunction(command, "DevMenu Select: " + xprs,
                    Gui.POT_REDO, Gui.OPA_OPAQUE)
            p.message(message)


    def __init__(self, cfh_id="DEV_RAVE_SEARCH"):
        ABox.__init__(self, cfh_id, 'Search for Objects by Rave Expression')
        self.l_area = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 0)), "Area")
        self.area = self.Area(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(0, 5)))
        self.l_method = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 30)), "Method")
        self.method = self.Method(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(0, 35)))
        self.l_mode = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(1, 0)), "Mode")
        self.mode = self.Mode(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(1, 5)))
        self.l_mark = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(1, 30)), "Mark")
        self.mark = self.Mark(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(1, 35)))
        self.sep = Cfh.Separator(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 0)),
                100, 0)
        self.expr = self.Expression(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhDim(58, 1), Cfh.CfhLoc(3, 0)))

        self.search = self.SearchButton(self, self._cfh_id())
        self.close = Cfh.Cancel(self, self._cfh_id(), Cfh.CfhArea(), 'Cancel', '_C')
        self.build()
        self.show(True)
        self.loop()


# RuleFailureBox ========================================================={{{1
class RuleFailureBox(ABox):
    """Search for rule failures. Experimental."""

    Area = Buttons.Area
    Mark = Buttons.Mark
    Method = Buttons.Method
    Mode = Buttons.Mode

    class SearchButton(Cfh.Function):
        """User defined button. Start search."""
        err_fmt = 'Rule Search: %s'
        def __init__(self, parent, name):
            Cfh.Function.__init__(self, parent, name,
                    Cfh.CfhArea(), 'Search', 'S', 0, 0, -1)
            self.parent = weakref.ref(parent)

        def action(self):
            from Variable import Variable
            p = self.parent()
            #p.update()
            # Do some basic tests
            rule = p.rule.getValue()
            try: 
                rr = rave.rule(rule)
            except rave.UsageError, ue: 
                p.message('Impossible: %s' % ue)
                Errlog.log(self.err_fmt % ue)
                return
            if not rr.on():
                mess = "Impossible: The rule has been switched off"
                p.message(mess)
                Errlog.log(self.err_fmt % mess)
                return
            try:
                Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, Variable())
            except StudioError, se:
                mess = "Impossible. You must load a sub plan first"
                p.message(mess)
                Errlog.log(self.err_fmt % mess + ' - ' + str(se))
                return

            # Get other entered values   
            areaid = int(p.area.getValue()) - 1
            context, mode = p.mode.context_and_mode()
            mark = p.mark.getValue()
            meth = p.method.getValue()
            command = """PythonEvalExpr("%s.select_by_rule_failure%s")""" % (
                    this_module,
                    (context, areaid, mode, rule, meth, int(mark == "LEG")),)
            Cui.CuiExecuteFunction(command, "DevMenu RuleFailure:" + rule,
                    Gui.POT_REDO, Gui.OPA_OPAQUE)


    class Rule(Cfh.String):
        """Has menu with all available rules."""
        def __init__(self, parent, name, area):
            Cfh.String.__init__(self, parent, name, area, 100, '')
            self.parent = weakref.ref(parent)
            l = ["Rules"]
            for m in Cui.CuiCrcModuleList():
                for rn in Cui.CuiCrcRuleList(m):
                    if m == "_topmodule":
                        rule_name = m
                    else:
                        rule_name = m + "." + rn
                    ro = rave.rule(rule_name)
                    if ro.on():
                        l.append("%s:[%s] %s" % (rule_name, rn, ro.remark()))
            l.sort()
            self.setMenu(l)


    def __init__(self, cfh_id='DEV_RULE_FAIL'):
        ABox.__init__(self, cfh_id, 'Search for Rule Failures')
        self.l_area = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 0)), "Area")
        self.area = self.Area(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(0, 5)))
        self.l_method = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(0, 30)), "Method")
        self.method = self.Method(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(0, 35)))
        self.l_mode = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(1, 0)), "Mode")
        self.mode = self.Mode(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(1, 5)))
        self.l_mark = Cfh.Label(self, self._cfh_id(),
                Cfh.Area(Cfh.Loc(1, 30)), "Mark")
        self.mark = self.Mark(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhLoc(1, 35)))
        self.sep = Cfh.Separator(self, self._cfh_id(), 
                Cfh.Area(Cfh.Loc(2, 0)), 100, 0)
        self.rule = self.Rule(self, self._cfh_id(),
                Cfh.CfhArea(Cfh.CfhDim(58, 1), Cfh.CfhLoc(3, 0)))
        self.search = self.SearchButton(self, self._cfh_id())
        self.close = Cfh.Cancel(self, self._cfh_id(), Cfh.CfhArea(), 'Cancel', '_C')
        self.build()
        self.show(True)
        self.loop()


# CodeSearch ============================================================={{{1
class CodeSearch(ABox):
    """Search for source code lines using grep. Present lines using Vim's
    Quickfix window."""

    class SearchButton(Cfh.Function):
        """Button to set search for string."""
        def __init__(self, parent, *args):
            Cfh.Function.__init__(self, parent, *args)
            self.parent = weakref.ref(parent) 
            self.fn = None

        def action(self):
            p = self.parent()
            fd, self.fn = mkstemp(dir=os.environ['CARMTMP'],
                    suffix='.tmp', prefix='DEV_MENU_SEARCH_')
            f = os.fdopen(fd, 'w')
            s = p.expr.getValue()
            (crc, crg, cdt, cpy) = (p.crc.getValue(), p.crg.getValue(), p.cdt.getValue(),
                    p.cpy.getValue())
            if crc:
                self.do_search(s, f, "$CARMUSR/crc")
            if crg:
                self.do_search(s, f, "$CARMUSR/crg")
            if cdt:
                self.do_search(s, f, "$CARMUSR/data")
            if cpy:
                self.do_search(s, f, "$CARMUSR/lib/python", include="*.py")
            f.close()
            if crc or crg or cdt or cpy:
                xterm('-e', editor, '-c', ':cfile %s' % self.fn)

        def __del__(self):
            if self.fn:
                try:
                    os.unlink(self.fn)
                except:
                    print "Could not delete file %s" % self.fn

        def do_search(self, sstr, file, path, include=None):
            cmd = ['grep']
            if self.parent().icase.getValue():
                cmd.append('-i')
            cmd.extend(['-n', '-d', 'recurse'])
            if not include is None:
                cmd.extend(['--include', include])
            cmd.extend([sstr, os.path.expandvars(path)])
            Popen(cmd, stdout=file).wait()


    def __init__(self, cfh_id="DEV_CODE_SEARCH"):
        ABox.__init__(self, cfh_id, 'Search Source Code')
        self.l_expr = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(0, 0)),
                "Enter search string or regular expression")
        self.l_icase = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(0, 48)),
                "Ignore Case")
        self.icase = Cfh.Toggle(self, self._cfh_id(), Cfh.Area(Cfh.Loc(0, 56)), True)
        self.expr = Cfh.String(self, self._cfh_id(), Cfh.Area(Cfh.Loc(1, 0)),
                62, "")
        self.l_crc = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 0)),
                "Rave Modules")
        self.crc = Cfh.Toggle(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 8)), True)
        self.l_crg = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 16)),
                "CRG Code")
        self.crg = Cfh.Toggle(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 24)), True)
        self.l_cdt = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 32)),
                "Forms & Conf.")
        self.cdt = Cfh.Toggle(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 40)), True)
        self.l_cpy = Cfh.Label(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 48)),
                "Python Code")
        self.cpy = Cfh.Toggle(self, self._cfh_id(), Cfh.Area(Cfh.Loc(2, 56)), True)
        self.s = self.SearchButton(self, self._cfh_id(), Cfh.Area(), 'Search', '_S')
        self.c = Cfh.Cancel(self, self._cfh_id(), Cfh.CfhArea(), 'Cancel', '_C')
        self.build()
        self.show(True)
        self.loop()


# XML Parsing for Entities================================================{{{1

# Entities ---------------------------------------------------------------{{{2
class Entities(dict):
    def __init__(self, dom):
        dict.__init__(self)
        for e in dom.getElementsByTagName("entity"):
            E = Entity_(e)
            self[E.name] = E
            for f in e.getElementsByTagName('field'):
                E.append(Field_(f))

    def set_ref_ind(self, references, indices):
        for entity_name, entity_obj in self.iteritems():
            for field in entity_obj:
                if (entity_name, field.name) in references:
                    field.set_reference(references[(entity_name, field.name)])
                if (entity_name, field.name) in indices:
                    field.is_index = True


# References -------------------------------------------------------------{{{2
class References(dict):
    def __init__(self, dom):
        dict.__init__(self)
        for r in dom.getElementsByTagName('reference'):
            entityname = str(r.getAttribute('entityname'))
            name = str(r.getAttribute('name'))
            tgtname = str(r.getAttribute('tgtname'))
            keys = str(r.getAttribute('key')).split(',')
            tgtkeys = str(r.getAttribute('tgtkey')).split(',')
            for i in xrange(len(keys)):
                self[(entityname, keys[i])] = (name, tgtname, tgtkeys[i])


# Indices ----------------------------------------------------------------{{{2
class Indices(set):
    def __init__(self, dom):
        set.__init__(self)
        for e in dom.getElementsByTagName('index'):
            entityname = str(e.getAttribute('entityname'))
            for i in e.getElementsByTagName('indexfield'):
                indexfield = str(i.getAttribute('name'))
                self.add((entityname, indexfield))


# Sequences --------------------------------------------------------------{{{2
class Sequences(list):
    def __init__(self, dom):
        list.__init__(self, [str(s.getAttribute('name')) for s in
            dom.getElementsByTagName('sequence')])


# Entity_ ----------------------------------------------------------------{{{2
class Entity_(list):
    def __init__(self, dom):
        list.__init__(self)
        self.name = str(dom.getAttribute('name'))
        self.desc = str(dom.getAttribute('desc'))

    def __str__(self):
        return " - %-40.40s %s" % (self.name, self.desc)


# Field_ -----------------------------------------------------------------{{{2
class Field_:
    def __init__(self, dom):
        self.name = str(dom.getAttribute('name'))
        self.type = str(dom.getAttribute('type'))
        self.desc = str(dom.getAttribute('desc'))
        self.size = str(dom.getAttribute('size'))
        self.pk = str(dom.getAttribute('pk')) == "true"
        self.is_index = False
        self.set_reference((None, None, None))

    def __str__(self):
        type_str = self.type
        if self.size:
            type_str += "(%s)" % self.size
        if self.ref_name is None:
            name_str = self.name
        else:
            name_str = "  .%s [%s]" % (self.ref_key, self.name)
        return "  %s%s%-30.30s %-15.15s %s" % ((' ', '*')[self.is_index],
                (' ', '*')[self.pk], name_str, type_str, self.desc)

    def set_reference(self, ref):
        name, tgtname, tgtkey = ref
        self.ref_name = name
        self.ref_key = tgtkey
        self.ref_entity = tgtname


# Dynamic reports ========================================================{{{1

# DynamicReport ----------------------------------------------------------{{{2
class DynamicReport:
    def __init__(self, report):
        self.report = report
        self.listener = Gui.MotionListener

    def run(self, scope='OBJECT', tag='', title=None, rpt_args=''):
        if title is None:
            title = self.report
        sf = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef,
                "PRTReportFormat")
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", "HTML", "")
        Cui.CuiCrgDisplayDynamicReport(Cui.gpc_info, Cui.CuiAllAreas, scope,
                self.report, self.listener, tag, title, rpt_args)
        Crs.CrsSetModuleResource("preferences", "PRTReportFormat", sf, "")

    def edit(self):
        if self.report.endswith('.py'):
            rpath = os.path.join(os.environ['CARMUSR'], 'lib', 'python',
                    'report_sources', 'hidden', self.report)
        else:
            rpath = os.path.join(os.environ['CARMUSR'], 'crg', 'hidden',
                    self.report)
        xterm('-e', editor, rpath)


# DynamicReports ---------------------------------------------------------{{{2
class DynamicReports(mnu.Menu):
    def __init__(self):
        menus = []
        for rpt in os.listdir(os.path.join(os.environ['CARMUSR'], 'lib',
                'python', 'report_sources', 'hidden')):
            if rpt.startswith('ZZ_dyn_') and rpt.endswith('.py'):
                menus.append(DynReportMenu(rpt.split('.')[0].upper(), rpt))
        mnu.Menu.__init__(self, 'DEV_MENU_DYN_REPORTS', menus, 
                title="Dynamic Reports", mnemonic="_D", tooltip="Dynamic reports")


# DynReportMenu ----------------------------------------------------------{{{2
class DynReportMenu(mnu.Menu):
    def __init__(self, name, reportfile):
        dynrep = DynamicReport(reportfile)
        mnu.Menu.__init__(self, name, (
            mnu.Button('Run', action=dynrep.run),
            mnu.Separator(),
            mnu.Button('Edit', action=dynrep.edit),
            ), title=reportfile)


# functions =============================================================={{{1

# csl_exec ---------------------------------------------------------------{{{2
def csl_exec(commands):
    try:
        fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.csl')
        f = os.fdopen(fd, "w")
        f.write('EVAL {\n%s\n}\n' % '\n'.join(commands))
        f.close()
        os.chmod(fn, stat.S_IRWXU)
        csl.evalExpr('csl_run_file("%s")' % fn)
        os.unlink(fn)
    except:
        print "csl_exec failed."


# do_reload --------------------------------------------------------------{{{2
def do_reload(module):
    exec("import %s" % module)
    exec("reload(%s)" % module)
    reload(__import__(module))


# make_executable --------------------------------------------------------{{{2
def make_executable(fn):
    os.chmod(fn, os.stat(fn)[stat.ST_MODE] | stat.S_IXUSR | stat.S_IXGRP |
            stat.S_IXOTH)


# reload_python_file -----------------------------------------------------{{{2
def reload_python_file(python_file):
    clp = os.path.expandvars("$CARMUSR/lib/python/")
    try:
        do_reload(python_file[:-3].replace(clp, '', 1).replace('/', '.'))
    except Exception, e:
        fd, fn = mkstemp(dir=os.environ['CARMTMP'])
        f = os.fdopen(fd, 'w')
        print >>f, traceback.format_exc()
        f.close()
        cfhExtensions.showFile(fn, "Reload of '%s'" % python_file)
        os.unlink(fn)


# create_menu ------------------------------------------------------------{{{2
def create_menus():
    """Developer"""
    dev = DeveloperMenu('Developer')
    dev.attach('TOP_MENU_BAR')

    dev_obj = DevMenuObject('Developer')
    for menu in object_menus:
        dev_obj.attach(menu)

    dev_gen = DevMenuGeneral('Developer')
    for menu in general_menus:
        dev_gen.attach(menu)


# mangle -----------------------------------------------------------------{{{2
def mangle(str, mangle=True):
    if mangle:
        return str.replace('"', '_@_')
    else:
        return str.replace('_@_', '"')


# select_by_leg_ids ------------------------------------------------------{{{2
def select_by_leg_ids(leg_ids, to_area, mode, iter='iterators.leg_set',
        method='REPLACE', mark=False):
    def legs_in_window():
        Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, 'WINDOW')
        result, = rave.eval('default_context', rave.foreach(rave.iter(iter),
            'leg_identifier'))
        return set([str(x[1]) for x in result])
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, to_area)
    if mode != Cui.CuiGetAreaMode(Cui.gpc_info, area):
        Cui.CuiDisplayObjects(Cui.gpc_info, area, mode, Cui.CuiShowNone)
    if method == "SUBSELECT":
        window_legs = legs_in_window()
        leg_ids = [x for x in leg_ids if x in window_legs]
        method = "REPLACE"
    elif method == "ADD":
        window_legs = legs_in_window()
        leg_ids = [x for x in leg_ids if not x in window_legs]
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, area, mode, Cui.LegMode, leg_ids)
    if method == "REPLACE":
        Cui.CuiSortArea(Cui.gpc_info, area, Cui.CuiSortFirstStart, 0)
    if mark:
        for leg in leg_ids:
            try:
                Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, leg)
                Cui.CuiMarkLegs(Cui.gpc_info, area, 'object', Cui.CUI_MARK_SET)
            except:
                print "Could not mark leg with leg id = %s" % leg


# select_by_rave_expression ----------------------------------------------{{{2
def select_by_rave_expression(context, to_area, mode, expr,
        iter='iterators.leg_set', method='REPLACE', mark=False):
    result, = rave.eval(context, rave.foreach(rave.iter(iter,
        where=mangle(expr, False)), 'leg_identifier'))
    leg_ids = [str(x[1]) for x in result]
    select_by_leg_ids(leg_ids, to_area, mode=mode, iter=iter, method=method,
            mark=mark)


# select_by_rule_failure -------------------------------------------------{{{2
def select_by_rule_failure(context, to_area, mode, rulename, method="REPLACE",
        mark=False):
    """Search for all objects violating a specific rule. Called by csl command
    in callback function from search_by_rule.py."""
    result, = rave.eval(context, rave.foreach(rave.iter('iterators.chain_set'),
        rave.foreach(rave.rulefailure(),
            rave.foreach(rave.iter('iterators.leg_set'), 'leg_identifier'))))
    leg_ids = []
    rulename = rulename.lower()
    for ix, crew in result:
        for rf, rule in crew:
            if rf.rule.name().lower() == rulename:
                for ix, leg_id in rule:
                    leg_ids.append(str(leg_id))
    select_by_leg_ids(leg_ids, to_area, mode=mode, iter='iterators.leg_set',
            method=method, mark=mark)


# PythonEvalExpr ---------------------------------------------------------{{{2
def PythonEvalExpr(name="PythonEvalExpr", *args):
    eval_expr = """PythonEvalExpr("%s")""" % ', '.join(["%s" % a for a in args])
    Cui.CuiExecuteFunction(eval_expr, name, Gui.POT_REDO, Gui.OPA_OPAQUE)


# PythonRunFile ----------------------------------------------------------{{{2
def PythonRunFile(*args):
    csl.evalExpr('PythonRunFile(%s)' % ', '.join(['"%s"' % x for x in args]))


# sort_ ------------------------------------------------------------------{{{2
def sort_(s):
    """Sort by rule value"""
    Cui.CuiSortArea(Cui.gpc_info, Cui.CuiWhichArea, Cui.CuiSortRuleValue, '%s' % s)


# xterm ------------------------------------------------------------------{{{2
def xterm(*args):
    Popen(['xterm', '-tm', "erase ^?"] + list(args))


def python_reload(module_list_module_str=the_reload_module_name):
    """
    The named list-module should contain one variable:
     modlist = [
       "mod.mod.mod",
       "mod.mod.mod2",
       "mod3.mod4",
       # etc
     ]
     First the module with the list is reloaded.
     Then each module in modlist is reloaded in order.

    :param module_list_module_str: String. The name of the module containing the list of modules.
    :return: None
    """
    do_reload(module_list_module_str)
    fd, fn = mkstemp(dir=os.environ['CARMTMP'])
    f = os.fdopen(fd, 'w')
    reloaded_ok = []
    exceptions = {}
    for module in sys.modules[module_list_module_str].modlist:
        try:
            do_reload(module)
            reloaded_ok.append(module)
        except Exception, e:
            exceptions[module] = traceback.format_exc()

    if reloaded_ok:
        print >> f, "=" * 80
        print >> f, "These modules were reloaded:"
        print >> f, "=" * 80
        for module in reloaded_ok:
            print >> f, "\t%s" % module

    if exceptions:
        if reloaded_ok:
            print >> f, "\n"
        print >> f, "=" * 80
        print >> f, "These modules failed:"
        print >> f, "=" * 80
        for module in exceptions:
            print >> f, module
            print >> f, "-" * 80
            print >> f, exceptions[module]
            print >> f, "=" * 80

    f.close()
    if reloaded_ok or exceptions:
        cfhExtensions.showFile(fn, "Python Module Reload  - from '%s'" % module_list_module_str)
    os.unlink(fn)


def set_time():
    from Variable import Variable
    time_var = Variable(0)
    key_var = Variable("", 30)
    try:
        Cui.CuiSelectTimeAndResource(Cui.gpc_info, time_var, key_var, 30)
    except:
        return 1
    atime = AbsTime(time_var.value)
    rave.param('fundamental.%now_debug%').setvalue(atime)
    rave.param('fundamental.%use_now_debug%').setvalue(True)
    Cui.CuiReloadTables()
    Gui.GuiCallListener(Gui.RefreshListener, 'parametersChanged')


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    #sys.path = [os.path.join(os.environ['HOME'], 'lib', 'python', 'acotest')] + sys.path
    import adhoc.developer_menu
    create_menus()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
