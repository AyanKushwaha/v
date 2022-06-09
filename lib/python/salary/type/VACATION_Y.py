

"""
Remaining Vacation from following year.

43.5.2 Vacation days/year account (SE)
    (2nd of June every year)

Flight Deck and Cabin Crew.
"""


from VACATION_A import RemainingVacYearRun


class SE(RemainingVacYearRun):
    def __init__(self, record):
        articles = ['VA_REMAINING_YR']
        RemainingVacYearRun.__init__(self, record, articles)

    def __str__(self):
        return 'Swedish Vacation Run (FD+CC, Remaining from following vacation year)'


class S3(RemainingVacYearRun):
    def __init__(self, record):
        articles = ['VA_REMAINING_YR']
        RemainingVacYearRun.__init__(self, record, articles)

    def __str__(self):
        return 'Swedish Vacation Run (FD+CC, Remaining from following vacation year)'


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
