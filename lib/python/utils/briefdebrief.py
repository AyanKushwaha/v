

"""
Create in regards to issues in SKPROJ-170/SKS-136.
The code have been separated from extiter.py.
Dependency chain, dig.xhandlers -> cio.acci -> crewlists.elements -> utils.extiter -> utils.rave -> carmensystem.rave.api,
caused the DIG channel to malfunction since it can't handle rave.
New dependency chain dig.xhandlers -> cio.acci -> crewlists.elements -> utils.briefdebrief, cuts the relation between DIG and rave.api
"""

class BriefDebriefException(Exception):
    """Activity does not need briefing/debriefing."""


class BriefDebriefExtender(list):
    """List containing possible briefing, activity, and, possible
    debriefing."""
    def __init__(self, activity):
        list.__init__(self)
        self.add_briefing(activity)
        self.append(activity)
        self.add_debriefing(activity)

    def add_briefing(self, activity):
        try:
            self.append(self.Briefing(activity))
        except BriefDebriefException, bde:
            pass
        except Exception, e:
            print e

    def add_debriefing(self, activity):
        try:
            self.append(self.Debriefing(activity))
        except BriefDebriefException, bde:
            pass
        except Exception, e:
            print e

    class Briefing:
        def __init__(self, activity):
            raise NotImplementedError("Not implemented.")

    class Debriefing:
        def __init__(self, activity):
            raise NotImplementedError("Not implemented.")