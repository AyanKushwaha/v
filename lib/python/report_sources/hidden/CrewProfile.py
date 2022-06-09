
# [acosta:08/092@17:09] Created.
# [acosta:08/095@11:41] Last flown has been commented out (see XXX)

"""
Create typeset report with Crew Profile information.

See CR 101.
"""

import carmensystems.publisher.api as prt
import carmusr.crewinfo.crew_profile as crew_profile

from report_sources.include.SASReport import SASReport


# PRT formatting functions ==============================================={{{1

def AColumn(s):
    if s is None:
        return prt.Column()
    else:
        return prt.Column(prt.Text(s))


def HeaderRow(*a, **k):
    k['font'] = prt.Font(size=10, weight=prt.BOLD)
    return prt.Row(*a, **k)


def TableRow(*a, **k):
    return prt.Row(*a, **k)


# CrewProfile ============================================================{{{1

class CrewProfile(SASReport):
    """Simple report with crew profile information."""

    def create(self):
        self.crewid = self.arg('CREWID')
        print "self.crewid", self.crewid, type(self.crewid)

        SASReport.create(self, title='Crew Profile for %s' % self.crewid,
                showPlanData=False, pageWidth=820, orientation=prt.LANDSCAPE)
        p = crew_profile.profile(self.crewid)

        self.add(HeaderRow(
            AColumn("Valid From"),
            AColumn("Title Rank"),
            AColumn("Crew Rank"),
            AColumn("Qualification 1"),
            AColumn("Qualification 2"),
            AColumn("Restriction 1"),
            AColumn("Restriction 2"),
            #AColumn("Last Flown 1"), # XXX
            #AColumn("Last Flown 2"), # XXX
            AColumn("Contract"),
            AColumn("Group type"),
            AColumn("Cycle start"),
            AColumn("Station"),
            AColumn("Base")))

        for x in p:
            if x.cyclestart is not None and x.cyclestart != 0:
                cyclestart = x.cyclestart
            else:
                cyclestart = ''
            self.add(TableRow(
                AColumn(str(x.startdate).split()[0]),
                AColumn(x.titlerank),
                AColumn(x.crewrank),
                AColumn(x.qual_1),
                AColumn(x.qual_2),
                AColumn(x.rest_1),
                AColumn(x.rest_2),
                #AColumn(x.last_flown_1), # XXX
                #AColumn(x.last_flown_2), # XXX
                AColumn(x.contract),
                AColumn(x.grouptype),
                AColumn(cyclestart),
                AColumn(x.station),
                AColumn(x.base)))
            self.page()


# run_report ============================================================={{{1
run_report = crew_profile.run_report


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    run_report()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
