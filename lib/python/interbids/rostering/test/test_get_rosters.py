
import xmlrpclib
import xml.etree.ElementTree as ET
from xml.dom import minidom
import StringIO


roster_request = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns7:getRosterParameters biddingCrewId="27117" authenticatedCrewId="27117" id="114ac6fa-12b3-4331-a1bc-710619541ede" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns10="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster" xmlns:ns8="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"/>'

roster_request_apa_crew = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns7:getRosterParameters biddingCrewId="APA" authenticatedCrewId="10034" id="114ac6fa-12b3-4331-a1bc-710619541ede" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns10="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster" xmlns:ns8="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"/>'

get_all_trips_request='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns6:getAllTripsParameters biddingCrewId="10033" authenticatedCrewId="10034" id="89154327-8564-447a-86da-d3c4169fe8ff" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns10="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster" xmlns:ns8="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"/>'

get_available_daysoff_request='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns8:availableDaysOffParameters category="A_F7S" biddingCrewId="27117" authenticatedCrewId="27117" id="d3f9134f-43c4-4040-beb1-6f6a9889dd92" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns10="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster" xmlns:ns8="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"><ns8:interval><ns3:from>2012-03-01</ns3:from><ns3:to>2012-03-30</ns3:to></ns8:interval></ns8:availableDaysOffParameters>'




create_request_no_limit = cancel_request = create_request='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns9:requestParameters type="FS" category="A_FS" biddingCrewId="11785" authenticatedCrewId="11785" id="cd1fdc7a-8771-4f0a-9868-eef93f38115b" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns10="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns11="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns8="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"><ns9:period><ns4:from>2012-06-01</ns4:from><ns4:to>2012-07-30</ns4:to></ns9:period><ns9:attributes><ns5:attribute name="startDate" value="2012-06-15"/><ns5:attribute name="start" value="2012-06-15 00:00"/><ns5:attribute name="nr_of_days" value="2"/></ns9:attributes></ns9:requestParameters>'

cancel_request ='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns9:requestParameters type="F7S" category="A_F7S" biddingCrewId="10033" authenticatedCrewId="10033" id="de3c0892-3d11-4490-9cc4-5536b915b574" xmlns:ns2="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource" xmlns="http://carmen.jeppesen.com/crewweb/framework/xmlschema/import" xmlns:ns4="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication" xmlns:ns3="http://carmen.jeppesen.com/crewweb/framework/xmlschema/datasource/configuration" xmlns:ns9="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request" xmlns:ns5="http://carmen.jeppesen.com/crewweb/framework/xmlschema/common" xmlns:ns6="http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip" xmlns:ns10="http://carmen.jeppesen.com/crewweb/interbids/xmlschema/requesttype" xmlns:ns7="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips" xmlns:ns11="http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype" xmlns:ns8="http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"><ns9:period><ns4:from>2012-06-01</ns4:from><ns4:to>2012-06-30</ns4:to></ns9:period><ns9:attributes><ns5:attribute name="startDate" value="2012-06-11"/><ns5:attribute name="start" value="2012-06-11 00:00"/><ns5:attribute name="nr_of_days" value="1"/></ns9:attributes></ns9:requestParameters>'
connection = 'http://batuna:13848'
#connection = 'http://goondiwindi:13848'

#b =  xmlrpclib.ServerProxy('http://dodoma:1798')

s = xmlrpclib.ServerProxy(connection)

#s.xmlrpc_listfunctions()

def _print(string, name):
    print  "#"*100
    fd = None
    try:
        fd = open("%s.xml"%name,'w')
        fd.write(str(string))
        print string[:1000]
        fd.close()
    except Exception, err:
        import traceback
        traceback.print_exc()
        print err
        if not fd is None:
            fd.close()
    
    
if __name__ == '__main__':
   # _print(s.version(),'version')
   # _print(s.get_rosters(roster_request),'roster_request')
   #_print(s.get_rosters(roster_request_apa_crew),'roster_request_apa_crew')
   #_print(s.get_all_trips(get_all_trips_request),'get_all_trips_request')
   #_print(s.get_available_days_off(get_available_daysoff_request),'get_available_daysoff_request')
   # _print(s.create_request(create_request_no_limit),'create_request_no_limit')
   _print(s.create_request(create_request),'create_request')
   #_print(s.cancel_request(cancel_request),'cancel_request')
   # s.toggle_call_log()
   #s.toggle_profiling()
   pass

def get_first_elementByTagNameNS(element, ns, localname):
    """
    Returns the first element in NodeList matching namespace and localname
    Will return None on empty list
    """
    try:
        return element.getElementsByTagNameNS(ns, localname)[0]
    except IndexError:
        return None

def dom_unpack_text_node(node, latin_encode=False):
    """
    Python DOM stores text in sepcuial way, let's unpack it
    Will return first text section in node
    """
    for childNode in [childNode for childNode in node.childNodes if childNode.nodeType == childNode.TEXT_NODE]:
        if latin_encode:
            return childNode.data.encode('latin-1')
        else:
            return childNode.data
        
## from xml.dom import minidom
## import StringIO
## doc = minidom.parse(StringIO.StringIO(create_request))

## CREATE_NS = "http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"
## COMMON = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/common"
## REQUEST = "requestParameters"

## ns8 = "http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"
## ns4 = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/common"
## ns3 = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication"

## ## #<ns8:period>
## ## #  <ns3:from>2012-03-01</ns3:from>
## ## #  <ns3:to>2012-05-31</ns3:to>
## ## #</ns8:period>
## ## #<ns8:attributes>
## ## #   <ns4:attribute name="startDate" value="2012-03-01"/>
## ## #   <ns4:attribute name="start" value="2012-03-01 00:00"/>
## ## #   <ns4:attribute name="endDate" value="2012-05-31"/>
## ## #   <ns4:attribute name="end" value="2012-05-31 23:59"/>
## ## #</ns8:attributes>


## request = get_first_elementByTagNameNS(doc,CREATE_NS,REQUEST)

## if request:
##     print "handle get days off"
##     print request
##     crew = request.attributes.getNamedItem('biddingCrewId').value
##     bidtype = request.attributes.getNamedItem('category').value

## ##     period = get_first_elementByTagNameNS(request,
## ##                                           ns8,
## ##                                           "period")
## ##     print "period", period
## ##     if period:
## ##         from_node = get_first_elementByTagNameNS(request,
## ##                                                  ns3,
## ##                                                  "from")
## ##         if from_node:
## ##             print dom_unpack_text_node(from_node, True)
            
## ##         to_node = get_first_elementByTagNameNS(request,
## ##                                                  ns3,
## ##                                                  "to")
## ##         if to_node:
## ##             print dom_unpack_text_node(to_node, True)
    
##     interval = get_first_elementByTagNameNS(request,
##                                             ns8,
##                                             "attributes")   
    
##     starttime = endtime = None
##     print "interval", interval
##     if interval:
##         print interval
##         for node in interval.getElementsByTagNameNS(ns4,
##                                                     'attribute'):
##             if node.attributes['name'].value == "start":
##                 print node.attributes['value'].value.encode('latin-1')
##             if node.attributes['name'].value == "end":
##                 print node.attributes['value'].value.encode('latin-1')

                
             
            
                

                                       

## ## doc = minidom.parse(StringIO.StringIO(get_all_trips_request))

## ## GETROSTER_NAMESPACE_URI_LOCALNAME = ['http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster',
## ##                                      'getRosterParameters']

## ## GETALLTRIPS_NAMESPACE_URI_LOCALNAME = ['http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips',
## ##                                        'getAllTripsParameters']
## GETDAYSOFF_NAMESPACE_URI_LOCALNAME = ['http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request',
##                                       "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication",
##                                       "http://carmen.jeppesen.com/crewweb/framework/xmlschema/bidtype",
##                                       'availableDaysOffParameters',
##                                       'interval',
##                                       'from',
##                                       'to']

## #<ns8:interval>
## #  <ns3:from>2012-03-01</ns3:from>
## #  <ns3:to>2012-05-31</ns3:to>
## #</ns8:interval>

## def get_first_elementByTagNameNS(element, ns, localname):
##     """
##     Returns the first element in NodeList matching namespace and localname
##     Will return None on empty list
##     """
##     try:
##         return element.getElementsByTagNameNS(ns, localname)[0]
##     except IndexError:
##         return None

## def dom_unpack_text_node(node, latin_encode=False):
##     """
##     Python DOM stores text in sepcuial way, let's unpack it
##     Will return first text section in node
##     """
##     for childNode in [childNode for childNode in node.childNodes if childNode.nodeType == childNode.TEXT_NODE]:
##         if latin_encode:
##             return childNode.data.encode('latin-1')
##         else:
##             return childNode.data
    
## request= get_first_elementByTagNameNS(doc,
##                                       GETDAYSOFF_NAMESPACE_URI_LOCALNAME[0],
##                                       GETDAYSOFF_NAMESPACE_URI_LOCALNAME[3])

## crew = None
## bidtype = None
## start = None
## end = None

## if request:
##     print "handle get days off"

##     crew = request.attributes.getNamedItem('biddingCrewId').value
##     bidtype = request.attributes.getNamedItem('category').value

##     interval =  get_first_elementByTagNameNS(request,
##                                              GETDAYSOFF_NAMESPACE_URI_LOCALNAME[0],
##                                              GETDAYSOFF_NAMESPACE_URI_LOCALNAME[4])
##     if interval:
##         print interval
##         f = get_first_elementByTagNameNS(interval,
##                                          GETDAYSOFF_NAMESPACE_URI_LOCALNAME[1],
##                                          GETDAYSOFF_NAMESPACE_URI_LOCALNAME[5])
##         print dom_unpack_text_node(f)
##         t = get_first_elementByTagNameNS(interval,
##                                          GETDAYSOFF_NAMESPACE_URI_LOCALNAME[1],
##                                          GETDAYSOFF_NAMESPACE_URI_LOCALNAME[6])
##         print dom_unpack_text_node(t)

## ## request = doc.getElementsByTagNameNS(GETROSTER_NAMESPACE_URI_LOCALNAME[0],
## ##                                      GETROSTER_NAMESPACE_URI_LOCALNAME[1])

## ## if request:
## ##     print "handle get rosters"
## ##     for i in request:
## ##         print i.attributes.getNamedItem('biddingCrewId').name
## ##         print i.attributes.getNamedItem('biddingCrewId').value

## ## request = doc.getElementsByTagNameNS(GETALLTRIPS_NAMESPACE_URI_LOCALNAME[0],
## ##                                      GETALLTRIPS_NAMESPACE_URI_LOCALNAME[1])


## ## if request:
## ##     print "handle get all trips"
## ##     for i in request:
## ##         print i.attributes.getNamedItem('biddingCrewId').name
## ##         print i.attributes.getNamedItem('biddingCrewId').value
        
## import xml.etree.ElementTree as ET

## doc2=ET.fromstring(roster_request)
## print doc2.tag 
## print doc2.get('biddingCrewId')



