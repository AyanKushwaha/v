import Cui
import os
import carmensystems.rave.api as R
from AbsTime import AbsTime
from tm import TM
import modelserver

def update():
    print "recalc_standby_days_acc::update()"
    print "###################################################"

    TM(['accumulator_int'])
    TM.newState()
    ppend, = R.eval('fundamental.%pp_end%')
    ppstart, = R.eval('fundamental.%pp_start%')
    acclimit = ppend.month_floor()
    date = ppstart.addmonths(1).month_floor()

    dates = []
    while(date <= acclimit):
        dates.append(date)
        date = date.addmonths(1)

    crew_ids = [crew.crew.id() for crew in R.context("sp_crew").bag().iterators.roster_set()]

    Cui.CuiLoadPublishedRosters(Cui.gpc_info, crew_ids, "SCHEDULED")

    # Run all accumulators
    for d in dates:
        _update(d)

    print "###################################################"


def _update(date):
    changed = 0
    data, = R.eval('plan_1_sp_crew',
                   R.foreach(R.iter('iterators.roster_set'),
                             'crew.%id%',
                             'accumulators.standby_days_acc(01Jan1986,%s)' % date))
    
    for (ix,crew,val1) in data:
        if val1 != None:
            try:
                entry = TM.accumulator_int[('accumulators.standby_days_acc',crew,date)]
                if val1 != entry.val:
                    print "CHANGED STANDBY_DAYS_ACC %s, %s, %s --> %s"% (crew, date, entry.val, val1)
                    entry.val = val1
                    changed+=1
            except modelserver.EntityNotFoundError:
                entry = TM.accumulator_int.create(('accumulators.standby_days_acc',crew,date))
                entry.val = val1
                changed+=1


    print "Changed acc values for date [%s]: %s"% (date,changed)


def save_close():
    print "recalc_standby_days_acc::save_close()"
    TM.save()
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

print "::recalcReducedMonthAcc::"
update()
save_close()
