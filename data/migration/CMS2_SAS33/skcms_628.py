import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '2015_12_18_d'


# AbsDate returns the same value as AbsTime, i.e. minutes since 1986 - only rounded down to 0:00
# BUT! If setting an AbsDate in DB, that value must be reduced to _days since 1986_, i.e. /60/24!
def minutes2days(m):
    return m/24/60


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    validfrom = int(AbsDate('01Jan2016'))
    validto = int(AbsDate('31Dec2035'))

    ops = []

    for aid in ["F15", "F16"]:
        ops.append(fixrunner.createOp('account_set', 'W', {
            "id": aid,
            "si": "Day off, comp for bought day QA FD",
        }))
        ops.append(
            fixrunner.createOp("activity_set", "W", {  # W = (write) insert or update
                "id": aid,
                "grp": "FRE",
                "si": "Day off, comp for bought day QA FD",
            }))
        ops.append(
            fixrunner.createOp("activity_set_period", "W", {
                "id": aid,
                "validfrom": validfrom,
                "validto": validto,
            }))

    for extartid, intartid in [("9496", "BOUGHT_QA_FC_COMP"), ("9497", "BOUGHT_QA_FP_COMP")]:
        ops.append(
            fixrunner.createOp("salary_article", "W", {
                "extsys": "DK",
                "extartid": extartid,
                "validfrom": validfrom,
                "validto": validto,
                "intartid": intartid,
                "note": "Bought day comp. Cimber FD"
            }))

    return ops


fixit.program = 'skcms_628.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


