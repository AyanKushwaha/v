"""
This is the entry point to reports of type R2 (GetReport).
Run specified report service, return result to report server.
"""

# imports ================================================================{{{1
import utils.exception
import crewlists.status as status

from crewlists.replybody import Reply, ReplyError, getReportReply


# functions =============================================================={{{1

# report -----------------------------------------------------------------{{{2
def report(rep, *a, **k):
    package = 'crewlists.subreports'
    if rep == 'GetReport':
        try:
            subrep = a[0]
        except:
            return str(Reply(rep, status.INPUT_PARSER_FAILED, "No reportId given.", payload=getReportReply('', a)))

        if k.has_key('rsLookupError') and k['rsLookupError']:
            return str(Reply(subrep, status.INPUT_PARSER_FAILED, "Request date outside CMS historic period.", payload=getReportReply(subrep, a)))

        try:
            c = __import__('%s.%s' % (package, subrep), (), (), [''])
            
        except:
            return str(Reply(rep, status.REPORT_NOT_FOUND, "The report '%s' was not found." % (subrep), payload=getReportReply(subrep, a)))

        try:
            if hasattr(c, "run"):
                return c.run(*a[1:], **k)

        except ReplyError, re:
            return str(re)

        except:
            import traceback
            traceback.print_exc
            return str(Reply(rep, status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(subrep, a)))

    else:
        return str(Reply(rep, status.INPUT_PARSER_FAILED, "Reports of type '%s' not supported by this interface (R2)." % (rep), payload=getReportReply('', a)))


# main ==================================================================={{{1
if __name__ == '__main__':
    """ For basic tests """
#    print report('GetReportList')
    print report('GetReport', 'PILOTLOGCREW', '41333', '200702')
#    print report('GetReport', 'PILOTLOGCRE', '41333', '200702')
    print report('GetReport', 'BOUGHTDAYS', '10112', 'BOUGHT BL', '2013')
    print report('GetReport', 'BOUGHTDAYS', 3, *('16187', 'Bought<=6 hrs', '2013'))
        
# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
