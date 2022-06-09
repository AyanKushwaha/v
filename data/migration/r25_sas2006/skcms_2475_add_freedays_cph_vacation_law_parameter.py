import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1.0'

def val_date(date_str):
    return int(AbsTime(date_str))/24/60

valid_from = val_date("01SEP2020")
valid_to = val_date("31Dec2035")

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []
    ops.append(fixrunner.createOp('agreement_validity', 'N', {'id': 'freedays_fd_cph_vacation_law',
                                                              'validfrom': valid_from,
                                                              'validto': valid_to,
                                                              'si': 'Added in SKCMS-2475'}))
    return ops

fixit.program = 'skcms_2475_add_freedays_cph_vacation_law_parameter (%s)' % __version__

if __name__ == '__main__':
    fixit()
