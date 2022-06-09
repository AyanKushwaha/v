'''
Created on May 5, 2010

@author: mattiasn
'''
from Localization import MSGR

import report_sources.include.check_legality as check_legality
import carmstd.select


class Report(check_legality.Report):

    def get_scope(self):
        """
        Should return the scope of the report, .i.e. 'window', 'margin'(, or 'plan')
        """
        return "window"

    def get_type(self):
        """
        Should return the type of the report, i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        return "leg"

    def get_report_view_name(self):
        return MSGR("Rotation")

    def get_identifier(self, bag):  # @UnusedVariable
        # We don't have any identifier for the ac rotations
        # and skipping giving an identifier will cause the
        # report to skip making the name clickable (show
        # in studio)
        return None

    def get_name(self, bag):  # @UnusedVariable
        return None

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
    rg.reload_and_display_report()
