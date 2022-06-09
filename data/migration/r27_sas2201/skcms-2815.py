"""
SKCMS-2815
Release: r27_2201_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = "2022-01-10"


filepath = os.path.expandvars("$CARMUSR")
directory = filepath + "/data/migration/r27_sas2201/"
# directory = filepath+'/data/config/models/'


def val_date(date_str):
    return int(AbsTime(date_str)) / 24 / 60


agr_valid_from = val_date("01Mar2022")
agr_valid_to = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = list()
    # --------------   Add entries to table agreement_validity -------------------------- #
    ops.append(
        fixrunner.createOp(
            "agreement_validity",
            "N",
            {
                "id": "min_legs_in_month_mff",
                "validfrom": agr_valid_from,
                "validto": agr_valid_to,
                "si": "MFF continuity rule SKCMS-2815",
            },
        )
    )
    return ops


fixit.program = "skcms-2815.py (%s)" % __version__
if __name__ == "__main__":
    fixit()
