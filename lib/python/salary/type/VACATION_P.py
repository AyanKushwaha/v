
# changelog {{{2
# [acosta:07/130@15:33] First try with Vacations.
# }}}

"""
Performed Vacation.

43.5.1.1 Vacation days performed (DK).
"""

from VACATION_A import PerformedVacRun


class DK(PerformedVacRun):
    def __init__(self, record):
        articles = ['VA_PERFORMED'] #, 'VA1_PERFORMED']
        PerformedVacRun.__init__(self, record, articles)

    def __str__(self):
        return 'Danish Vacation Run (Performed)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
