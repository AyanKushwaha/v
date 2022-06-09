import re
from AbsTime import AbsTime
import csv
from datetime import date, datetime, timedelta
import logging
import modelserver
import time
import os
import logging
from crewlists.replybody import Reply, ReplyError
from utils.rave import RaveIterator
from utils.selctx import SelectionFilter, FlightFilter, GroundDutyFilter, BasicContext
from utils.divtools import fd_parser, is_base_activity
from utils.paxfigures import CIOStatus

import crewlists.elements as elements
import crewlists.status as status
import utils.exception

from xml.etree import ElementTree

logging.basicConfig()
log = logging.getLogger('CrewList_SN')


tablemanager = modelserver.TableManager.instance()

CARMDATA = os.getenv("CARMDATA")
REPORT_PATH = "/opt/Carmen/CARMTMP/ftp/out/Safetynet/"
XML_PATH = CARMDATA + "/REPORTS/SAFETY_NET/XML_RESPONSE/"

FLIGHT_HEADERS = ['Departure Date', 'Flight', 'Number', 'Registration', 'Type',
                  'Departure', 'Arrival', 'PAX', 'INF', 'Crew', 'STD', 'ETD', 'ATD', 'STA', 'ETA', 'ATA']
FD_HEADERS = ['LHS Name', 'LHS ID No.', 'LHS Home Base', 'Operating Position', 'LHS Qualification Rank', 'LHS Duty Day of Block', 'LHS Sector Number of Event', 'LHS Number of sectors operated in duty day',
              'RHS Name', 'RHS ID No.', 'RHS Home Base', 'RHS Operating Position', 'RHS Qualification Rank', 'RHS Duty Day of Block', 'RHS Sector Number of Event', 'RHS Number of sectors operated in duty day',
              'OBS1 Name', 'OBS1 ID No.', 'OBS1 Home Base', 'OBS1 Operating Position', 'OBS1 Qualification Rank', 'OBS1 Duty Day of Block', 'OBS1 Sector Number of Event', 'OBS1 Number of sectors operated in duty day',
              'OBS2 Name', 'OBS2 ID No.', 'OBS2 Home Base', 'OBS2 Operating Position', 'OBS2 Qualification Rank', 'OBS2 Duty Day of Block', 'OBS2 Sector Number of Event', 'OBS2 Number of sectors operated in duty day',
              'OBS3 Name', 'OBS3 ID No.', 'OBS3 Home Base', 'OBS3 Operating Position', 'OBS3 Qualification Rank', 'OBS3 Duty Day of Block', 'OBS3 Sector Number of Event', 'OBS3 Number of sectors operated in duty day',
              'OBS4 Name', 'OBS4 ID No.', 'OBS4 Home Base', 'OBS4 Operating Position', 'OBS4 Qualification Rank', 'OBS4 Duty Day of Block', 'OBS4 Sector Number of Event', 'OBS4 Number of sectors operated in duty day',
              'OBS5 Name', 'OBS5 ID No.', 'OBS5 Home Base', 'OBS5 Operating Position', 'OBS5 Qualification Rank', 'OBS5 Duty Day of Block', 'OBS5 Sector Number of Event', 'OBS5 Number of sectors operated in duty day',
              'OBS6 Name', 'OBS6 ID No.', 'OBS6 Home Base', 'OBS6 Operating Position', 'OBS6 Qualification Rank', 'OBS6 Duty Day of Block', 'OBS6 Sector Number of Event', 'OBS6 Number of sectors operated in duty day',
              'OBS7 Name', 'OBS7 ID No.', 'OBS7 Home Base', 'OBS7 Operating Position', 'OBS7 Qualification Rank', 'OBS7 Duty Day of Block', 'OBS7 Sector Number of Event', 'OBS7 Number of sectors operated in duty day',
              'OBS8 Name', 'OBS8 ID No.', 'OBS8 Home Base', 'OBS8 Operating Position', 'OBS8 Qualification Rank', 'OBS8 Duty Day of Block', 'OBS8 Sector Number of Event', 'OBS8 Number of sectors operated in duty day',
              'OBS9 Name', 'OBS9 ID No.', 'OBS9 Home Base', 'OBS9 Operating Position', 'OBS9 Qualification Rank', 'OBS9 Duty Day of Block', 'OBS9 Sector Number of Event', 'OBS9 Number of sectors operated in duty day',
              'OBS10 Name', 'OBS10 ID No.', 'OBS10 Home Base', 'OBS10 Operating Position', 'OBS10 Qualification Rank', 'OBS10 Duty Day of Block', 'OBS10 Sector Number of Event', 'OBS10 Number of sectors operated in duty day']

CC_HEADERS = ['CM Name', 'CM Crew No.', 'CM Base', 'CM Operating Position', 'CM Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank',
              'CC Name', 'CC Crew No.', 'CC Base', 'CC Operating Position', 'CC Qualification Rank']

# functions ==============================================================

def run():
    log.setLevel(logging.DEBUG)
    log.debug("Starting the Safetynet crewlist fetch....")
    start_time = time.time()

    today = date.today().strftime("%d%b%Y")
    start_date = (datetime.strptime(today, '%d%b%Y') - timedelta(days=7)).strftime("%d%b%Y")
    end_date = (datetime.strptime(today, '%d%b%Y') + timedelta(days=7)).strftime("%d%b%Y")
    log.debug('Fetching flights for the period {0} to {1}'.format(start_date, end_date))    
    fetchFlightLegs(start_date, end_date)

    end_time = time.time()
    log.debug("End of the execution at %s and took: %0.2f seconds.\n\n" %
             (time.ctime(end_time), end_time - start_time))

def fetchFlightLegs(start_date, end_date):
    flights = []
    fl_table = tablemanager.table('flight_leg')
    svs_filter = '(|(actype=E94)(aco=SVS))'

    flightLegs = fl_table.search('(&(udor>={st})(udor<={end})(|(&{svs_filter})))'.format(
        st=start_date,
        end=end_date,
        svs_filter=svs_filter
    ))

    for flight in flightLegs:
        flights.append(flight)

    if(len(flights) > 0):
        log.debug('Fetched total nr of {0} flights from flight_leg table'.format(len(flights)))
        report_file = generateReportFile()
        for flight in flights:
            parseFlightRequest(flight, report_file)
    else:
        log.debug('Fetched {0} flights from flight_leg table, unable to process'.format(len(flights)))

def generateReportFile():
    if not os.path.exists(REPORT_PATH):
        os.makedirs(REPORT_PATH)

    cl_report_name = report_name()
    cl_report = create_report_file(cl_report_name)
    log.debug('Created the report file: {f}'.format(f=cl_report))
    return cl_report

def report_name():
    report_name = 'crewlist_link_safetynet.csv'
    return report_name

def create_report_file(report_name):
    headers = []
    for fh in FLIGHT_HEADERS:
        headers.append(fh)

    for fdh in FD_HEADERS:
        headers.append(fdh)

    for cc in CC_HEADERS:
        headers.append(cc)

    report_name = REPORT_PATH + report_name
    with open(report_name, 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(headers)
    return report_name

def parseFlightRequest(flight, report_file):
    if(flight.fd[1] == 'V'):
        flt = (flight.fd[0:3]+flight.fd[5:]).upper()
    else:
        flt = (flight.fd[0:2]+flight.fd[5:]).upper()
    
    flt_dt = datetime.strptime(str(flight.udor), '%d%b%Y %H:%M').strftime('%Y%m%d')
    log.debug('parseFlightRequest: Request params: flightId= {0}, originDate= {1}, depStation= {2}, arrStation= {3}, std= {4}, sta= {5}, acType= {6}, aco= {7}'.format(
            flt, flt_dt, flight.adep.id, flight.ades.id, flight.sobt, flight.sibt, flight.actype.id, flight.aco))

    requestName = 'CrewList'
    activityId = flt
    date = flt_dt
    requestDateAsOrigin = 'Y'
    requestDateInLocal = 'N'
    depStation = flight.adep.id
    arrStation = flight.ades.id
    std = ''
    mainRank = ''
    getPublishedRoster = 'Y'
    getTimesAsLocal = 'N'
    getLastFlownDate = 'Y'
    getNextFlightDuty = 'Y'
    getPrevNextDuty = 'Y'
    getPrevNextAct = 'Y'
    getCrewFlightDocuments = 'Y'
    getPackedRoster = 'N'
    getPackedRosterFromDate = ''
    getPackedRosterToDate = ''
    rsLookupError = None

    crewListReply = report(requestName, activityId, date, requestDateAsOrigin, requestDateInLocal,
                           depStation, arrStation, std, mainRank, getPublishedRoster, getTimesAsLocal,
                           getLastFlownDate, getNextFlightDuty, getPrevNextDuty, getPrevNextAct,
                           getCrewFlightDocuments, getPackedRoster, getPackedRosterFromDate,
                           getPackedRosterToDate, rsLookupError)
    #log.debug('crewListReply: {0}'.format(crewListReply))
    parseCrewListResponse(activityId, date, crewListReply, report_file)

def parseCrewListResponse(activityId, date, crewListReply, report_file):
    #log.debug('parseCrewListResponse: {0}'.format(crewListReply[23:]))
    if(str(crewListReply[22]) == '0'):
        if not os.path.exists(XML_PATH):
            os.makedirs(XML_PATH)
        report_name = XML_PATH + \
            '{f}_{d}.xml'.format(f=activityId, d=str(date)[:9])
        # saving the xml response in file
        with open(report_name, 'wb') as f:
            f.write(str(crewListReply[24:]))

        # PARSE XML
        root = ElementTree.fromstring(str(crewListReply[24:]))
        log.debug('parseCrewListResponse: Received valid response: statusCode= {0}, statusText= {1}'
                    .format(root.find("statusCode").text, root.find("statusText").text))

        # FOR FLIGHT DATA
        totalCrew = 0
        crewListMembers = root.findall("./crewListReply/crewListActivity/crewList/crewListMember")
        if(len(crewListMembers) > 0):
            totalCrew = len(crewListMembers)

        flightDetails = []
        flightLegs = root.findall("./crewListReply/crewListActivity/crewFlightActivity")
        for flightLeg in flightLegs:
            flightId = flightLeg.find("flightLeg")[0].text
            originDate = flightLeg.find("flightLeg")[1].text
            depStation = flightLeg.find("flightLeg")[4].text
            arrStation = flightLeg.find("flightLeg")[5].text
            std = flightLeg.find("flightLeg")[6].text
            sta = flightLeg.find("flightLeg")[7].text
            acReg = flightLeg.find("flightLeg")[8][0].text
            acType = flightLeg.find("flightLeg")[8][1][0].text
            etd = flightLeg.find("flightLeg")[9][0].text
            eta = flightLeg.find("flightLeg")[9][1].text
            atd = flightLeg.find("flightLeg")[9][2].text
            ata = flightLeg.find("flightLeg")[9][3].text
            # log.debug('parsedFlightData: flightId= {0}, originDate= {1}, depStation= {2}, arrStation= {3}, std= {4}, sta= {5}, acReg= {6}, acType= {7}, etd= {8}, eta= {9}, atd= {10}, ata= {11}'.format(
            #     flightId, originDate, depStation, arrStation, std, sta, acReg, acType, etd, eta, atd, ata))

            # Additional Formatting for Safetynet
            departure_date = (datetime.strptime(originDate, '%Y-%m-%dZ')).strftime("%d/%m/%Y")            
            flight = flightId[0:2]
            number = flightId[3:]
            pax = ''
            inf = ''
            std_sn = datetime.strptime(std, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            sta_sn = datetime.strptime(sta, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            etd_sn = datetime.strptime(etd, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            eta_sn = datetime.strptime(eta, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            atd_sn = datetime.strptime(atd, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            ata_sn = datetime.strptime(ata, '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M")
            log.debug('parsedFlightData: Formatted flightDetails: departure_date= {0}, flight= {1}, number= {2}, acReg= {3}, acType= {4}, depStation= {5}, arrStation= {6}, pax= {7}, inf= {8}, totalCrew= {9}, std_sn= {10}, etd_sn= {11},atd_sn= {12}, sta_sn= {13},eta_sn= {14}, ata_sn= {15}'.format(
                 departure_date, flight, number, acReg, acType, depStation, arrStation, pax, inf, totalCrew, std_sn, etd_sn, atd_sn, sta_sn, eta_sn, ata_sn))

            flightDetails = [departure_date, flight, number, acReg, acType, depStation, 
                             arrStation, pax, inf, totalCrew, std_sn, etd_sn, atd_sn, sta_sn, eta_sn, ata_sn]

        # FOR FLIGHT DATA
        fd_count = 0
        cc_count = 0
        
        fd_rec_set=[]
        cc_rec_set=[]
        
        for crew in root.findall("./crewListReply/crewListActivity/crewList/crewListMember"):
            crewId = crew.find("crew")[0].text
            name = crew.find("crew")[2].text.encode('iso-8859-1')
            base = crew.find("crew")[8][1].text
            mainRank = crew.find("crew")[5].text
            if mainRank == "F":
                fd_count += 1
            else:
                cc_count += 1
            titleRank = crew.find("crew")[6].text

            
            pos = fetchCrewPosition(originDate, flightId, depStation, crewId)
            if(len(pos) > 0):
                oprPos = pos
            else:
                oprPos = mainRank

            if mainRank == "F":
                fd_rec = [name, crewId, base, oprPos, titleRank, '', '', '']
                fd_rec_set.append(fd_rec)
            else:
                cc_rec = [name, crewId, base, oprPos, titleRank]
                cc_rec_set.append(cc_rec)
            
            log.debug('parsedCrewData: crewId= {0}, name= {1}, base= {2}, mainRank= {3}, titleRank={4}'
                    .format(crewId, name, base, mainRank, titleRank))
        log.debug('parsedCrewData: fd_count= {0}, cc_count= {1}, totalCrew={2}'.format(fd_count, cc_count, totalCrew))

        crewDetails = formatCrewDetails(fd_rec_set, cc_rec_set, fd_count, cc_count)        
        generateRow(flightDetails, crewDetails, report_file)
    else:
        #log.debug('parseCrewListResponse: Error in XML response: {0}'.format(str(crewListReply[26:])))
        # PARSE XML
        root = ElementTree.fromstring(str(crewListReply[26:]))
        statusCode = root.find("statusCode").text
        statusText = root.find("statusText").text
        log.debug('parseCrewListResponse: Error in XML response: statusCode= {0}, statusText= {1}'.format(statusCode, statusText))

def formatCrewDetails(fd_rec_set, cc_rec_set, fd_count, cc_count):
    nopFdDetail = ['', '', '', '', '','','','']
    nopCcDetail = ['', '', '', '', '']
    crewDetailsList = []

    nopFD = (len(FD_HEADERS)/8) - fd_count #FD has 8 headers
    nopCC = (len(CC_HEADERS)/5) - cc_count #CC has 5 headers
    log.debug('formatCrewDetails: Adding {0} FD rows and {1} CC rows'.format(nopFD, nopCC))
    for n in range(nopFD):
        fd_rec_set.append(nopFdDetail)

    for n in range(nopCC):
        cc_rec_set.append(nopCcDetail)

    #log.debug('formatCrewDetails: len(fd_rec_set)= {0} and len(cc_rec_set)= {1}'.format(len(fd_rec_set), len(cc_rec_set)))
    for fd in fd_rec_set:
        crewDetailsList.append(fd)

    for cc in cc_rec_set:
        crewDetailsList.append(cc)

    return crewDetailsList

def fetchCrewPosition(originDate, flightId, depStation, crewId):
    flight_date = datetime.strptime(originDate, '%Y-%m-%dZ').strftime("%Y%m%d")
    flight = flightId[0:3]+'00'+ flightId[3:]
    #log.debug('fetchCrewPosition: flight_date= {0}, flight= {1}, depStation={2}, crewId={3}'.format(
            #flight_date, flight, depStation, crewId))
    leg = flight_date + '+' + flight + '+' + depStation
    #log.debug('fetchCrewPosition: leg= {0}, crewId= {1}'.format(leg, crewId))

    cfd_table = tablemanager.table('crew_flight_duty')
    crew_pos = ''
    for cp in cfd_table.search('(&(leg={fl})(crew={c}))'.format(fl=leg, c=crewId)):        
        crew_pos = cp.pos.id

    log.debug('fetchCrewPosition: For leg= {0}, crewId= {1}, fetched crew_pos= {2} from table crew_flight_duty'.format(leg, crewId,crew_pos))
    return crew_pos    

def generateRow(flightDetails, crewDetails, report_file):
    row = flightDetails
    for crewDetail in crewDetails:
        row += crewDetail

    write_to_report(row, report_file)
    log.debug('Added the row: {r}'.format(r=row))

def write_to_report(row, report):
    with open(report, 'a+') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(row)

def report(
        requestName='CrewList',
        activityId=None,
        date=None,
        requestDateAsOrigin=None,
        requestDateInLocal=None,
        depStation=None,
        arrStation=None,
        std=None,
        mainRank=None,
        getPublishedRoster=None,
        getTimesAsLocal=None,
        getLastFlownDate=None,
        getNextFlightDuty=None,
        getPrevNextDuty=None,
        getPrevNextAct=None,
        getCrewFlightDocuments=None,
        getPackedRoster=None,
        getPackedRosterFromDate=None,
        getPackedRosterToDate=None,
        rsLookupError=None):
    """
    Returns an XML-formatted string with the report.
    """

    try:
        supportedRequests = ('CrewList')
        ip = InputParameters()

        # requestName
        if not requestName in supportedRequests:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED, "requestName '%s' not supported. This report supports '%s' requests." % (
                requestName, ', '.join(supportedRequests)))
        ip.requestName = requestName

        if rsLookupError:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED,
                             'Request date outside CMS historic period (%s).' % date)

        # activityId
        if activityId is None:
            raise ReplyError(
                requestName, status.INPUT_PARSER_FAILED, 'No activityId given.')
        ip.activityId = activityId.upper()

        # date
        if date is None:
            raise ReplyError(
                requestName, status.INPUT_PARSER_FAILED, 'No date given.')
        ip.dateRaw = date
        try:
            ip.date = AbsTime(date)
        except:
            raise ReplyError(requestName, status.INPUT_PARSER_FAILED,
                             'date (%s) not usable.' % date)

        # requestDateAsOrigin
        ip.requestDateAsOrigin = check_yn(
            requestDateAsOrigin, requestName, 'requestDateAsOrigin')

        # requestDateInLocal
        ip.requestDateInLocal = check_yn(
            requestDateInLocal, requestName, 'requestDateInLocal')

        # depStation
        ip.depStation = None
        if not depStation in ('', 3 * ' ', None):
            ip.depStation = depStation

        # arrStation
        ip.arrStation = None
        if not arrStation in ('', 3 * ' ', None):
            ip.arrStation = arrStation

        # std
        if std is None or str(std) == '' or str(std) == '00:00':
            ip.std = None
        else:
            try:
                ip.std = RelTime(std)
            except:
                raise ReplyError(
                    requestName, status.INPUT_PARSER_FAILED, 'std (%s) not usable.' % std)

        ip.mainRank = mainRank

        ip.getPublishedRoster = check_yn(
            getPublishedRoster, requestName, 'getPublishedRoster')
        ip.getTimesAsLocal = check_yn(
            getTimesAsLocal, requestName, 'getTimesAsLocal')
        ip.getLastFlownDate = check_yn(
            getLastFlownDate, requestName, 'getLastFlownDate')
        ip.getNextFlightDuty = check_yn(
            getNextFlightDuty, requestName, 'getNextFlightDuty')
        ip.getPrevNextDuty = check_yn(
            getPrevNextDuty, requestName, 'getPrevNextDuty')
        ip.getPrevNextAct = check_yn(
            getPrevNextAct, requestName, 'getPrevNextAct')
        ip.getCrewFlightDocuments = check_yn(
            getCrewFlightDocuments, requestName, 'getCrewFlightDocuments')
        ip.getPackedRoster = check_yn(
            getPackedRoster, requestName, 'getPackedRoster')

        # getPackedRosterFromDate, getPackedRosterToDate
        if ip.getPackedRoster:
            try:
                ip.getPackedRosterFromDate = AbsTime(getPackedRosterFromDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED,
                                 'getPackedRosterFromDate (%s) not usable.' % getPackedRosterFromDate)
            try:
                ip.getPackedRosterToDate = AbsTime(getPackedRosterToDate)
            except:
                raise ReplyError(requestName, status.INPUT_PARSER_FAILED,
                                 'getPackedRosterToDate (%s) not usable.' % getPackedRosterToDate)
        else:
            ip.getPackedRosterFromDate = 'fundamental.%pp_start%'
            ip.getPackedRosterToDate = 'fundamental.%pp_end%'

        # print('=====================')
        # log.debug('report: ip.requestName= {0}'.format(ip.requestName))
        # log.debug('report: ip.activityId= {0}'.format(ip.activityId))
        # log.debug('report: ip.dateRaw= {0}'.format(ip.dateRaw))
        # log.debug('report: ip.requestDateAsOrigin= {0}'.format(ip.requestDateAsOrigin))
        # log.debug('report: ip.requestDateInLocal= {0}'.format(ip.requestDateInLocal))
        # log.debug('report: ip.depStation= {0}'.format(ip.depStation))
        # log.debug('report: ip.arrStation= {0}'.format(ip.arrStation))
        # log.debug('report: ip.std= {0}'.format(ip.std))
        # log.debug('report: ip.mainRank= {0}'.format(ip.mainRank))
        # log.debug('report: ip.getPublishedRoster= {0}'.format(ip.getPublishedRoster))
        # log.debug('report: ip.getTimesAsLocal= {0}'.format(ip.getTimesAsLocal))
        # log.debug('report: ip.getLastFlownDate= {0}'.format(ip.getLastFlownDate))
        # log.debug('report: ip.getNextFlightDuty= {0}'.format(ip.getNextFlightDuty))
        # log.debug('report: ip.getPrevNextDuty= {0}'.format(ip.getPrevNextDuty))
        # log.debug('report: ip.getPrevNextAct= {0}'.format(ip.getPrevNextAct))
        # log.debug('report: ip.getCrewFlightDocuments= {0}'.format(ip.getCrewFlightDocuments))
        # log.debug('report: ip.getPackedRoster= {0}'.format(ip.getPackedRoster))
        # log.debug('report: ip.getPackedRosterFromDate= {0}'.format(ip.getPackedRosterFromDate))
        # log.debug('report: ip.getPackedRosterToDate= {0}'.format(ip.getPackedRosterToDate))
        # print('=====================')
        return elements.report(Activity(ip))

    except ReplyError, ere:
        # flight not found, etc.
        return str(ere)

    except:
        # programming errors, missing rave definitions.
        return str(Reply(requestName, status.UNEXPECTED_ERROR, utils.exception.getCause()))


def check_yn(x, r, p):
    if not x in ('Y', 'N'):
        raise ReplyError(r, status.INPUT_PARSER_FAILED,
                         '%s must be one of ("Y", "N").' % (p,))
    return x == "Y"


if __name__ == '__main__':
    """ Main function to capture report start and end time and run the main function run()
    """
    run()

# Classes ==============================================================


class InputParameters:
    """ Keeps the input parameters used for the report. """
    pass


class Activity:
    """
    An object that holds the input data together with the rave values.
    That way the XML-formatting routines further down will have everything
    available.

    Has two fields:
        'inparams' - InputParameters object
        'iterator' - RaveIterator object
    """

    def __init__(self, inparams):
        self.inparams = inparams
        self.cioinfo = CIOStatus()

        # Filter for flights
        self.isFlight = True
        if is_base_activity(inparams.activityId):
            self.isFlight = False
            flightTaskSetIterator = RaveIterator(RaveIterator.iter('iterators.flight_task_set',
                                                                   where='(default(training.%%leg_code_redefined%%,"") = "%s" or leg.%%code%% = "%s") and leg.%%start_date_utc%% = %s ' % (inparams.activityId, inparams.activityId, inparams.date)), {'code': 'leg.%code%', })
            bc = BasicContext()
            activities = flightTaskSetIterator.eval(bc.getGenericContext())

            # If not activities for that day is found, return FLIGHT_NOT_FOUND
            if len(activities) == 0:
                raise ReplyError(inparams.requestName,
                                 status.FLIGHT_NOT_FOUND, inparams=inparams)

            inparams.activityId = activities[0].code
            ff = GroundDutyFilter(inparams.activityId, inparams.date,
                                  requestDateAsOrigin=inparams.requestDateAsOrigin, requestDateInLocal=inparams.requestDateInLocal)
        else:
            ff = FlightFilter.fromComponents(inparams.activityId, inparams.dateRaw, None,
                                             inparams.requestDateAsOrigin, inparams.requestDateInLocal)

        flightSetIterator = RaveIterator(RaveIterator.iter(
            'iterators.flight_set', where=ff.asTuple()))

        # Filter for legs
        leg_set = 'iterators.flight_std_leg_set'
        ufilter = SelectionFilter(ff)
        if inparams.depStation is not None:
            ufilter.add('report_crewlists.%leg_adep%',
                        '=', '"%s"' % inparams.depStation)
            if not self.isFlight and not inparams.std is None:
                if inparams.requestDateInLocal:
                    ufilter.add('report_crewlists.%std_time_lt%',
                                '=', '%s' % inparams.std)
                else:
                    ufilter.add('report_crewlists.%std_time_utc%',
                                '=', '%s' % inparams.std)
        else:
            if not self.isFlight:
                leg_set = 'iterators.unique_leg_set'

        if inparams.arrStation is not None:
            ufilter.add('report_crewlists.%leg_ades%',
                        '=', '"%s"' % inparams.arrStation)

        uniqueLegSetIterator = RaveIterator(
            RaveIterator.iter(
                leg_set, sort_by='report_crewlists.%leg_start_utc%', where=ufilter.asTuple()),
            elements.FlightInfo()
        )

        # Criteria for selecting crew
        cfilter = SelectionFilter(ff)
        cfilter.add('fundamental.%is_roster%', '', '')

        # Note: this calculation could be faulty as we don't have control over LDOR.
        if not self.isFlight and not inparams.std is None:
            if inparams.requestDateInLocal:
                cfilter.add('report_crewlists.%std_time_lt%',
                            '=', '%s' % inparams.std)
            else:
                cfilter.add('report_crewlists.%std_time_utc%',
                            '=', '%s' % inparams.std)
        if not inparams.depStation is None:
            cfilter.add('report_crewlists.%leg_adep%',
                        '=', '"%s"' % inparams.depStation)
        if not inparams.arrStation is None:
            cfilter.add('report_crewlists.%leg_ades%',
                        '=', '"%s"' % inparams.arrStation)

        if inparams.mainRank == 'F':
            cfilter.append(
                'report_crewlists.%crew_main_rank%(report_crewlists.%leg_start_lt%) = "F"')
        elif inparams.mainRank == 'C':
            cfilter.append(
                'report_crewlists.%crew_main_rank%(report_crewlists.%leg_start_lt%) = "C"')

        leg_set = RaveIterator.iter(
            'iterators.leg_set',
            where=cfilter.asTuple(),
            sort_by='report_crewlists.%sort_key%'
        )

        if inparams.getPackedRoster:
            legSetIterator = RaveIterator(leg_set, elements.CrewInfoForLegWithRoster(
                inparams.date, inparams.getPackedRosterFromDate, inparams.getPackedRosterToDate))
        else:
            legSetIterator = RaveIterator(
                leg_set, elements.CrewInfoForLeg(inparams.date))

        # Document info iteration
        docInfoIterator = RaveIterator(RaveIterator.times(
            'report_crewlists.%document_count%'), elements.DocumentInfo())

        # Connect the iterators
        flightSetIterator.link(uniqueLegSetIterator)
        uniqueLegSetIterator.link(crew=legSetIterator)
        legSetIterator.link(doc=docInfoIterator)

        try:
            # Join all iterator results
            self.iterator = []

            res = flightSetIterator.eval(ff.context())
            for e in res:
                print "Leg, first attempt, count", len(e.chain()), e
                self.iterator.extend(e.chain())
            if len(res) == 0:
                for e in flightSetIterator.eval(ff.context(None, True)):
                    print "Leg, second attempt, count", len(e.chain()), e
                    self.iterator.extend(e.chain())
        except:
            # Not sure this code is ever executed.
            try:
                # Third (?) attempt: Flip udor over day shift
                self.iterator = flightSetIterator.eval(
                    ff.context(None, True))[0].chain()
            except:
                raise ReplyError(inparams.requestName,
                                 status.FLIGHT_NOT_FOUND, inparams=inparams)
