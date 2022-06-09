"""
Creates CrewNotifications Messages that is sent to SEIP and is used by IPAD applications by the crew
"""

from report_sources.report_server.rs_if import add_reportprefix, argfix
import xml.etree.ElementTree as ET
import cio.rv as rv
from AbsTime import AbsTime
from tm import TM
import carmensystems.rave.api as rave
from carmensystems.common.report_server_exceptions import ReportServerRequestError

class CrewNotificationAck():

    def __init__(self):
        self.messageType = None
        self.crewId = None
        self.notificationId = None
        self.creationTime = None
        self.now = None

    def _parse(self,XMLmessage):

        #Remove header from message and check that it is an XMLmessage
        i = XMLmessage.find('''<?xml version="1.0"''')
        if i==-1 :
            raise ReportServerRequestError("ERROR: Not an XML message: %s" % (XMLmessage,))
        else:
            XMLmessage=XMLmessage[i:]

        if len(XMLmessage) >0:
            tree = ET.fromstring(XMLmessage)

            incoming_tags = map( lambda x: x.tag , list(tree[1][0]))

            # print "  ## incoming_tags:", incoming_tags

            for my_tag in ["empno", "notificationId", "creationTime"]:
                if my_tag not in incoming_tags:
                    raise ReportServerRequestError("ERROR: XML message missing tag %s: %s" % (my_tag, XMLmessage,))

            self.now, = rave.eval('fundamental.%now%')

            if tree[0].text == "crewNotificationAck":
                self.messageType = "crewNotificationAck"
                empno =           tree[1][0][0].text
                self.notificationId =   tree[1][0][1].text
                self.creationTime =     tree[1][0][2].text

                search_str ="(&(extperkey=%s)(validfrom<%s)(validto>=%s))"%(empno,self.now,self.now)
                crewIds=TM.crew_employment.search(search_str)
                l = [x for x in crewIds]
                if len(l) == 1:
                    for e in l:
                        self.crewId = e.crew.id
                        return True
                else:
                    raise ReportServerRequestError("ERROR: Expected one occurence of crewid for empno %s, found %s. Search string: %s" % (empno, l, search_str))

        else:
            raise ReportServerRequestError("ERROR: XML message is empty")

        return False


    def _OKToSetInformed(self):
        if self.crewId == None :
            raise ReportServerRequestError("ERROR: No crewId was found")
        if self.notificationId == None :
            raise ReportServerRequestError("ERROR: No notificationId was found")

        # Fetch the row for the identification number and the roster change if delivered is None i.e. it is not published
        crew_id,created,firstmodst,lastmodet = self.notificationId.split(";")
        if firstmodst == "None":

            self.setManualAssignmentDelivered(crew_id, created)
            return False
        else:
            search_str = "(&(crew=%s)(created=%s)(firstmodst=%s)(lastmodet=%s)(typ.subtype=Assignment))" %(crew_id, created, firstmodst, lastmodet)

        if crew_id != self.crewId:
            raise ReportServerRequestError("ERROR: crew_id = %s != self.crewId = %s" % (crew_id, self.crewId))

        notifications = [notification for notification in TM.crew_notification.search(search_str)]
        if len(notifications) == 0:
            # Exit silently for now since we get a lot of failed notification searches when the roster is changed after the initial notification was created.
            # To enable warning mails just uncomment the following line.
            # raise ReportServerRequestError("ERROR: Did not find any notifications matching %s" % (search_str,))
            return False

        for notification in notifications:
            notification.delivered = self.now
        return True

    def setManualAssignmentDelivered(self,crew_id, created):
        search_str = "(&(crew=%s)(created=%s)(typ.subtype=*Alert))" % (crew_id, created)
        notifications = [notification for notification in TM.crew_notification.search(search_str)]
        if len(notifications) == 0:
            raise ReportServerRequestError("ERROR: Did not find any notifications matching %s" % (search_str,))
        for notification in notifications:
            notification.delivered=self.now
        TM.save()


    def handleCrewNotificationAck(self,XMLmessage):

        if self._parse(XMLmessage):
            if self._OKToSetInformed():
                rv.publish(self.crewId, rave.eval('fundamental.%pp_start%')[0], self.now, None)
            # else:
            #     raise ReportServerRequestError("ERROR: Not OK to set informed for message %s" % (XMLmessage,))
        else:
            raise ReportServerRequestError("ERROR: Could not parse message %s" % (XMLmessage,))


@argfix
@add_reportprefix
def generate(*a, **k):
    XMLmessage =  a[0]
    ack = CrewNotificationAck()
    ack.handleCrewNotificationAck(XMLmessage)

    reports = []
    return reports, True

