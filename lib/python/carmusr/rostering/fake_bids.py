"""
create some preference bids for every crew in the plan.
"""
import itertools
import os
import random
import re
import time

from carmstd import bag_handler
from carmensystems.rave import api as rave

LIFESTYLES_ALL = ["nights_at_home_pref", "early_ends_pref", "late_starts_pref", "west_destinations_pref",
              "east_destinations_pref", "nights_at_home_early_ends_pref", "nights_at_home_late_starts_pref",
              "commuter_2_3_days_pref", "commuter_3_5_days_pref", "commuter_2_3_days_early_ends_pref", "commuter_2_3_days_late_starts_pref",
              "commuter_3_5_days_early_ends_pref", "commuter_3_5_days_late_starts_pref", "any_longhaul_destinations_pref",]

STRICTLY_LH_KEY = 'SKI'

LH_LIFESTYLES = [
    "west_destinations_pref", "east_destinations_pref",
]

ETABLE_PATH = os.path.join(os.path.expandvars("$CARMDATA"), "ETABLES/PBS/BIDS")
DEF_VAL = "01Jan1986"

SAS_BIDS_MAP = {
    "CC_SKS_201710": "SAS_bids_cc_sks.csv",
    "FD_SKI_201710": "SAS_bids_fd_ski.csv",
    "FD_SKI_201707": "SAS_bids_fd_ski.csv",
    "FD_SKN_201710": "SAS_bids_fd_skn.csv"
}


def get_example_bids(plan_name, etables_path):
    bids_parsed = []
    try:
        real_bids_path = os.path.join(etables_path, SAS_BIDS_MAP[plan_name])
        with open(real_bids_path) as bidf:
            idx = None
            scen_arr = []
            for line in bidf.readlines():
                curr_idx = line.split(',')[0]
                if curr_idx != idx:
                    idx = curr_idx
                    if scen_arr != []:
                        bids_parsed.append(scen_arr)
                        scen_arr = []
                scen_arr.append(line.strip())
    except (KeyError, IOError):
        bids_parsed = []
    return bids_parsed


def get_pure_lifestyles(plan_category):
    lifestyle_bids = []
    for lifestyle in itertools.chain(LIFESTYLES_ALL, LH_LIFESTYLES):
        header = get_bid_header()
        bidline = get_preference_line(lifestyle)
        lifestyle_bids.append([header, bidline])
    return lifestyle_bids


def get_plan_category():
    bag_wrapper = bag_handler.WindowChains()
    bag = bag_wrapper.bag
    return bag.keywords.fp_version()


def insert_crew_id(crew_id, line):
    return re.sub("[0-9]{5}", crew_id, line)


def has_lh_restricted_bids(bid_list):
    for bidline in bid_list:
        for lh_lifestyle in LH_LIFESTYLES:
            if lh_lifestyle in bidline:
                return True
    return False


def has_no_lifestyle_bids(bid_list):
    return all("Preference" not in bidl for bidl in bid_list)


def do():
    plan_cat = get_plan_category()
    available_bids = get_example_bids(plan_cat, ETABLE_PATH)
    available_bids.extend(get_pure_lifestyles(plan_cat))
    bag_wrapper = bag_handler.WindowChains()
    bag = bag_wrapper.bag
    new_etab_name = "LIFE_generated_" + str(time.time()) + ".etab"
    new_etab_path = os.path.join(ETABLE_PATH, new_etab_name)
    with open(new_etab_path, "w") as f:
        f.write(get_file_header())
        for roster_bag in bag.iterators.roster_set():
            crew_id = roster_bag.crew.id()
            has_cc_lh_qual = roster_bag.crew.has_acqln_in_pp("AL")
            if STRICTLY_LH_KEY in plan_cat :
                filtered_bidset = filter(lambda x: has_lh_restricted_bids(x) or
                                         has_no_lifestyle_bids(x), available_bids)
            elif has_cc_lh_qual:
                filtered_bidset = available_bids
            else:
                filtered_bidset = filter(lambda x: not has_lh_restricted_bids(x), available_bids)
            bid_lines = random.choice(filtered_bidset)
            for line in bid_lines:
                bline = insert_crew_id(crew_id, line)
                f.write(bline + "\n")
    rave.param('bid.table_para').setvalue(new_etab_name)


def get_bid_header(crew_id="00000"):
    """
    "00001",0,0,0,"NrOfBids",1,0,0:00,0:00,01JAN1986,01JAN1986,"",false,
    """
    return "".join(["\"" + crew_id + "\",", "0,", "0,", "0,", "\"NrOfBids\",", "1,", "0,",
                    "0:00,", "0:00,", "01JAN1986,", "01JAN1986,", "\"\",", "false,"])


def get_preference_line(preference, crew_id="00000",):
    """
    "00001", 1, 0, 0, "Preference", 0, 0, 0:00, 0:00, 01JAN1986, 01JAN1986,
    "west_destinations_pref", false,
    """
    return "".join(["\"" + crew_id + "\",", "1,", "0,", "0,", "\"Preference\",",
                    "0,", "0,", "0:00,", "0:00,", "01JAN1986,", "01JAN1986,",
                    "\"" + preference + "\",", "false,"])


def get_file_header():
    return """13
Sempno,
Iseqno,
Isubseqno,
Ipoints,
Sbidtype,
Iint1,
Iint2,
Rrel1,
Rrel2,
Aabs1,
Aabs2,
Sstr1,
Bbool1,

"""


if __name__ == '__main__':
    do()
