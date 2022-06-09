
# [acosta:08/126@12:49] Created for debugging purposes.

"""
Some useful debugging extensions to the menu system.

To use the debug menus, enable "Special Menu" and create a script:
    ~/my_python.py
with the following contents:
    import utils.mnu
    import adhoc.debug_menu
"""

import __main__
import utils.mnu
from utils.mnu import Menu, Button, Separator, CSLEval
import Cui
import Csl
import os
from tempfile import mkstemp
from carmstd import cfhExtensions


csl = Csl.Csl()
gpd_types = (BLOB, BLOBLINE, SUBWINDOW, AREA) = tuple(range(4))


class quantify:
    @staticmethod
    def start():
        return Cui.CuiQuantifyCtrl(1)

    @staticmethod
    def stop():
        return Cui.CuiQuantifyCtrl(2)

    @staticmethod
    def reset():
        return Cui.CuiQuantifyCtrl(3)


quantify_menu = Menu('QuantifyMenu',
    (
        Button(title="Start", action=quantify.start),
        Button(title="Stop", action=quantify.stop),
        Button(title="Reset", action=quantify.reset),
    ), title="Quantify")

quantify_menu.attach('TOP_MENU_BAR')



class B_LP(Button):
    def __init__(self, title='Print LP', details='false', subobjects='false',
            plan='main', show_file=True, func='CuiPrintLocalplan'):
        self.title = title
        self.details = details
        self.subobjects = subobjects
        self.plan = plan
        self.func = func
        self.show_file = show_file
        Button.__init__(self, title=title)

    def run(self):
        if self.show_file:
            fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
            csl.evalExpr('%s(gpc_info, "%s", "%s", "%s", "%s")' % (self.func,
                self.details, self.subobjects, self.plan, fn))
            cfhExtensions.showFile(fn, self.title)
            os.unlink(fn)
        else:
            csl.evalExpr('%s(gpc_info, "%s", "%s", "%s")' % (self.func,
                self.details, self.subobjects, self.plan))


class B_SP(B_LP):
    def __init__(self, title='Print SP', details='false', subobjects='false',
            plan='main', show_file=True, func='CuiPrintSubplan'):
        B_LP.__init__(self, title=title, details=details, subobjects=subobjects,
                plan=plan, show_file=show_file, func=func)


class B_LP_Sanity(Button):
    def __init__(self, title='LP Sanity Check', show_file=True, func='CuiLocalPlanSanityCheck'):
        self.title = title
        self.func = func
        self.show_file = show_file
        Button.__init__(self, title=title)

    def run(self):
        if self.show_file:
            fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
            csl.evalExpr('%s(gpc_info, "%s")' % (self.func, fn))
            cfhExtensions.showFile(fn, self.title)
            os.unlink(fn)
        else:
            csl.evalExpr('%s(gpc_info)' % self.func)


class B_GPD(Button):
    def __init__(self, title='Print Object', level=BLOB, all=True,
            show_file=True, func='PrintDebug'):
        self.title = title
        self.func = func
        self.level = level
        self.all = all
        self.show_file = show_file
        Button.__init__(self, title=title)

    def run(self):
        if self.show_file:
            fd, fn = mkstemp(dir=os.environ['CARMTMP'], suffix='.tmp')
            csl.evalExpr('%s(gpc_info, %d, %d, "%s")' % (self.func, self.level, self.all, fn))
            cfhExtensions.showFile(fn, self.title)
            os.unlink(fn)
        else:
            csl.evalExpr('%s(gpc_info, %d, %d)' % (self.func, self.level, self.all))


class B_print(Button):
    def __init__(self, func, title, details='false', subobjects='false', memaddr='false', prevrev=None):
        self.func = func
        self.title = title
        self.details = details
        self.subobjects = subobjects
        self.memaddr = memaddr
        self.prevrev = prevrev
        Button.__init__(self, title)

    def run(self):
        if self.prevrev is None:
            csl.evalExpr('%s(gpc_info, CuiWhichArea, "%s", "%s", "%s")' % (
                self.func, self.details, self.subobjects, self.memaddr))
        else:
            csl.evalExpr('%s(gpc_info, CuiWhichArea, "%s", "%s", "%s", "true")' % (
                self.func, self.details, self.subobjects, self.memaddr))


dbg_print_crew = Menu('CrewDebugPrint', (
    B_print('CuiPrintCrew', 'Print Crew'),
    B_print('CuiPrintCrew', 'Print Crew (detailed)', details='true', memaddr='true'),
    B_print('CuiPrintCrew', 'Print Crew (detailed, incl all sub objects)', details='true', subobjects='true'),
    B_print('CuiPrintCrew', 'Print Crew (detailed + previous revision)', details='true', memaddr='true', prevrev='true'),
    ), title="Debug Menu")

dbg_print_crew.attach('LeftDat24CrewCompMode1')

dbg_print_crr = Menu('CrrDebugPrint', (
    B_print('CuiPrintCrr', 'Print'),
    B_print('CuiPrintCrr', 'Print (detailed)', details='true', memaddr='true'),
    B_print('CuiPrintCrr', 'Print (detailed, incl all sub objects)', details='true', subobjects='true'),
    B_print('CuiPrintCrr', 'Print (detailed + previous revision)', details='true', memaddr='true', prevrev='true'),
    ), title="Crr")

dbg_print_chain = Menu('ChainDebugPrint', (
    B_print('CuiPrintChain', 'Print', memaddr='true'),
    B_print('CuiPrintChain', 'Print (detailed, incl all sub objects)', details='true', subobjects='true', memaddr='true'),
    ), title="Chain")

dbg_print_segment = Menu('SegmentDebugPrint', (
    B_print('CuiPrintSegment', 'Print'),
    B_print('CuiPrintSegment', 'Print (detailed)', details='true', memaddr='true'),
    B_print('CuiPrintSegment', 'Print (detailed, incl all sub objects)', details='true', subobjects='true'),
    B_print('CuiPrintSegment', 'Print (detailed + previous revision)', details='true', memaddr='true', prevrev='true'),
    ), title="Segment")

dbg_print_leg = Menu('SegmentDebugPrint', (
    B_print('CuiPrintLeg', 'Print'),
    B_print('CuiPrintLeg', 'Print (detailed)', details='true', memaddr='true'),
    B_print('CuiPrintLeg', 'Print (detailed, incl all sub objects)', details='true', subobjects='true'),
    B_print('CuiPrintLeg', 'Print (detailed + previous revision)', details='true', memaddr='true', prevrev='true'),
    ), title="Leg")

dbg_print_acrot = Menu('ACRotDebugPrint', (
    B_print('CuiPrintACrot', 'Print'),
    B_print('CuiPrintACrot', 'Print (detailed)', details='true', memaddr='true'),
    B_print('CuiPrintACrot', 'Print (detailed, incl all sub objects)', details='true', subobjects='true'),
    B_print('CuiPrintACrot', 'Print (detailed + previous revision)', details='true', memaddr='true', prevrev='true'),
    ), title="A/C Rotation")

dbg_general = Menu('PrintDebug', (
    B_GPD('Print Blob (detailed)', level=BLOB, all=True),
    B_GPD('Print BlobLine (detailed)', level=BLOBLINE, all=True),
    B_GPD('Print SubWindow (detailed)', level=SUBWINDOW, all=True),
    B_GPD('Print Area (detailed)', level=AREA, all=True),
    ), title="General")

dbg_plan = Menu('PlanDebugMenu',
    (
        B_LP_Sanity(),
        Separator(title='LP'),
        Menu('PlanDebugMenuLP', (
            B_LP('Print LP'),
            B_LP('Print LP (detailed)', details='true'),
            B_LP('Print LP (incl all sub objects)', subobjects='true'),
            B_LP('Print LP (detailed, incl all sub objects)', details='true', subobjects='true'),
            ), title="Local Plan (main)"),
        Menu('PlanDebugMenuLP1', (
            B_LP('Print LP', plan='ref1'),
            B_LP('Print LP (detailed)', details='true', plan='ref1'),
            B_LP('Print LP (incl all sub objects)', subobjects='true', plan='ref1'),
            B_LP('Print LP (detailed, incl all sub objects)', details='true', subobjects='true', plan='ref1'),
            ), title="Local Plan (ref1)"),
        Menu('PlanDebugMenuLP2', (
            B_LP(plan='ref2', title='Print LP'),
            B_LP('Print LP (detailed)', details='true', plan='ref2'),
            B_LP('Print LP (incl all sub objects)', subobjects='true', plan='ref2'),
            B_LP('Print LP (detailed, incl all sub objects)', details='true', subobjects='true', plan='ref2'),
            ), title="Local Plan (ref2)"),
        Separator(title='SP'),
        Menu('PlanDebugSP', (
            B_SP(),
            B_SP('Print SP (detailed)', details='true'),
            B_SP('Print SP (incl all sub objects)', subobjects='true'),
            B_SP('Print SP (detailed, incl all sub objects)', details='true', subobjects='true'),
            ), title="Subplan"),
        Menu('PlanDebugSP1', (
            B_SP(plan='ref1', title='Print SP'),
            B_SP('Print SP (detailed)', details='true', plan='ref1'),
            B_SP('Print SP (incl all sub objects)', subobjects='true', plan='ref1'),
            B_SP('Print SP (detailed, incl all sub objects)', details='true', subobjects='true', plan='ref1'),
            ), title="Subplan (ref1)"),
        Menu('PlanDebugSP2', (
            B_SP(plan='ref2', title='Print ref2 SP'),
            B_SP('Print SP (detailed)', details='true', plan='ref2'),
            B_SP('Print SP (incl all sub objects)', subobjects='true', plan='ref2'),
            B_SP('Print SP (detailed, incl all sub objects)', details='true', subobjects='true', plan='ref2'),
            ), title="Subplan (ref2)"),
        Separator(title='ACOU'),
        Button('Print Object Diffs', 
            action=CSLEval('CuiPrintObjectDiffs(gpc_info)')),
        Button('Print Context Tree', 
            action=CSLEval('CuiPrintContextTree(gpc_info, "false")')),
        Button('Print Context Tree (detailed incl. diffs)', 
            action=CSLEval('CuiPrintContextTree(gpc_info, "true")')),
        Button('AcRot Onward Update', 
                action=CSLEval('CuiAcRot2Onward(gpc_info)')),
        ), title="Debug Menu")

dbg_plan.attach('OptionsMenu')

dbg_roster = Menu('RosterDebugMenu', (
        dbg_print_crr,
        dbg_print_chain,
        dbg_print_segment,
        dbg_print_leg,
        dbg_general,
    ), title="Debug Menu")

dbg_roster.attach('MainDat24CrewCompMode1')
dbg_roster.attach('MainDat24CrrMode1')
#dbg_roster.attach('MainStd24CrrMode1')
#dbg_roster.attach('LeftStd24CrrMode1')

dbg_leg = Menu('LegDebugMenu', (
        dbg_print_segment,
        dbg_print_leg,
        dbg_general,
        Separator(title="LEGKEY"),
        B_print('CuiPrintLegByLegKey', 'Print Leg by LegKey', details='true', memaddr='true', subobjects='true'),
        Button('Invert Marked Legs in Chain', action=CSLEval('CuiInvertMarked(gpc_info, CuiWhichArea, "Object")')),
        Button('Invert Marked Legs in Window', action=CSLEval('CuiInvertMarked(gpc_info, CuiWhichArea, "Window")')),
    ), title="Debug Menu")


dbg_leg.attach('MainDat24LegMode1')
dbg_leg.attach('MainDat24LegSetCompMode1')

dbg_acrot = Menu('ACRotDebugMenu', (
        dbg_print_acrot,
        dbg_print_segment,
        dbg_print_leg,
        dbg_general,
        Separator(title="LEGKEY"),
        B_print('CuiPrintLegByLegKey', 'Print Leg by LegKey', details='true', memaddr='true', subobjects='true'),
        Button('Invert Marked Legs in Chain', action=CSLEval('CuiInvertMarked(gpc_info, CuiWhichArea, "Object")')),
        Button('Invert Marked Legs in Window', action=CSLEval('CuiInvertMarked(gpc_info, CuiWhichArea, "Window")')),
    ), title="Debug Menu")

#dbg_acrot.attach('MainStd24AcCompMode1')
dbg_acrot.attach('MainDat24AcCompMode1')


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
