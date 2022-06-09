

"""
Remaining Vacation from following year.

43.5.2 Vacation days/year account (DK, NO)
    (2nd of June every year)

Flight Deck only.
"""

from VACATION_A import RemainingVacYearRunFD

class DK(RemainingVacYearRunFD):
    def __init__(self, record):
        articles = ['VA_REMAINING_YR']
        RemainingVacYearRunFD.__init__(self, record, articles)

    def __str__(self):
        return 'Danish Vacation Run (FD, Remaining from following vacation year)'


class NO(DK):
    def __str__(self):
        return 'Norwegian Vacation Run (FD, Remaining from following vacation year)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
