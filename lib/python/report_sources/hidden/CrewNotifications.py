from utils.xmlutil import XMLElement,XMLDocument
from AbsTime import AbsTime
from RelTime import RelTime
from tm import TM
from datetime import datetime
from utils.airport_tz import Airport
import carmensystems.rave.api as rave


def dateTimeInUTC(t):
    """ AbsTime to ISO 8601 (date + time).
    """
    (y, mo, d, h, mi) = t.split()

    return "%04d-%02d-%02dT%02d:%02d:00" % (y, mo, d, h, mi) + "Z"

def dateTimeInHomebaseTimeEnd(utctime, homebase):
    timeMinusOneMinute = utctime -RelTime("00:01")
    return dateTimeInHomebaseTime(timeMinusOneMinute, homebase)

def dateTimeInHomebaseTime(utctime, homebase):
    """ AbsTime to ISO 8601 (date + time).
    """
    airport =Airport(homebase)
    localtime = airport.getLocalTime(utctime)

    (y, mo, d, h, mi) =localtime.split()

    return "%04d-%02d-%02dT%02d:%02d:00" % (y, mo, d, h, mi) + "Z"

def fetch_data(now,creatime_offset,deadline_offset):
    """
        This routine fetches data from the crew_notifications and and crew_employment tables
        In crew_notifications table it fetches rows where created >=now-creatime_offset
        When created output the deadline for crew using Cabin Crew Device shall be less
        then crew_notification.deadline - deadline_offset

        Input:
            now                     : Abstime
            creationtime_offset     : String in hours for example "08:00"
            deadline_offset         : String in hours for example "01:00"
        Output: A list of dictionaries. Each dictionary contains the following keys:
                   {['crewId']
                    ['empno']
                    ['notificationId']
                    ['notificationType']
                    ['notificationSubType']
                    ['validity_start']
                    ['validity_end']
                    ['deadline']
                    ['creationTime']
                    ['notificationText']
                    ['additionalInfo']}
                Data is only created for cabin crew
    """

    def relevant_row(typ,subtype):

    # The only interesting rows are those who concerns a roster change or an inforamtion message
        ret = (typ=="Automatic" and subtype=="Assignment") or (typ=="Manual" and subtype=="!NoAlert") \
              or (typ=="Manual" and subtype=="*Alert")
        return ret

    def fetch_notification_message(idnr):
        # Fetches data from notification_message table. Since there can exist more than one row
        # given an idnr, the messages are sorted by seqno and made to one string
        search_string = "(idnr=%s)"%idnr
        nfs = TM.notification_message.search(search_string)
        message_list=[]
        for notification_message in nfs:
            this_message = []
            this_message.append(notification_message.seq_no)
            this_message.append(notification_message.free_text)
            message_list.append(this_message)
            message_list.sort()
        txt = ""
        for message_part in message_list:
            txt = txt + message_part[1]
        return txt

    notification_search_start = now - RelTime(creatime_offset)
    notification_search_end = now - RelTime(2)  # SKCIS-3: Added 'delay' to ensure CrewInfoServer has received data
    notification_deadline_limit = now + RelTime(30) # Give crew at least 30 minutes to react

    TM(["crew_notification"])

    # Get notification from crew_notification which is created from a special date and for which we
    # have not sent a notification_message yet and is not informed i.e. delivered is null

    search_str = "(&(created<%s)(deadline>%s)(!(delivered_seip=*))(!(delivered=*)))" % (notification_search_end,
                                                                                        notification_deadline_limit)

    notifications = TM.crew_notification.search(search_str)

    datalist=[]
    for notification in notifications:

        data = {}
        if relevant_row(notification.typ.typ,notification.typ.subtype):

            # Get rank and extperkeys from crew_employment
            search_str2 = "(&(crew.id=%s)(validfrom<%s)(validto>=%s))" % (notification.crew.id, now, now)
            extperkeys=TM.crew_employment.search(search_str2)
            extperkey_list = [x for x in extperkeys]
            empno=notification.crew.id
            homebase = "CPH"
            if len(extperkey_list) == 1:
                for employee in extperkey_list:
                    homebase = employee.station
                    if employee.extperkey <> None:
                        empno=employee.extperkey
                    else:
                        empno=notification.crew.id

            data['crewId']= notification.crew.id
            data['empno'] = empno
            tmp_str = get_notificationId(notification).decode("latin1")
            data['notificationId'] = tmp_str.encode("utf-8")
            if (notification.typ.typ=="Automatic" and notification.typ.subtype=="Assignment"):
                data['notificationType'] = "ACTION"
                data['notificationSubType'] = "FLIGHT_CHANGE"
                data['validity_start'] = dateTimeInHomebaseTime(AbsTime(notification.firstmodst), homebase)
                data['validity_end'] = dateTimeInHomebaseTimeEnd(AbsTime(notification.lastmodet), homebase)

            if (notification.typ.typ=="Manual" and notification.typ.subtype=="!NoAlert"):
                data['notificationType'] = "INFORMATIONAL"
                data['notificationSubType'] = "INFORMATION"
                data['validity_start'] = dateTimeInUTC(AbsTime(now))
                data['validity_end'] = dateTimeInUTC(AbsTime(now))

            if (notification.typ.typ=="Manual" and notification.typ.subtype=="*Alert"):
                data['notificationType'] = "ACTION"
                data['notificationSubType'] = "INFORMATION"
                data['validity_start'] = dateTimeInUTC(AbsTime(now))
                data['validity_end'] = dateTimeInUTC(AbsTime(now))


            deadline_for_crew=(AbsTime(notification.deadline)-RelTime(deadline_offset))
            data['deadline'] = dateTimeInUTC(deadline_for_crew)
            data['creationTime'] = dateTimeInUTC(AbsTime(notification.created))
            if notification.typ.typ!="Manual":
                tmp_str = notification.failmsg.decode("latin1")
                data['notificationText'] = tmp_str.encode("utf-8")
            else:
                tmp_str = fetch_notification_message(notification.idnr)
                notification_message = tmp_str.decode("latin1")
                data['notificationText'] = notification_message.encode("utf-8")
            data['additionalInfo'] = "TBD"


            datalist.append(data)
            notification.delivered_seip = now

    return datalist
def get_notificationId(crew_notification):
    return crew_notification.crew.id+";"+str(crew_notification.created)+";"+str(crew_notification.firstmodst)+";"+str(crew_notification.lastmodet)
    end_string = str(crew_notification.lastmodet) if  crew_notification.lastmodet is not None else ""
    return str(crew_notification.created)+";"+start_string+";"+end_string

class CrewNofication():
    def __init__(self):
        """
        Creates an empty Crew_notification message:
            <crewMessage>
              <messageName>CrewNotifaction</messageName>
              <messageBody>
                <crewNotification version="1.0.0-alpha">
                  <empno></empno>
                  <notificationId></notificationId>
                  <notificationType></notificationType>
                  <notificationSubType></notificationSubType>
                  <validity>
                    <start></start>
                    <end></end>
                  </validity>
                  <deadline></deadline>
                  <creationTime></creationTime>
                  <notificationText></notificationText>
                  <additionalInfo></additionalInfo>
                </crewNotification>
              </messageBody>:
        """
        self.tag_empno=XMLElement('empno',{})
        self.tag_notificationId=XMLElement('notificationId',{})
        self.tag_notificationType =XMLElement('notificationType',{})
        self.tag_notificationSubType=XMLElement('notificationSubType',{})
        self.tag_validity = XMLElement('validity',{})
        self.tag_start=XMLElement('start',{})
        self.tag_end=XMLElement('end',{})
        self.tag_validity.append(self.tag_start)
        self.tag_validity.append(self.tag_end)
        self.tag_deadline =  XMLElement('deadline',{})
        self.tag_creationTime = XMLElement('creationTime',{})
        self.tag_notificationText = XMLElement('notificationText',{})
        self.tag_additionalInfo = XMLElement('additionalInfo')

        self.tag_crewNotification=XMLElement('crewNotification',{'version':"1.0.0-beta"})
        self.tag_crewNotification.append(self.tag_empno)
        self.tag_crewNotification.append(self.tag_notificationId)
        self.tag_crewNotification.append(self.tag_notificationType)
        self.tag_crewNotification.append(self.tag_notificationSubType)
        self.tag_crewNotification.append(self.tag_validity)
        self.tag_crewNotification.append(self.tag_deadline)
        self.tag_crewNotification.append(self.tag_creationTime)
        self.tag_crewNotification.append(self.tag_notificationText)
        self.tag_crewNotification.append(self.tag_additionalInfo)

        self.tag_messageBody = XMLElement('messageBody')
        self.tag_messageBody.append(self.tag_crewNotification)

        self.tag_messageName =XMLElement('messageName')
        self.tag_messageName.append('crewNotification')

        self.tag_crewMessage = XMLElement('crewMessage')
        self.tag_crewMessage.append(self.tag_messageName)
        self.tag_crewMessage.append(self.tag_messageBody)

    def make_message(self,data):
        """
        Appends data to the empty CrewNotification message and returns the message as an XML-document
        i.e. the header <?xml version="1.0" encoding="UTF-8"?> added to the message
        :param data: a dict containing the keys created in fetch_data
        :return:
        """

        self.tag_empno.append(data['empno'])
        self.tag_notificationId.append(data['notificationId'])
        self.tag_notificationType.append(data['notificationType'])
        self.tag_notificationSubType.append(data['notificationSubType'])
        self.tag_start.append(data['validity_start'])
        self.tag_end.append(data['validity_end'])
        self.tag_deadline.append(data['deadline'])
        self.tag_creationTime.append(data['creationTime'])
        self.tag_notificationText.append(data['notificationText'])
        self.tag_additionalInfo.append(data['additionalInfo'])
        return str(XMLDocument(self.tag_crewMessage))


class CrewNotifactions():
    def __init__(self, creation_time_offset, deadline_line_offset):
        self.now, = rave.eval('fundamental.%now%')
        self.creation_time_offset = creation_time_offset
        self.dead_line_offset = deadline_line_offset

    def make_reports(self):
        # Fetches data from crew_nofication table and for each row creates a crew_notification message
        # Return a list of crew_notifiaction_messages
        data = fetch_data(self.now, self.creation_time_offset, self.dead_line_offset)
        reports = []
        for d in data:
            cn = CrewNofication()
            report = cn.make_message(d)
            reports.append(report)
        return reports

