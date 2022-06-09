import Cui
import os
import carmensystems.rave.api as R
from AbsTime import AbsTime
from tm import TM
import modelserver

def update():
    print "recalcReducedMonthAcc::update()"
    print "###################################################"
    
    ppend, = R.eval('fundamental.%pp_end%')
    ppstart, = R.eval('fundamental.%pp_start%')
    acclimit = ppend.addmonths(1).month_floor()
    date = ppstart.addmonths(1).month_floor()

    dates = []
    while(date <= acclimit):
        dates.append(date)
        date = date.addmonths(1)

    for d in dates:
        _update(d)

    print "###################################################"
    

def _update(date):
    changed = 0
    data, = R.eval('sp_crew',
                   R.foreach(R.iter('iterators.roster_set'),
                             'crew.%id%',
                             'accumulators.reduced_months_skn_acc(01Jan2012,%s)' % date))
        
    for (ix,crew,val) in data:
        if val is None:
            continue

        try:
            entry = TM.accumulator_int[('accumulators.reduced_months_skn_acc',crew,date)]
            if val != entry.val:
                entry.val = val
                changed+=1
        except modelserver.EntityNotFoundError:
            continue

    print "Changed acc values for date [%s]: %s"% (date,changed)


def save_close():
    print "recalcReducedMonthAcc::save_close()"
    TM.save()
    Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

print "::recalcReducedMonthAcc::"
update()
save_close()
