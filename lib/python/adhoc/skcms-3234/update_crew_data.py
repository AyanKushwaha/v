"""
SKCMS-3234: Link FD SPG: Script to change data to identify SVS SPG crew
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = "2023-01-31_4"

filepath = os.path.expandvars("$CARMUSR")
dataFile = filepath + "/lib/python/adhoc/skcms-3234/spg_crew_list"


valid_from = int(AbsTime("01Apr2023"))
valid_to = int(AbsTime("31Dec2035"))

crewList = []


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()

    crewList = open(dataFile).read().splitlines()
    for crew in crewList:
        print("Looking for %s crew to modify" % crew)
        for ce_entry in fixrunner.dbsearch(
            dc,
            "crew_employment",
            "crew='%s' and company='%s' and validto>=%i" % (crew, "SVS", valid_to),
        ):
            print("Updating validto in crew_employment for %s", crew)
            ce_entry["validto"] = valid_from
            ops.append(fixrunner.createop("crew_employment", "U", ce_entry))
            ce_entry["validto"] = valid_to
            ce_entry["validfrom"] = valid_from
            ce_entry["company"] = "SK"
            ce_entry["si"] = "K22 changing to SPG"
            ops.append(fixrunner.createop("crew_employment", "N", ce_entry))

        for cc_entry in fixrunner.dbsearch(
            dc,
            "crew_contract",
            "crew='%s' and validto>=%i and (contract='VSVS-001' or contract='VSVS-002' or contract='VSVS-011')"
            % (crew, valid_to),
        ):
            print("Updating validto in crew_contract for %s", crew)
            cc_entry["validto"] = valid_from
            ops.append(fixrunner.createop("crew_contract", "U", cc_entry))
            cc_entry["validto"] = valid_to
            cc_entry["validfrom"] = valid_from
            cc_entry["si"] = "K22 changing to SPG"
            if cc_entry["contract"] == "VSVS-001":
                cc_entry["contract"] = "VSA-001"
            elif cc_entry["contract"] == "VSVS-002":
                cc_entry["contract"] = "VSA-009"
            else:
                cc_entry["contract"] = "VSA-032"
            ops.append(fixrunner.createop("crew_contract", "N", cc_entry))
    return ops


fixit.program = "update_crew_data.py (%s)" % __version__
if __name__ == "__main__":
    fixit()
