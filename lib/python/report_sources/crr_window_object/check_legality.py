'''
Created on Jun 3, 2010

@author: Andreas Lidholm
'''
from Localization import MSGR

import report_sources.include.check_legality as check_legality
import carmstd.select


class Report(check_legality.Report):

    def get_report_view_name(self):
        return MSGR("Trip")

    def get_identifier(self, bag):
        "Gets the crr_identifier for the trip"
        return bag.keywords.crr_identifier()

    def get_name(self, bag):
        "Gets the trip name for the trip"

        # Have to do it this way since we are working with chain bags
        # and for rostering that means roster. We want to
        # evalulate trip.name on the right level
        for trip_bag in bag.iterators.trip_set():
            return trip_bag.trip.name()

    def get_scope(self):
        """
        Should return the scope of the report, .i.e. 'window', 'margin'(, or 'plan')
        """
        return "window"

    def get_type(self):
        """
        Should return the type of the report, i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        return "trip"

    @staticmethod
    def show_in_studio(*args, **kw):
        "Shows the trip(s) in studio"
        carmstd.select.show_trips(*args, **kw)

    def get_header_text(self):
        """
        Return the name of the report
        """
        return MSGR("Check Legality")


if __name__ == "__main__":
    import carmstd.report_generation as rg
    #reload(check_legality)
    rg.reload_and_display_report()
