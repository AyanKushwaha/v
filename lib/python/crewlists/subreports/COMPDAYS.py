
# changelog {{{2
# [acosta:07/078@14:06] First version
# [acosta:07/095@12:00] Refactoring...
# }}}

"""
This is report 32.21 Compensation Days.
"""

# imports ================================================================{{{1

import crewlists.status as status
import utils.exception
from crewlists.subreports import Util

from tm import TM
from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime


# constants =============================================================={{{1
REPORT_NAME = 'COMPDAYS'
TITLE = "Compensation Days"

# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey, self.account, year) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.",
                             payload=getReportReply(REPORT_NAME, parameters))
        try:
            # date in format 'YYYYMM'
            self.year = int(year)
            self.firstDate = AbsTime("%04d0101" % (self.year))
            self.lastDate = AbsTime("%04d0101" % (self.year + 1))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Date not usable.",
                             payload=getReportReply(REPORT_NAME, parameters))

        self.crewid = None
        for x in TM.crew_employment.search('(&(extperkey=%s)(validto>%s)(validfrom<%s))' % (self.extperkey,
                                                                                            self.firstDate,
                                                                                            self.lastDate)
                                           ):
            self.crewid = x.crew.id
            break
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND,
                             "Crew with extperkey '%s' not found.." % (self.extperkey),
                             payload=getReportReply(REPORT_NAME, parameters))

        try:
            c = TM.crew[(self.crewid,)]
            self.logname = c.logname
        except:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND,
                             "Crew logname not found for crew with extperkey '%s'." % (self.extperkey),
                             payload=getReportReply(REPORT_NAME, parameters))

    def __str__(self):
        """ for basic tests only """
        L = ["--- !InputData"]
        L.extend(["%s : %s" % (str(x), self.__dict__[x]) for x in self.__dict__])
        return "\n".join(L)

# run ===================================================================={{{1
def run(*a):
    """ Here is where the report gets generated. """
    try:
        i = InputData(a)

        def compdays_filter(account):
            return account in ('F0', 'F15', 'F16', 'F3', 'F31', 'F32', 'F33', 'F35', 'F38','F3S', 'F7S', 'F89', 'F9')

        html = Util.run(i, compdays_filter, REPORT_NAME, TITLE)

        return str(Reply('GetReport', payload=getReportReply(REPORT_NAME, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(),
                         payload=getReportReply(REPORT_NAME, a))
                   )


# main ==================================================================={{{1
# for basic tests
if __name__ == '__main__':
    # Nbr parameters (3), crewId, account/type, year
    print run(3, '37640', 'F3', '2019')