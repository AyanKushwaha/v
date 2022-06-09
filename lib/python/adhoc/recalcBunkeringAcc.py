import Cui
import os
import carmensystems.rave.api as R
from AbsTime import AbsTime
from RelTime import RelTime
import carmusr.Accumulators as Accumulators
import carmensystems.rave.api as rave
import carmusr.modcrew as modcrew
import carmusr.ConfirmSave as cs

def update():
    print "sks_376_prod_days_accu::update()"
    print "###################################################"
    
    ppend, = R.eval('fundamental.%pp_end%')
    ppstart, = R.eval('fundamental.%pp_start%')

    print "Start --- recalculating accumulators"
    print 'ppstart: {0}'.format(ppstart)
    print 'ppend: {0}'.format(ppend)

    acclimit = ppend.month_floor()
    date = ppstart.addmonths(1).month_floor()

    print 'Recalculating Accumulators DEBUG: acclimit: {0}'.format(acclimit)
    print 'Recalculating Accumulators DEBUG: date: {0}'.format(date)

    dates = []
    while(date <= acclimit):
        dates.append(date)
        date = date.addmonths(1)
    print 'Recalculating Accumulators: {0}'.format(dates)

    for d in dates:
        print 'Recalculating Accumulators for {0}: STARTING'.format(d)
        _update(d)
        print 'Recalculating Accumulators for {0}: COMPLETED'.format(d)

    print "###################################################"
    

def _update(date):
    rave_accus = ["accumulators.nr_bunkering_reducing_activities",
                  "accumulators.nr_bunkering_banked_days",
                  "accumulators.nr_bunkering_recovered_days",
                  "accumulators.nr_actual_prod_days_acc"]

    ###
    default_bag = rave.context('sp_crew').bag()
    crewlist = [roster_bag.crew.id() for roster_bag in default_bag.iterators.roster_set()]

    for crewid in crewlist:
        modcrew.add(crewid)

    start_date = date
    end_date = date.addmonths(1)+RelTime("0:01")
    print 'Recalculating Accumulators range {0} to {1}'.format(start_date, end_date)

    current_area = Cui.CuiScriptBuffer
    Cui.CuiDisplayGivenObjects(Cui.gpc_info, current_area, Cui.CrewMode, Cui.CrewMode, crewlist)
    Accumulators.accumulate_rave(start_date, end_date, current_area, rave_accus)


def save_close():
    print "recalc_standby_days_acc::save_close()"
    Cui.CuiSyncModels(Cui.gpc_info)

    cs.skip_confirm_dialog = True #Set global variable in carmusr/ConfirmSave.py
    try:
        Cui.CuiSavePlans(Cui.gpc_info,Cui.CUI_SAVE_DONT_CONFIRM+Cui.CUI_SAVE_SILENT+Cui.CUI_SAVE_FORCE)
    except:
        pass
    modified_crew = len(modcrew.get())
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

print "::recalcBunkeringAcc::"
update()
save_close()
