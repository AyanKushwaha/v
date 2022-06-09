'''
Created on Feb 21, 2012

@author: pergr
'''
# namespaces
TRIP_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/trip"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
COMMON_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/common"
FRAMEWORK_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication"
GETROSTER_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getroster"
GETROSTERCARRYOUT_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getrostercarryout"
GETALLTRIPS_NAMESPACE = "http://carmen.jeppesen.com/crewweb/framework/xmlschema/backendcommunication/getalltrips"
REQUEST_NAMESPACE = "http://carmen.jeppesen.com/crewweb/interbids/xmlschema/backendcommunication/request"


# request names
GET_ROSTER_REQUEST = 'getRosterParameters'
GET_ROSTER_RESPONSE = 'getRosterResponse'

GET_ROSTER_CARRYOUT_REQUEST = 'getRosterCarryoutParameters'
GET_ROSTER_CARRYOUT_RESPONSE = 'getRosterCarryoutResponse'

GET_ALL_TRIPS_REQUEST = 'getAllTripsParameters'
GET_ALL_TRIPS_RESPONSE = 'getAllTripsResponse'

GET_AVAILABLE_DAYSOFF_REQUEST = "availableDaysOffParameters"
GET_AVAILABLE_DAYSOFF_RESPONSE = "availableDaysOffResponse"

CREATE_DAYSOFF_REQUEST = 'requestParameters'
CREATE_DAYSOFF_RESPONSE = 'requestResponse'

# status response to create_request
AWARDED = 'awarded'
REJECTED = 'rejected'
ERROR = 'error'
CANCELLED = 'cancelled'
GRANTED = 'granted'

# Number of seconds required between bid requests for FS and F7S.
LOCK_GRACE_TIME = 20
# Number of seconds until the lock for a request completely times out.
LOCK_TIMEOUT = 120

#xml tags
CATEGORY_TAG = 'category'
TYPE_TAG = 'type'
INTERVAL_TAG = 'interval'
TO_TAG = 'to'
FROM_TAG = 'from'
CREW_ID_TAG = 'biddingCrewId'
NAME_TAG = 'name'
VALUE_TAG = 'value'
STARTTIME_TAG = 'start'
STARTDATE_TAG = 'startDate'
ENDDATETIME_TAG = 'endDateTime'
STARTDATETIME_TAG = 'startDateTime'
DURATION_TAG = 'nr_of_days'
ATTRIBUTES_TAG = 'attributes'
ATTRIBUTE_TAG = 'attribute'
POSITION = 'position'
QUANTITY = 'quantity'
PERIOD = 'period'
ROSTER_TAG = 'roster'
TRIP_TAG = 'CRR'
CODE_TAG = 'code'
# request names
VERSION = 'version'
LIST_MODULES = 'list_modules'
RELOAD_MODULES = 'reload_modules'
GET_ROSTERS = 'get_rosters'
GET_ALL_TRIPS = 'get_all_trips'
GET_TRIPS = 'get_trips'
GET_AVAILABLE_DAYS_OFF = 'get_available_days_off'
CREATE_REQUEST = 'create_request'
CANCEL_REQUEST = 'cancel_request'
GET_ROSTER_CARRYOUT = 'get_roster_carryout'

# encoding used
MODEL_ENCODING = 'latin-1'
CREWPORTAL_ENCODING = 'UTF-8' 
