

"""
Remaining Vacation from following year.

43.5.2 Vacation days/year account (NO)
    (2nd of June every year)

Cabin Crew only.
"""

from VACATION_A import RemainingVacYearRunCC

class NO(RemainingVacYearRunCC):
    def __init__(self, record):
        articles = ['VA_REMAINING_YR']
        RemainingVacYearRunCC.__init__(self, record, articles)

    def __str__(self):
        return 'Norwegian Vacation Run (CC, Remaining from following vacation year)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
