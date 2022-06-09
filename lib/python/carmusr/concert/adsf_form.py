'''
ADSF export settings form
Used to pick a PMP and data context, and to optionally define planning areas and scenario names.

Initial version by Arvid M-A, Jeppesen 2015.
'''
import os
import tempfile
import weakref

from Localization import MSGR
import Cfh
import Gui

import carmusr.fatigue_compat.ots_message as message
from carmusr.concert import adsf

if __name__ == "__main__":
    raise NotImplementedError("Do not run this file as a script.")


class ADSFFormError(Exception):
    pass


class FileExportButton(Cfh.Function):
    def __init__(self, parent, name, field, kind):
        self.field = weakref.ref(field)
        self.kind = kind
        self.parent = weakref.ref(parent)
        Cfh.Function.__init__(self, parent, name)

    def action(self):
        _key = self.field().getValue()

        pmp = self.parent().pmp.getValue()
        pmp = adsf.PMPS[pmp]
        bagtype = self.parent().bagtype.getValue()
        bagtype = adsf.BAGS[bagtype]

        use_planning_area = (self.parent().planningarea_toggle.getValue() == "True")
        planning_area = self.parent().planningarea.getValue()

        toggle_scenario = (self.parent().toggle_scenario.getValue() == "True")
        scenario = self.parent().scenario.getValue()

        try:
            result = adsf.run(bagtype, pmp, use_planning_area, planning_area, toggle_scenario, scenario)
        except Exception:
            import traceback
            result = traceback.format_exc()

        message.show_text(MSGR("ADSF Export Result"), result)


class ADSFForm(Cfh.Box):

    the_default_form = None

    def __init__(self):

        self.default_out = None

        Cfh.Box.__init__(self, "ADSFForm")

        _len = max(len(l) for l in adsf.PMPS.keys())
        self.pmp = Cfh.String(self, "PMP", _len, adsf.guess_the_pmp()[0])

        _len = max(len(l) for l in adsf.BAGS.keys())
        self.bagtype = Cfh.String(self, "BAGTYPE", _len, adsf.guess_the_bag())

        self.planningarea_toggle = Cfh.Toggle(self, "PLANNINGAREA_T", False)
        self.planningarea = Cfh.String(self, "PLANNINGAREA", 30)

        self.toggle_scenario = Cfh.Toggle(self, "SCENARIO", False)
        self.scenario = Cfh.String(self, "SCENARIONAME", 30)

        self.close = Cfh.Cancel(self, "CLOSE")
        self.expfile_btn = FileExportButton(self, "EXPORTF_BUTTON", self.pmp, MSGR("Save ADSF file"))

        lo = ["FORM;ADSFForm;%s" % MSGR("Export to Concert"),
              "MENU;VALUES;%s" % (";".join(MSGR(k) for k in adsf.PMPS.keys())),
              "FIELD;PMP;PMP;%s" % MSGR("The relevant Process Measurement Point for your data-set"),
              "MENU;VALUES;%s" % (";".join(MSGR(k) for k in adsf.BAGS.keys())),
              "FIELD;BAGTYPE;%s" % MSGR("Data selection"),
              "FIELD;PLANNINGAREA_T;%s" % MSGR("Use Concert planning area"),
              "FIELD;PLANNINGAREA;%s;%s" % (MSGR("Concert planning area name"),
                                            MSGR("The planning area is subset of the current PMP, i.e A320 FD pairings.")),
              "",
              "GROUP",
              "LABEL;%s" % MSGR("Scenarios are used for analysing \"one-off\" data-sets in Concert"),
              "FIELD;SCENARIO;%s" % MSGR("Toggle scenario mode"),
              "FIELD;SCENARIONAME;%s;%s" % (MSGR("Scenario name"),
                                            MSGR("The scenario name is displayed together with date range, PMP and PA in Concert.")),
              "",
              "BUTTON;CLOSE;%s;_C" % MSGR("Close"),
              "BUTTON;EXPORTF_BUTTON;%s;_i" % MSGR("Save ADSF")]

        fd, filepath = tempfile.mkstemp()
        os.write(fd, "\n".join(lo))
        os.close(fd)
        self.load(filepath)
        os.unlink(filepath)


ADSFForm.the_default_form = ADSFForm()


def do():
    try:
        ADSFForm.the_default_form.show(1)
    except ADSFFormError, e:
        Gui.GuiMessage(MSGR("Error. %s." % e))
