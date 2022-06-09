"""
SKCMS-2751
Release: r27_2112_T
"""
import os
import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime


__version__ = "2021-12-08"


filepath = os.path.expandvars("$CARMUSR")
directory = filepath + "/data/migration/r27_sas2112/"
# directory = filepath+'/data/config/models/'


def val_date(date_str):
    return int(AbsTime(date_str)) / 24 / 60


agr_valid_from = val_date("01Feb2022")
agr_valid_to = val_date("31Dec2035")

valid_from = int(AbsTime("01Jan2022"))
valid_to = int(AbsTime("31Dec2035"))

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
                "id": "web_training_pc_22",
                "validfrom": agr_valid_from,
                "validto": agr_valid_to,
                "si": "New name standard for web training at PC, SKCMS-2751",
            },
        )
    )

    # --------------      Add entries to table activity_set    -------------------------- #
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT11", "grp": "COD", "si": "RWBT New Code Year 1 Spring"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT12", "grp": "COD", "si": "RWBT New Code Year 1 Autumn"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT21", "grp": "COD", "si": "RWBT New Code Year 2 Spring"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT22", "grp": "COD", "si": "RWBT New Code Year 2 Autumn"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT31", "grp": "COD", "si": "RWBT New Code Year 3 Spring"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "WT32", "grp": "COD", "si": "RWBT New Code Year 3 Autumn"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W11A2", "grp": "COD", "si": "RWBT New A2 1/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W11A3", "grp": "COD", "si": "RWBT New A3 1/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W11A5", "grp": "COD", "si": "RWBT New A5 1/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W11B3", "grp": "COD", "si": "RWBT New B737-800 1/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W11LH", "grp": "COD", "si": "RWBT New LH A3+A5 1/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W11M3", "grp": "COD", "si": "RWBT New MFF A2+A3 1/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W11M5", "grp": "COD", "si": "RWBT New MFF A2+A5 1/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W12A2", "grp": "COD", "si": "RWBT New A2 2/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W12A3", "grp": "COD", "si": "RWBT New A3 2/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W12A5", "grp": "COD", "si": "RWBT New A5 2/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W12B3", "grp": "COD", "si": "RWBT New B737-800 2/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W12LH", "grp": "COD", "si": "RWBT New LH A3+A5 2/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W12M3", "grp": "COD", "si": "RWBT New MFF A2+A3 2/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W12M5", "grp": "COD", "si": "RWBT New MFF A2+A5 2/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W21A2", "grp": "COD", "si": "RWBT New A2 3/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W21A3", "grp": "COD", "si": "RWBT New A3 3/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W21A5", "grp": "COD", "si": "RWBT New A5 3/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W21B3", "grp": "COD", "si": "RWBT New B737-800 3/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W21LH", "grp": "COD", "si": "RWBT New LH A3+A5 3/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W21M3", "grp": "COD", "si": "RWBT New MFF A2+A3 3/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W21M5", "grp": "COD", "si": "RWBT New MFF A2+A5 3/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W22A2", "grp": "COD", "si": "RWBT New A2 4/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W22A3", "grp": "COD", "si": "RWBT New A3 4/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W22A5", "grp": "COD", "si": "RWBT New A5 4/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W22B3", "grp": "COD", "si": "RWBT New B737-800 4/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W22LH", "grp": "COD", "si": "RWBT New LH A3+A5 4/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W22M3", "grp": "COD", "si": "RWBT New MFF A2+A3 4/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W22M5", "grp": "COD", "si": "RWBT New MFF A2+A5 4/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W31A2", "grp": "COD", "si": "RWBT New A2 5/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W31A3", "grp": "COD", "si": "RWBT New A3 5/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W31A5", "grp": "COD", "si": "RWBT New A5 5/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W31B3", "grp": "COD", "si": "RWBT New B737-800 5/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W31LH", "grp": "COD", "si": "RWBT New LH A3+A5 5/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W31M3", "grp": "COD", "si": "RWBT New MFF A2+A3 5/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W31M5", "grp": "COD", "si": "RWBT New MFF A2+A5 5/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W32A2", "grp": "COD", "si": "RWBT New A2 6/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W32A3", "grp": "COD", "si": "RWBT New A3 6/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set", "N", {"id": "W32A5", "grp": "COD", "si": "RWBT New A5 6/6"}
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W32B3", "grp": "COD", "si": "RWBT New B737-800 6/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W32LH", "grp": "COD", "si": "RWBT New LH A3+A5 6/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W32M3", "grp": "COD", "si": "RWBT New MFF A2+A3 6/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set",
            "N",
            {"id": "W32M5", "grp": "COD", "si": "RWBT New MFF A2+A5 6/6"},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT11", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT12", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT21", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT22", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT31", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "WT32", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W11M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W12M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W21M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W22M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W31M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32A2", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32A3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32A5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32B3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32LH", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32M3", "validfrom": valid_from, "validto": valid_to},
        )
    )
    ops.append(
        fixrunner.createOp(
            "activity_set_period",
            "N",
            {"id": "W32M5", "validfrom": valid_from, "validto": valid_to},
        )
    )
    return ops


fixit.program = "skcms-2751.py (%s)" % __version__
if __name__ == "__main__":
    fixit()
