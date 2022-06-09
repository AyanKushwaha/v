
# changelog {{{2
# [acosta:07/130@15:33] First try with Vacations.
# [acosta:07/267@21:31] Non-Rave based solution.
# }}}

"""
Remaining Vacation.

43.5.1.1.2 Vacation days remaining (DK).
"""

from VACATION_A import RemainingVacRun


class DK(RemainingVacRun):
    def __init__(self, record):
        articles = ['VA_REMAINING']
        RemainingVacRun.__init__(self, record, articles)

    def __str__(self):
        return 'Danish Vacation Run (Remaining)'


class NO(DK):
    def __str__(self):
        return 'Norwegian Vacation Run (Remaining)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
