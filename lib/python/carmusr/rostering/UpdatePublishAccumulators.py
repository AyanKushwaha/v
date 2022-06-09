##################################
#
# Update publication accumulators
#
##################################
"""
The script will open a form where you can either
* Select a month and update all accumulators that are run on roster publish
* Select a month and some accumulators that are run on roster publish
* Marked crew are updated
"""

import Cfh
import Cui
import Localization
import AbsTime
import Errlog
import carmensystems.rave.api as rave
import carmstd.cfhExtensions as cfhExtensions
import carmusr.Accumulators as Accumulators

PUBLISH_ACCUMULATORS = ["fdc15_nr_possibly_scheduled_freedays_acc",
                        "fdc15_nr_entitled_freedays_acc",
                        "duty_time_planned_skd_acc",
                        "last_free_weekend_acc",
                        "qual_freedays_acc",
                        "reduced_months_skn_acc",
                        "va_days_acc",
                        "va_days_pt_acc",
                        "loa_days_pt_acc",
                        "required_freedays_month_2_month_acc",
                        "skbu_resource_planned_working_days_acc",
                        "standby_blocks_acc",
                        "short_standby_block_date_acc",
                        "standby_line_date_acc",
                        "blank_days_acc",
                        "standby_days_acc",
                        "standby_line_days_acc",
                        "scattered_standby_days_acc",
                        "standby_lines_acc",
                        "airport_standby_date_acc",
                        "standby_date_acc",
                        "qual_pt_freedays_acc",
                        "required_pt_freedays_month_2_month_acc",
                        "required_freedays_month_3_month_acc",
                        "non_qualifying_days_fulltime_fc_sh_acc",
                        "non_qualifying_days_cc_skn_acc",
                        "nr_freedays_fulltime_fc_sh_acc",
                        "nr_p_days_fc_skd_acc",
                        "nr_production_days_skn_acc",
                        "nr_planned_p_days_fc_fg_acc",
                        "nr_planned_p_days_fc_vg_acc",
                        "planned_duty_time_fc_fg_acc",
                        "planned_duty_time_fc_vg_acc",
                        "nr_planned_sb_ln_days_cc_acc",
                        "nr_planned_p_days_cc_acc",
                        "nr_planned_p_days_skn_cc_acc",
                        "planned_duty_time_cc_acc",
                        "planned_duty_time_skn_cc_acc",
                        "actual_duty_time_skn_cc_scheduled_acc",
                        "fdc15_nr_entitled_freedays_qa_2_months_acc",
                        "nr_planned_instr_sim_duty_acc",
                        "nr_planned_sim_duty_as_tr_acc",
                        "nr_far_single_slipping"]


def inputForm(label="Publication month", default = "", form_name = "INPUT_BOX", title = "Update", all_accus=False):
    """
    Shows a box containing a label with an input date field
    And possibly a list of accumulators

    """
    default_start,  = rave.eval('accumulators.%publ_acc_start%')

    if all_accus:
        publ_accumulators = []
    else:
        publ_accumulators = PUBLISH_ACCUMULATORS

    box = Cfh.Box(form_name, title)

    l = Cfh.Label(box,"LABEL",label)
    l.setLoc(Cfh.CfhLoc(2, 1)) # row 2 col 1

    i = Cfh.Date(box,"MONTH",Cfh.CfhArea(2, 12, 20, 1))
    start_str = str(default_start).split(" ")[0]
    i.setMandatory()
    i.assign(start_str)

    rows_per_column = (len(publ_accumulators)+1)/2

    labels = []
    togs = []
    for idx, accu in enumerate(publ_accumulators):

        if idx < rows_per_column:
            # First column
            togs.append(Cfh.Toggle(box, "INPUT", Cfh.CfhArea(Cfh.CfhLoc(idx + 4, 1)), False)) # row, col
            labels.append(Cfh.Label(box,"LABEL", accu))
            labels[idx].setLoc(Cfh.CfhLoc(idx + 4, 8))
        else:
            # Second column
            togs.append(Cfh.Toggle(box, "INPUT", Cfh.CfhArea(Cfh.CfhLoc(idx - rows_per_column + 4, 35)), False)) # row, col
            labels.append(Cfh.Label(box,"LABEL", accu))
            labels[idx].setLoc(Cfh.CfhLoc(idx - rows_per_column + 4, 42))


    y = Cfh.Done(box,"OK")
    y.setText(Localization.MSGR("Ok"))
    y.setMnemonic(Localization.MSGR("_OK"))
  
    n = Cfh.Cancel(box,"CANCEL")
    n.setText(Localization.MSGR("Cancel"))
    n.setMnemonic(Localization.MSGR("_Cancel"))
  
    box.build()
    box.show(1)
    if box.loop() == Cfh.CfhOk:
        accu_list = []
        for idx, accu in enumerate(publ_accumulators):
            if togs[idx].valof():
                accu_list.append("accumulators.{0}".format(accu))

        return i.valof(), accu_list
    else:
        return None, None


def updateAccu(all_acc=False):
    """
    Update publish info for crew selected in crew header
    """
    default_bag = rave.context('marked_in_window_left').bag()
    crewlist = [roster_bag.crew.id() for roster_bag in default_bag.iterators.roster_set()]

    if len(crewlist) == 0:
        cfhExtensions.show("No crew selected.")
        return

    rave.param("accumulators.%accumulator_mode%").setvalue(True)
    rave.param("accumulators.%job_publication_p%").setvalue(True)

    start_date_cfh, accu_list = inputForm(title = "Update publish accumulators", all_accus=all_acc)
    if not start_date_cfh:
        return

    if (not all_acc) and (len(accu_list) == 0):
        cfhExtensions.show("No accumulators selected.")
        return

    start_date = AbsTime.AbsTime(start_date_cfh)
    
    end_date, = rave.eval("round_up_month({0} + 0:01) + 0:01".format(start_date))
    print "START: " + str(start_date)
    print "ACCUS: "
    print accu_list

    publ_acc_start, =  rave.eval('accumulators.%publ_acc_start%')

    if start_date != publ_acc_start:
        rave.param("accumulators.%is_publ_debug_p%").setvalue(True)
    rave.param("accumulators.%acc_start_p%").setvalue(start_date)
    rave.param("accumulators.%acc_end_p%").setvalue(end_date)


    publ_acc_start, publ_acc_end =  rave.eval('accumulators.%publ_acc_start%', 'accumulators.%publ_acc_end%')

    current_area = Cui.CuiScriptBuffer
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, current_area, Cui.CrewMode, Cui.CrewMode, crewlist)

    start_str = str(publ_acc_start).split(" ")[0]
    end_str = str(publ_acc_end).split(" ")[0]
    message = "Update publish accumulators for {0} crew for period {1} -{2}?\n\n".format(len(crewlist), start_str, end_str)

    if not all_acc:
        message = message + "The following accumulators will be updated:\n"
        for accu in accu_list:
            message = message + " -  " + accu + "\n"


    if not cfhExtensions.confirm(message):
        return

    Accumulators.accumulatePublished(current_area, accu_list)

def setBackAccuParams():
    rave.param("accumulators.%is_publ_debug_p%").setvalue(False)
    rave.param("accumulators.%accumulator_mode%").setvalue(False)
    rave.param("accumulators.%job_publication_p%").setvalue(False)

def updateSome():
    """
    Select and Update publish accumulators
    """
    PUBLISH_ACCUMULATORS.sort()
    updateAccu()
    setBackAccuParams()

def updateAll():
    """
    Update all publish accumulators
    """
    updateAccu(all_acc=True)
    setBackAccuParams()
