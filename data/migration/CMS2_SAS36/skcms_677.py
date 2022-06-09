import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '2016_04_08_a'


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

    for extsys, extartid in [("NO", "99991"), ("SE", "217"), ("DK", "9499")]:
        ops.append(
            fixrunner.createOp("salary_article", "W", {
                "extsys": extsys,
                "extartid": extartid,
                "validfrom": validfrom,
                "validto": validto,
                "intartid": "SNGL_SLIP_LONGHAUL",
                "note": "Extra salary for a single-slipping longhaul flight"
            }))

    return ops


fixit.program = 'skcms_628.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


