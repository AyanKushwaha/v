"""
    Export per-flight fatigue predictions for consumption by Enplore
     `Export to Enplore`
        f.exec PythonEvalExpr("__import__('carmusr.fatigue.enplore').fatigue.enplore.export(bag_description='')")

"""
import json
import urllib2

from datetime import datetime
import os
import getpass

import hashlib
from collections import OrderedDict

from BSIRAP import RelTime, AbsTime
import Cui
import carmensystems.rave.api as rave
import carmusr.concert.log as log

logger = log.get_logger()

class headerStr:
    # using only class variable
    crewid_md5 = "crewid_md5"
    leg_id = "leg_id"
    leg_actual_start_time = "leg_actual_start_time"
    position = "position"
    rank = "rank"
    lifetime_experience_actype = "lifetime_experience_actype"
    alertness_tod = "alertness_tod"
    leg_afr = "leg_afr"
    time_since_sleep_opportunity = "time_since_sleep_opportunity"
    time_since_last_pred_sleep = "time_since_last_pred_sleep"
    total_pred_sleep_in_48h = "total_pred_sleep_in_48h"
    days_on_duty = "days_on_duty"

    header_str_list = [crewid_md5,
                       leg_id,
                       leg_actual_start_time,
                       position,
                       rank,
                       lifetime_experience_actype,
                       alertness_tod,
                       leg_afr,
                       time_since_sleep_opportunity,
                       time_since_last_pred_sleep,
                       total_pred_sleep_in_48h,
                       days_on_duty,
                      ]


def get_export_path():
    directory = os.path.expandvars("$CARMTMP/ENPLORE")
    if not os.path.exists(directory):
       os.makedirs(directory)

    now = datetime.today().strftime('%Y-%m-%d_%H.%M.%S')
    return "%s/%s_%s.csv" % (directory, getpass.getuser(), now)


def write_csv_header(header_str):
    csv_header_line = ""
    for elem in header_str:
        csv_header_line += elem + "," + " "

    csv_header_line += "\n"

    return csv_header_line


def get_time_since_last_pred_sleep(chain_bag, start, end):
    step = RelTime("00:15")
    ival_start = start
    ival_end = end
    alertnessvalues = chain_bag.capi_test(ival_start, ival_end, step)
    ix = 0
    time = 0
    for value in alertnessvalues[::-1]:
        ix += 1
        if value < 0:
            time = RelTime(ix * 15)
            break
        elif value > 0:
            continue
    if time == 0:
        return RelTime("-01:00")
    else:
        return time


def get_total_sleep_48h(chain_bag, start, end):
    step = RelTime("00:15")
    # Format: AbsTime("01JAN2018 10:00")
    ival_start = start
    # Format: AbsTime("03JAN2018 10:00")
    ival_end = end
    alertnessvalues = chain_bag.capi_test(ival_start, ival_end, step)
    count = sum(map(lambda x: x < 0, alertnessvalues))
    return RelTime(count * 15)


def make_entries_by_crew(crewid, leg_bags):
    crewid_md5 = hashlib.md5(crewid).hexdigest()
    crew_data = []
    hs = headerStr()

    for leg_bag in leg_bags:
        d = OrderedDict()
        crew_data_line = ""
        m = leg_bag.report_enplore_fatigue
        search_value = 0
        search_value_48h = 0

        valid_leg = m.is_valid_enplore_leg()
        if valid_leg:
            d[hs.crewid_md5] = crewid_md5
            d[hs.leg_id] = "%s" % (m.leg_flight_descriptor())
            d[hs.leg_actual_start_time] = leg_bag.activity_actual_start_time()
            d[hs.position] = m.leg_position()
            d[hs.rank] = m.crew_rank()
            d[hs.lifetime_experience_actype] = m.lifetime_blocktime_on_actype()
            d[hs.alertness_tod] = m.leg_alertness_tod()
            d[hs.leg_afr] = m.leg_afr()

            provisionnal_time_since_sleep_opportunity = m.time_since_sleep_opportunity()

            search_period_start = m.time_since_last_pred_sleep_period_start()
            search_period_end = m.time_since_last_pred_sleep_period_end()
            search_48h_period_start = m.total_pred_sleep_48h_period_start()

            if search_period_start and search_period_end:
                if search_period_end > search_period_start:
                    search_value = get_time_since_last_pred_sleep(leg_bag,
                                                                  search_period_start,
                                                                  search_period_end)

            search_value_48h = get_total_sleep_48h(leg_bag,
                                                   search_48h_period_start,
                                                   search_period_end)
            time_since_pred_sleep = m.time_on_duty_since_sleep_period_end() + search_value
            if provisionnal_time_since_sleep_opportunity < time_since_pred_sleep:
                d[hs.time_since_sleep_opportunity] = provisionnal_time_since_sleep_opportunity
            else:
                d[hs.time_since_sleep_opportunity] = time_since_pred_sleep

            d[hs.time_since_last_pred_sleep] = time_since_pred_sleep
            d[hs.total_pred_sleep_in_48h] = search_value_48h
            d[hs.days_on_duty] = m.consecutive_working_days()
            for key in d.keys():
                crew_data_line += str(d[key]) + "," + " "
            crew_data_line += "\n"
            crew_data.append(crew_data_line)

    return crew_data


try:
    from nth.studio.message import show_text

except ImportError:
    from tempfile import mktmp
    import Csl
    csl = Csl.Csl()

    def _show_file(title, filepath):
        csl.evalExp('csl_show_file("%s", "%s")' % (title, filepath))

    def show_text(title, text):
        fn = mktmp()
        f = open(fn, 'w')
        f.write(text)
        f.close()
        _show_file(title, fn)
        os.unlink(fn)


def show_export_path(path):
    text_to_show = ""
    text_to_show = path + "\n\n"

    show_text("Enplore Export", text_to_show)


def export(bag_description, target="show", debug=False):

    exp_path = get_export_path()
    hsl = headerStr.header_str_list

    if target == "show":
        show_export_path(exp_path)

    f = open(exp_path, 'w')
    f.write(write_csv_header(hsl))
    import carmusr.fatigue_compat.ots_bag_handler as bag_handler
    tbh = bag_handler.PlanRosters()
    for chain_bag in tbh.bag.fatigue_mappings.frms_chain_set(where="report_adsf.%consider_chain%\
                                                             and report_enplore_fatigue.%is_valid_roster_chain%"):
        leg_bags = chain_bag.fatigue_mappings.frms_leg_set(sort_by="capi.%departure_utc%",
                                                           where="report_adsf.%consider_chain%\
                                                           and report_enplore_fatigue.%is_valid_trip_chain%")

        crew_data =[] 
        crew_data = make_entries_by_crew(chain_bag.report_enplore_fatigue.chainref(), leg_bags)

        for crew_line in crew_data:
            f.write(crew_line)
    
    f.close

if __name__ == '__main__':
    
    export(bag_description="")


