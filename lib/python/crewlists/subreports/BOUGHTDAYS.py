# imports ================================================================{{{1

import crewlists.status as status
import utils.exception

from tm import TM
from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime
from crewlists.subreports import Util


# constants =============================================================={{{1
REPORT_NAME = 'BOUGHTDAYS'
TITLE = "Bought Days"

# InputData =============================================================={{{1
class InputData:
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey, self.account, year) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED,
                             "Wrong number of arguments.", payload=getReportReply(REPORT_NAME, parameters))
        try:
            # date in format 'YYYYMM'
            self.year = int(year)
            self.firstDate = AbsTime("%04d0101" % (self.year))
            self.lastDate = AbsTime("%04d0101" % (self.year + 1))
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED,
                             "Date not usable.", payload=getReportReply(REPORT_NAME, parameters))


        try:
            #More readable values, SASCMS-5720
            accountNameDict = dict()
            accountNameDict['BOUGHT BL'] = 'BOUGHT_BL'
            accountNameDict['BOUGHT+F3'] = 'BOUGHT_COMP'
            accountNameDict['BOUGHT&gt;6 HRS'] = 'BOUGHT'
            accountNameDict['BOUGHT&lt;=6 HRS'] = 'BOUGHT_8'
            accountNameDict['BOUGHT>6 HRS'] = 'BOUGHT'
            accountNameDict['BOUGHT<=6 HRS'] = 'BOUGHT_8'
            accountNameDict['BOUGHT=F3S'] = 'BOUGHT_COMP_F3S'
            accountNameDict['BOUGHT FORCED'] = 'BOUGHT_FORCED'
            accountNameDict[self.account] = self.account
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED,
                             "Unknown account %s" % (self.account), payload=getReportReply(REPORT_NAME, parameters))

        
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
            return account in ('BOUGHT', 'BOUGHT_BL', 'BOUGHT_COMP', 'BOUGHT_8', 'BOUGHT_COMP_F3S', 'BOUGHT_FORCED')

        html =  Util.run(i, compdays_filter, REPORT_NAME, TITLE)

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
    print run(3, '34220', 'BOUGHT', '2011')


