
#####

##
#####
__version__ = "$Revision$"

"""
RosterInfo report in prt-format, to use in crew general
@date: 2jun2008
@author: Per Groenberg
@org Jeppesen Systems AB
"""
from report_sources.include.RosterInfo import _RosterInfo as Report

class RosterInfo(Report):

    def create(self):
        Report.create(self)
