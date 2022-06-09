##########################
#
# Update reschedule info
#
##########################
"""
The script will reset reschedule info after assignments have been fetched from a file 
base rostering in order for the new assignments to be considered not rescheduled.
The script is supposed to be run after a re-planning in rostering and after the script PrepareForJCTImport.py
has been run and assignments have been fetched to the tracking plan.

"""

import Cfh
import Cui
import Localization
import AbsTime
import Errlog
import carmensystems.rave.api as rave
import carmstd.cfhExtensions as cfhExtensions
import carmusr.tracking.Rescheduling as Rescheduling


def inputDate(label, default = "", form_name = "INPUT_BOX", title = "Update published info"):
    """
    Shows a box containing a label with an input field, optionally using a
    specified title. 
    """
  
    box = Cfh.Box(form_name, title)

    l = Cfh.Label(box,"LABEL",label)
    l.setLoc(Cfh.CfhLoc(1,0))

    i = Cfh.Date(box,"INPUT",Cfh.CfhArea(2, 0, 20, 1))

    y = Cfh.Done(box,"OK")
    y.setText(Localization.MSGR("Ok"))
    y.setMnemonic(Localization.MSGR("_OK"))
  
    n = Cfh.Cancel(box,"CANCEL")
    n.setText(Localization.MSGR("Cancel"))
    n.setMnemonic(Localization.MSGR("_Cancel"))
  
    box.build()
    box.show(1)
    if box.loop() == Cfh.CfhOk:
        return i.valof()
    else:
        return None


def updatePuplishedInfo():
    """
    Update publish info for crew selected in crew header
    """
    default_bag = rave.context('marked_in_window_left').bag()
    crewlist = [roster_bag.crew.id() for roster_bag in default_bag.iterators.roster_set()]

    if len(crewlist) == 0:
        cfhExtensions.show("No crew selected.")
        return

    start_date_cfh = inputDate("From date", form_name="Update rescheduling info", title="Update rescheduling info for selected crew")
    if not start_date_cfh:
        return
        
    start_date = AbsTime.AbsTime(start_date_cfh)
    
    end_date, = rave.eval("round_up_month({0} + 0:01)".format(start_date))


    start_str = str(start_date).split(" ")[0]
    end_str = str(end_date).split(" ")[0]
    message = "Update reschedule info for {0} crew in period {1} -{2}?\nThe plan will be saved.".format(len(crewlist), start_str, end_str)
    if not cfhExtensions.confirm(message):
        return

    Rescheduling.publish(crew_list=crewlist,
                         start_date=start_date,
                         end_date=end_date,
                         sel_mode=Rescheduling.ROSTER_PUBLISH)
    try:
        Cui.CuiSavePlans(Cui.gpc_info,Cui.CUI_SAVE_DONT_CONFIRM+Cui.CUI_SAVE_SILENT+Cui.CUI_SAVE_FORCE)
    except:
        Errlog.message("Plan could not be saved.")

def update():
    updatePuplishedInfo()
