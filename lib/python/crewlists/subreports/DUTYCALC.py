'''
This is report Duty calculation (CR426)
'''

# imports ================================================================{{{1
import carmensystems.rave.api as rave

import crewlists.html as HTML               
import crewlists.status as status
import utils.exception
import utils.extiter as extiter

from crewlists.replybody import Reply, ReplyError, getReportReply
from AbsTime import AbsTime
from RelTime import RelTime
from AbsDate import AbsDate
from utils.xmlutil import XMLElement
from utils.rave import RaveIterator, Entry
from utils.selctx import SingleCrewFilter
from utils.divtools import default as D

from report_sources.hidden import DutyPointsReport as DutyReport


# constants =============================================================={{{1
report_name = 'DUTYCALC'
title = "Duty Calculation"

class ActivitiesTable(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'Start',
            'End',
            'Activity',
            'From',
            'STD',
            'STA/ETA/ATA',
            'To',
            'Stop time'
        )
        self['id'] = "activities"
        for duty in rosterInfo:
            legs = [x for x in duty]
            if legs:
                duty_start_date, duty_st = str(duty.start_time).split()
                duty_end_date, duty_et = str(duty.end_time).split()
                if duty_start_date == duty_end_date:
                    duty_end_date = ''
                legs[0].duty_start_date = duty_start_date
                legs[0].duty_st = duty_st
                legs[-1].duty_end_date = duty_end_date
                legs[-1].duty_et = duty_et
            for leg in legs:
                duty_date, duty_st, duty_et = '', '', ''
                try:
                    duty_date = leg.duty_end_date
                    duty_et = leg.duty_et
                except:
                    pass
                try:
                    duty_date = leg.duty_start_date
                    duty_st = leg.duty_st
                except:
                    pass
                deadhead = ""
                if leg.activity_code == 'FLT': 
                    leg_activity = leg.number 
                    if leg.deadhead:
                        deadhead = "(DH)"
                else: 
                    leg_activity = leg.activity_code
                    
                if leg.stop_time is None:
                    leg.stop_time = "-"
                self.append(("%s" % duty_date),
                                    ("%s" % duty_st),
                                    ("%s" % duty_et),
                                    HTML.span_right("%s %s" % (leg_activity, deadhead)), 
                                    ("%s" % leg.start_station), 
                                    ("%s" % str(leg.start_time)[-5:]),
                                    ("%s" % str(leg.end_time)[-5:]),
                                    ("%s" % leg.end_station),
                                    HTML.span_right("%s" % leg.stop_time))

class UnionAgreementsTable(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'Pass',
            'Night',
            '24 hours',
            '7 days',
            'To next duty',
            'Slipping time',
            '24 hours'
        )
        self['id'] = "union"
        head2 = HTML.tr(HTML.td)
        head2.append(XMLElement("th", "Duty Time", colspan="5"))
        head2.append(XMLElement("th", "Time Off", colspan="3"))
        self.thead.insert(0, head2)
        for duty in rosterInfo:
            night = str(duty.pass_time - duty.pass_no_night_upg)
            if duty.is_long_haul:
                slippingTime = duty.time_to_next
            else:
                slippingTime = "00:00"
            
            self.append(("%s" %str(duty.start_time)[:-5]),
                                ("%s" %str(duty.pass_time)),
                                ("%s" %night),
                                ("%s" %str(duty.day_points)),
                                ("%s" %str(duty.seven_day_duty)),
                                ("%s" %duty.time_to_next),
                                ("%s" %slippingTime),
                                ("%s" %duty.rest_in_24))


# allowTable -------------------------------------------------------------{{{2
class SubQTable(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'FDP/(MAX)',
            'DP',
            'rest',
            'rest',
            'C/I',
            'B/O',
            'C/O',
            'red',
            'red',
            'red',
            'add',
            'red',
            'DP 7 days',
            'DP 28 days',
            'CI diff'
        )
        self['id'] = "subpartq"
        head2 = HTML.tr(HTML.td)
        head2.append(XMLElement("th", "", colspan="3"))
        head2.append(XMLElement("th", "Req", colspan="1"))
        head2.append(XMLElement("th", "Act", colspan="1"))
        head2.append(XMLElement("th", "", colspan="3"))
        head2.append(XMLElement("th", "Sector", colspan="1"))
        head2.append(XMLElement("th", "WOCL", colspan="1"))
        head2.append(XMLElement("th", "SBY", colspan="1"))
        head2.append(XMLElement("th", "ROB", colspan="1"))
        head2.append(XMLElement("th", "Break", colspan="1"))
        head2.append(XMLElement("th", "", colspan="2"))
        head2.append(XMLElement("th", "FDP", colspan="1"))
        self.thead.insert(0, head2)
        for duty in rosterInfo:
            if duty.use_dp:
                self.append(("%s" %str(duty.check_in)[:-5]), 
                                ("%s%s/(%s)" %(str(duty.fdp)[-5:],str(duty.extended),str(duty.max_fdp)[-5:])),
                                ("%s" %str(duty.dp)[-5:]),
                                ("%s" %str(duty.min_req_rest)),
                                ("%s" %str(duty.act_rest)),
                                ("%s" %str(duty.check_in)[-5:]),
                                ("%s" %str(duty.block_on)[-5:]),
                                ("%s" %str(duty.check_out)[-5:]),
                                ("%s" %str(duty.sector_reduction)),
                                ("%s" %str(duty.wocl_reduction)),
                                ("%s" %str(duty.sby_reduction)),
                                ("%s" %str(duty.rob_addition)),
                                ("%s" %str(duty.break_reduction)),
                                ("%s" %str(duty.dp_7days).replace("<", "&lt;")),
                                ("%s" %str(duty.dp_28days).replace("<", "&lt;")),
                                ("%s" %str(duty.check_in_diff)[-5:])
                                )

class SubQ2Table(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'BLH in c. year',
            'BLH 28 days fwd'
        )
        self['id'] = "subpartq2"
        head2 = HTML.tr(HTML.td)
        head2.append(XMLElement("th", "", colspan="3"))
        self.thead.insert(0, head2)
        for duty in rosterInfo:
            if duty.use_dp:
                self.append(
                    ("%s" % str(duty.check_in)[:-5]),
                    ("%s" % str(duty.blh_year)[-6:]),
                    ("%s  [<-%5s]" % (str(duty.blh_28days), str(duty.blh_28days_end)))
                )


# allowTable -------------------------------------------------------------{{{2
class OMA16Table(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'FDP/(MAX)',
            'DP',
            'rest',
            'rest',
            'C/I',
            'B/O',
            'C/O',
            'num',
            'red',
            'add',
            'add',
            'CI diff',
            'DP 7 days',
            'DP 14 days',
            'DP 28 days'
        )
        self['id'] = "subpartq"
        head2 = HTML.tr(HTML.td)
        head2.append(XMLElement("th", "", colspan="3"))
        head2.append(XMLElement("th", "Req", colspan="1"))
        head2.append(XMLElement("th", "Act", colspan="1"))
        head2.append(XMLElement("th", "", colspan="3"))
        head2.append(XMLElement("th", "Sectors", colspan="1"))
        head2.append(XMLElement("th", "SBY", colspan="1"))
        head2.append(XMLElement("th", "ROB", colspan="1"))
        head2.append(XMLElement("th", "Break", colspan="1"))
        head2.append(XMLElement("th", "FDP", colspan="1"))
        head2.append(XMLElement("th", "", colspan="3"))
        self.thead.insert(0, head2)
        for duty in rosterInfo:
            if duty.use_dp:
                self.append(("%s" %str(duty.check_in)[:-5]), 
                                ("%s%s/(%s)" %(str(duty.fdp)[-5:],str(duty.extended),str(duty.max_fdp)[-5:])),
                                ("%s" %str(duty.dp)[-5:]),
                                ("%s" %str(duty.min_req_rest)),
                                ("%s" %str(duty.act_rest)),
                                ("%s" %str(duty.check_in)[-5:]),
                                ("%s" %str(duty.block_on)[-5:]),
                                ("%s" %str(duty.check_out)[-5:]),
                                ("%s" %str(duty.sectors_num)),
                                ("%s" %str(duty.sby_reduction)),
                                ("%s" %str(duty.rob_addition)),
                                ("%s" %str(duty.break_addition)),
                                ("%s" %str(duty.check_in_diff)),
                                ("%s" %str(duty.dp_7days).replace("<", "&lt;")),
                                ("%s" %str(duty.dp_14days).replace("<", "&lt;")),
                                ("%s" %str(duty.dp_28days).replace("<", "&lt;"))
                                )

class OMA16Table2(HTML.table):
    def __init__(self, rosterInfo):
        HTML.table.__init__(self,
            'Date',
            'BLH in c. year',
            'BLH in 12 c. months'
            'BLH 28 days fwd'
        )
        self['id'] = "subpartq2"
        head2 = HTML.tr(HTML.td)
        head2.append(XMLElement("th", "", colspan="3"))
        self.thead.insert(0, head2)
        for duty in rosterInfo:
            if duty.use_dp:
                self.append(
                    ("%s" % str(duty.check_in)[:-5]),
                    ("%s" % str(duty.blh_year)[-6:]),
                    ("%s" % str(duty.blh_12months)[-6:]),
                    ("%s  [<-%5s]" % (str(duty.blh_28days), str(duty.blh_28days_end)))
                )



class InputData:
    def __init__(self, parameters):
        try:
            (noParameters, self.extperkey, start, end) = parameters
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Wrong number of arguments.", payload=getReportReply(report_name, parameters))
        try:
            self.firstDate = AbsDate(start)
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "Start date not usable.", payload=getReportReply(report_name, parameters))
        try:
            self.lastDate = AbsDate(end)
        except:
            raise ReplyError('GetReport', status.INPUT_PARSER_FAILED, "End date not usable.", payload=getReportReply(report_name, parameters))
        now = AbsDate(rave.eval('sp_crew', 'fundamental.%now%')[0])
        #if self.firstDate > now:
        #    raise ReplyError('GetReport', status.REQUEST_NOT_SUPPORTED, "%s cannot be used for future dates." % report_name)
        #if self.lastDate > now:
        #    self.lastDate = now
        self.crewid = rave.eval('sp_crew', 'report_crewlists.%%crew_extperkey_to_id%%("%s")' % (self.extperkey))[0]
        if self.crewid is None:
            raise ReplyError('GetReport', status.CREW_NOT_FOUND, payload=getReportReply(report_name, parameters))

    def __str__(self):
        """ for basic tests only """
        L = ["--- !InputData"]
        L.extend(["%s : %s" % (str(x), self.__dict__[x]) for x in self.__dict__])
        return "\n".join(L)


def run(*a):
    """ Here is where the report gets generated. """
    try:
        i = InputData(a)
        oma16_valid = DutyReport.isOMA16valid(str(i.firstDate))
        
        SingleCrewFilter(i.crewid).context() # Set default context to single crew
        
        rosterInfo = DutyReport.collectRosterInfo(i.firstDate, i.lastDate+RelTime(24,0), oma16_valid)
        html = HTML.html(title="%s (%s)" % (title, i.extperkey), report=report_name)
        html.append(XMLElement('h1', title))
        html.append(XMLElement('h2', 'ACTIVITIES'))
        html.append(ActivitiesTable(rosterInfo))
        html.append(XMLElement('h2', 'UNION AGREEMENTS CALCULATION'))
        html.append(UnionAgreementsTable(rosterInfo))
        if oma16_valid:
            html.append(XMLElement('h2', 'OMA16 - DUTY CALCULATIONS'))
            html.append(OMA16Table(rosterInfo))
            html.append(XMLElement('h2', 'OMA16 - DUTY CALCULATIONS CONTINUED'))
            html.append(OMA16Table2(rosterInfo))
        else:
            html.append(XMLElement('h2', 'SUBPART Q - DUTY CALCULATIONS'))
            html.append(SubQTable(rosterInfo))
            html.append(XMLElement('h2', 'SUBPART Q - DUTY CALCULATIONS CONTINUED'))
            html.append(SubQ2Table(rosterInfo))

        return str(Reply('GetReport', payload=getReportReply(report_name, a, html)))

    except ReplyError, e:
        # Anticipated errors
        return str(e)

    except:
        import traceback
        traceback.print_exc
        return str(Reply('GetReport', status.UNEXPECTED_ERROR, utils.exception.getCause(), payload=getReportReply(report_name, a)))

def archive(crew, firstdate, lastdate):
    s = str(firstdate).split()[0]
    y = s[-4:]
    m = s[-7:-4]
    ret = {}
    lc = len(crew)
    for i,(id,extperkey) in enumerate(crew):
        print "DUTYCALC Crew",id,extperkey," (",i,"of",lc,")"
        try:
            ret[extperkey] = run(3, extperkey, str(firstdate), str(lastdate))
        except:
            import traceback, sys
            traceback.print_exc()
            ret[extperkey] = "!!ERROR!!" + sys.exc_info()
    return ret

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
