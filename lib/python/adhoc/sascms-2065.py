

"""
SASCMS-2065

Add rave_paramset_set key "subq_violation_report_rules"
Add default rules in rave_string_paramset.
"""
import datetime

try:
    import adhoc.fixrunner as fixrunner
except ImportError:
    import sys
    print >>sys.stderr, "Please source (CARMUSR)/etc/carmenv.sh first!"
    sys.exit(1)
__version__ = '1'


def to_dave_date(dt):
    """Return now as DAVE date."""
    EPOCH = datetime.datetime(1986, 1, 1)
    timestamp = dt - EPOCH
    return timestamp.days

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validstart = to_dave_date(datetime.datetime(1986, 1, 1))
    validto = to_dave_date(datetime.datetime(2035, 12, 31))

    return [
        fixrunner.createOp('rave_paramset_set', 'N', {
            'id': 'subq_violation_report_rules',
            'description': 'Expressions to match rule names for inclusion in Sub Q Violation Report',
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'subq_violation_report_rules',
            'val': 'rule*.*subq*',
            'validfrom': validstart,
            'validto': validto,
            'si': 'All rules with subq in the name',
        }),
        fixrunner.createOp('rave_string_paramset', 'N', {
            'ravevar': 'subq_violation_report_rules',
            'val': '!*max_duty_in_fdp*',
            'validfrom': validstart,
            'validto': validto,
            'si': 'Exclude rules *max_duty_in_fdp*',
        }),
    ]


fixit.program = 'sascms-2065.py (%s)' % __version__


if __name__ == '__main__':
    fixit()
