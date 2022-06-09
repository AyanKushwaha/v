"""
SKCMS-2461: Add and update activity set entries for web trainings as they are split in to two separate activities.
New format contains a trailing 1 or 2 to indicate which period the web training should occur in.
Release: SAS2006
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime

__version__ = '1.2'

valid_from = int(AbsTime("01JAN1986"))
valid_to = int(AbsTime("31DEC2035"))

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    wt_sequence = ["11", "12", "21", "22", "31", "32"]
    for aircraft in ["A", "B"]:
        for idx in range(1, 7):
            # WTA22 and WTB22 manually added in TEST and PROD. Skip these to avoid error.
            if idx == 4:
                continue

            ac_man = "Airbus" if aircraft == "A" else "Boeing"
            wt_id = "WT" + aircraft + wt_sequence[idx - 1]
            ops.append(fixrunner.createOp('activity_set', 'N', {'id': wt_id,
                                                                'grp': 'COD',
                                                                'si': 'RWBT ' + ac_man + ' ' + str(idx) + '/6'}))

            ops.append(fixrunner.createOp('activity_set_period', 'N', {'id': wt_id,
                                                                       'validfrom': valid_from,
                                                                       'validto': valid_to}))
    return ops


fixit.program = 'skcms_2461_update_web_trainings (%s)' % __version__

if __name__ == '__main__':
    fixit()
