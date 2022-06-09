"""
adsf.py
Main module of Concert ADSF export package for Studio.

This is the entry point for your carmusr-customization, which should be carried
out in a separate module. The customized module should provide a settings dict
based on the one defined below ("SETTINGS"), and a rave bag description fitting
one of the alternatives in "get_bag_from_desc()" below.

Arvid M-A, Jeppesen 2016
"""

import datetime
import os.path

from Localization import MSGR
import Cui

import carmusr.concert.log
import carmusr.fatigue_compat.ots_bag_handler as bag_handler
import adsf_writer

logger = carmusr.concert.log.get_logger()

# These dicts are referenced form the ADSF export form. If you change any canonical
# names, don't forget to modify the the guess_* functions below as well. The keys are
# localized, since they are used for display in the GUI.
BAGS = {MSGR("Window 1"): "window",
        MSGR("Sub-plan"): "subplan",
        MSGR("Marked trips in window 1"): "marked_trips_main",
        MSGR("Marked rosters in window 1"): "marked_rosters_left"}
PMPS = {MSGR("Published Rosters"): 300,
        MSGR("Flown Rosters"): 500,
        MSGR("Published Pairings"): 200,
        MSGR("Timetable analysis"): 100}


# The run() function is invoked from the ADSF export form
def run(bag_description, pmp, use_planning_area=False, planning_area="", toggle_scenario=False, scenario=""):
    logger.info("ADSF export in progress")
    bag_handler = get_bag_from_desc(bag_description, pmp)
    settings = standard_settings(bag_handler, pmp)

    if use_planning_area:
        settings["planning_area"] = planning_area

    if toggle_scenario:
        settings["scenario_name"] = scenario

    return generate_adsf_export(bag_handler, settings)


def get_bag_from_desc(bag_desc, pmp):
    logger.info("get_bag_from_desc(%s, %i)" % (bag_desc, pmp))
    if bag_desc == 'marked_trips_main':
        if pmp >= 300:
            raise Exception("Cannot export trip bag for rostering PMP")
        tbh = bag_handler.MarkedTripsMain(Cui.CuiArea0)

    elif bag_desc == 'marked_rosters_left':
        if pmp < 300:
            raise Exception("Cannot export roster bag for pairing PMP")
        tbh = bag_handler.MarkedRostersLeft(Cui.CuiArea0)

    elif bag_desc == 'window':
        tbh = bag_handler.WindowChains(Cui.CuiArea0)

    elif bag_desc == 'subplan':
        if pmp < 300:
            tbh = bag_handler.PlanTrips()
        else:
            tbh = bag_handler.PlanRosters()

    else:
        raise Exception("Bag could not be created based on description: '%s'" % bag_desc)

    if tbh.warning:
        logger.warn(tbh.warning)

    return tbh


def standard_settings(bag_handler, pmp):
    bag = bag_handler.bag
    if bag is None:
        raise Exception("Bag was None. Empty window?")
    return {"adsf_location": get_adsf_location(),
            "airline": bag.report_adsf.airline(),
            "pp_start": bag.report_adsf.pp_start(),
            "pp_end": bag.report_adsf.pp_end(),
            "pmp": pmp,
            "forecast_time": get_now()}


def get_adsf_location():
    ADSF_LOCATION = os.path.expandvars("$CARMDATA/ADSF_FILES/")
    if not os.path.exists(ADSF_LOCATION):
        os.makedirs(ADSF_LOCATION)
    return ADSF_LOCATION


def get_now():
    return str(datetime.datetime.strftime(datetime.datetime.now(), '%d%b%Y %H:%M')).upper()


def generate_adsf_export(bag_handler, settings):
    logger.info(settings)
    adsf_temp = adsf_writer.ADSFWriter(settings)
    bag = bag_handler.bag
    for chain_bag in bag.fatigue_mappings.frms_chain_set(where='report_adsf.%consider_chain%'):
        md, cd_list = make_entries_from_chain(chain_bag)
        adsf_temp.write(md, cd_list)

    s = "%i chains with %i legs were included in the exported data set" % (adsf_temp.chain_count,
                                                                           adsf_temp.leg_count)
    s += adsf_temp.finalize()
    s += "\n\nExport settings:\n"
    s += "\n".join("  %s : %s" % (str(k), str(v)) for k, v in sorted(settings.iteritems()))
    logger.info(s)
    return s


def make_entries_from_chain(chain_bag):
    """function to add one roster or trip"""
    # Default variables moved from report_adsf Rave module to avoid compiler warnings
    height = -1
    weight = -1

    cm = chain_bag.report_adsf
    chainref = cm.chainref()
    md = [chainref,
          cm.birthyear(), cm.gender(), weight, height,
          cm.chain_position_string(),
          cm.diurnal_type(), cm.habitual_sleep_length(),
          cm.homebasecommute(), cm.fte_ratio(), 0,
          cm.homebase(), cm.acqual(),
          cm.chain_custom_attribute_1(), cm.chain_custom_attribute_2()]
    cd_list = list()
    for leg_bag in chain_bag.fatigue_mappings.frms_leg_set(sort_by="report_adsf.%departure_utc%",
                                                           where="report_adsf.%consider_activity%"):
        lm = leg_bag.report_adsf
        cd_list.append([chainref,
                        1, lm.departure_utc(), lm.arrival_utc(),
                        lm.departure_lt(), lm.arrival_lt(),
                        lm.departure_station(), lm.arrival_station(),
                        lm.flightnum(), lm.acfamily(), lm.briefing(), lm.debriefing(),
                        lm.wake_before(), lm.wake_after(), lm.sleep_type_before(),
                        lm.nap1start(), lm.nap1end(), lm.nap1type(),
                        lm.nap2start(), lm.nap2end(), lm.nap2type(), -1, -1, 3,
                        lm.activity_type(), lm.arrlatitude(), lm.arrlongitude(),
                        lm.ac_change(), lm.first_in_duty(), lm.augmentation(),
                        lm.leg_custom_attribute_1(), lm.leg_custom_attribute_2()])

    return md, cd_list


def guess_the_pmp():
    """ Used too much modern OTS code to be portable to SAS. Replaced with dummy.  """
    pmp_name = MSGR("Published Pairings")
    return (pmp_name, PMPS[pmp_name])


def guess_the_bag():
    """ Used to pre-populate the data source field in the ADSF form """
    return MSGR("Sub-plan")
