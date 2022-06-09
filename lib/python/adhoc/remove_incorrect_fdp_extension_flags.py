from utils.rave import RaveIterator
import Cui
import utils.selctx as selctx
from carmusr.tracking.Rescheduling import FlagSet
from tm import TM
from AbsTime import AbsTime
from datetime import datetime
import os
import carmensystems.rave.api as R

def current_time():
    return datetime.now().strftime('%d%b%Y %H:%M')

pp_start,pp_end = R.eval('fundamental.%pp_start%', 'add_months(fundamental.%pp_start%,1)')

carmtmp_path = os.environ['CARMTMP']
filepath = carmtmp_path + '/logfiles/cmd_remove_incorrect_fdp_extension_flags' + datetime.now().strftime('.%Y%m%d.%H%M')
logfile = open(filepath,'wb')
logfile.write(current_time()+" :: Starting check for incorrectly set fdp extension flags for period %s - %s\n" % (pp_start, pp_end)) 

#Find legs which were published as being an fdp extension in Planning but not in Tracking.
legFilter = 'rescheduling.%leg_inf_has_extended_fdp% and not oma16.%is_extended_fdp% and rescheduling.%leg_start_date_hb% >= fundamental.%pp_start%'
li = RaveIterator(RaveIterator.iter('iterators.leg_set', where=legFilter), {'crewid' : 'crew.%id%', 'start_date_hb' : 'rescheduling.%leg_start_date_hb%'})
legs = li.eval('sp_crew')

FlagSet._cls_init()

start_date_hb = []
leg_start_dates = {}
for leg in legs:
    if leg.crewid not in leg_start_dates.keys():
        leg_start_dates[leg.crewid] = []
    leg_start_dates[leg.crewid].append(leg.start_date_hb)

for crewid in leg_start_dates.keys():
    crew = TM.crew[(crewid,)]
    for db_entry in crew.referers("crew_publish_info", "crew"):
        if db_entry.flags and FlagSet.subq_extended_fdp in db_entry.flags:
            for leg_start_date in leg_start_dates[crewid]:
                if AbsTime(db_entry.start_date) <= leg_start_date and AbsTime(db_entry.end_date) > leg_start_date:
                    flags = FlagSet(db_entry.flags)
                    flags -= FlagSet.subq_extended_fdp
                    flags += FlagSet.subq_non_extended_fdp
                    db_entry.flags = str(flags)
                    leg_start_dates[crewid].remove(leg_start_date)
                    logfile.write(current_time()+" :: Removed subq extension flag for crew: %s on date: %s\n" %(crewid, leg_start_date))
logfile.write(current_time()+" :: Finished checking for incorrectly set fdp extension flags\n")
logfile.close()
TM.save()
Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
