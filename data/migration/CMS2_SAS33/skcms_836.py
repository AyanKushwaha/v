import adhoc.fixrunner as fixrunner
from AbsDate import AbsDate

__version__ = '2016_01_12_l'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    validfrom = int(AbsDate('01Jan1986'))/24/60
    validto = int(AbsDate('31Dec2035'))/24/60

    ops = []
    ops.append(
        fixrunner.createOp('rave_string_paramset', 'W', {
            'ravevar': 'weekend_free_activity_codes_fc_sh',
            'val': 'FW',
            'validfrom': validfrom,
            'validto': validto,
        }),
    )

    return ops




fixit.program = 'skcms_836.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
