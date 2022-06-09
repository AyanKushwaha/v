#

#
"""
Hotel Booking Report utility functions.
"""

from carmensystems.publisher.api import *
from utils.divtools import default as D
import hotel_transport.HotelBookingData as H
import hotel_transport.TransportBookingData as T
import carmensystems.rave.api as R
from AbsDate import AbsDate
import os


import Cfh



def add_rows(column, title, texts):
    """ Add rows to a column box, the title is in bold
        and the texts is a list. Line breaks are added
        when the row is to too long. 
        Example:  add_rows(dummy, 'Address', ['Gotgatan 1', 'Stockholm'])
        Address: Gotgatan 1
                 Stockholm
        
        Example: add_rows(dummy, 'Address': ['Odinsgatan vid centralen', 'Goteborg'])
        Address: 
         Odinsgatan vid centralen
         Goteborg
            
    
    """
    title_len = len(title)
    text_len = len(max(texts, key=len))
    if title_len + text_len > 32:
        column.add(Row(Text('%s:' % title, font=Font(weight=BOLD))))
        for text in texts:
            column.add(Row(Text(' %s' % text)))                       
    else:
        column.add(Row(Text('%s:' % title, font=Font(weight=BOLD)),
                    Text('%s' % texts[0])))
        for text in texts[1:]:
            column.add(Row(Text(''),
                        Text('%s' % text)))                       
    
def add_email_rows(column, email_addresses):
    """ Add emails addresses. Adds linebreaks if needed """
        
    emails = separateMails(email_addresses)
    if ((len(emails) <= 1) and (len(emails[0]) <= 30)):
        column.add(Row(Text('e-mail:', font=Font(weight=BOLD)),
                         Text('%s' % (email_addresses))))   
    else:
        column.add(Row(Text('e-mail(s):', font=Font(weight=BOLD))))
        nof_emails = len(emails)
        for indx, email in enumerate(emails):
            if len(email) <= 35:
                column.add(Row(Text(' %s%s' % (email, ["",","][nof_emails - indx > 1]))))
            else:
                head, tail = email.split("@")
                column.add(Row(Text(' %s@' % (head))))
                column.add(Row(Text(' %s%s' % (tail, ["",","][nof_emails - indx > 1]))))

    
    

def companyColumn(title, name, street, postal_city, phone, fax, email):
    """ A company column """ 
    
    companyBox = Column(
        Row(Text(title,
                 font=Font(size=9, weight=BOLD),
                 background='#cdcdcd',
                 align=CENTER,
                 colspan=2)),
            width=100)

    add_rows(companyBox, "Company", [name])    
    add_rows(companyBox, "Address", [D(street), D(postal_city)])
    add_rows(companyBox, "Phone", [D(phone)])
    add_rows(companyBox, "Fax", [D(fax)])
    add_email_rows(companyBox, D(email))
                
    return companyBox


def infoBox(title, fromDate, toDate):
    """
    Creates an Information Box.
    """
    infoBox = Column(
        Row(Text(title,
                 font=Font(size=9, weight=BOLD),
                 background='#cdcdcd',
                 align=CENTER,
                 colspan=2)),
        Row(Text('Period:', font=Font(weight=BOLD)),
            Text('%s-%s' % (fromDate, toDate))),
        Row(Text('Day period:', font=Font(weight=BOLD)),
            Text('from 02:00 to 01:59')),
        Row(Text('Local times!', 
                 font=Font(weight=BOLD), colspan=2)))

    return infoBox

def getHotel(hotelId):

    bookingManager = T.TransportBookingManager()
    if hotelId.lower() in ['default', 'none']:
        class HotelTemp:
            def __init__(self):
                if hotelId.lower() == 'none':
                    self.name = 'No booking required'
                else:
                    self.name = 'No hotel defined'
                self.street = None
                self.postalcode = None
                self.city = None
                self.tel = None
                self.fax = None
                self.email = None
        hotel = HotelTemp()
    else:
        hotel = bookingManager.getHotelData(hotelId)
    return hotel

def hotelBox(hotelId):
    """
    Creates a Hotel information Box.
    """
    hotel = getHotel(hotelId)
    return companyColumn('from/to Hotel', 
                         hotel.name, 
                         hotel.street, 
                         '%s %s' % (D(hotel.postalcode), D(hotel.city)), 
                         hotel.tel, 
                         hotel.fax, 
                         hotel.email) 


def getTransport(transportId):
    bookingManager = T.TransportBookingManager()
    if transportId == 'default':
        class TransportTemp:
            def __init__(self):
                self.name = 'No transport defined'
                self.street = None
                self.postalcode = None
                self.city = None
                self.tel = None
                self.fax = None
                self.email = None
        transport = TransportTemp()
    else:
        transport = bookingManager.getTransportData(transportId)
    return transport

def transportBox(transportId):
    """
    Creates a Transport information Box.
    """
    transport = getTransport(transportId)

    return companyColumn('Transport Co.', 
                         transport.name, 
                         transport.street, 
                         '%s %s' % (D(transport.postalcode), D(transport.city)), 
                         transport.tel, 
                         transport.fax, 
                         transport.email) 

def getHotelRegion(country):
    """
    convert country to region
    """
    if country == "SE":
        region="SKS"
    elif country == "NO":
        region="SKN"
    else:
        region="SKD"
    return region

def customerBox(region,hotelId):
    """
    Creates a Customer information Box.
    """
    bookingManager = T.TransportBookingManager()
    if hotelId.lower() in ['default', 'none']:
        region="SKD"
    else:
        hotel = bookingManager.getHotelData(hotelId)
        region = getHotelRegion(hotel.country)

    customer = bookingManager.getCustomerData(region)

    customerBox = Column(Row(Text('Customer',
                                  font=Font(size=9, weight=BOLD),
                                  background='#cdcdcd',
                                  align=CENTER,
                                  colspan=2)),
                         width=100)

    company_name = [D(customer.name)]
        
    if customer.careof:
        company_name.append('c/o %s' % customer.careof)
    
    add_rows(customerBox, "Company", company_name)

    
    add_rows(customerBox, "Department", [D(customer.department)])
    add_rows(customerBox, "Address", ["%s %s" % (D(customer.postalcode),D(customer.city)),
                                      D(customer.country)])

    add_rows(customerBox, "Contact", [D(customer.contact)])
    
    if customer.phone:
        add_rows(customerBox, "Phone", [D(customer.phone)])
        
    if customer.fax:        
        add_rows(customerBox, "Fax", [D(customer.fax)])

    add_email_rows(customerBox, D(customer.email))
    
                            
    return customerBox

class CfhHotelString(Cfh.String):
    """
    this class is used for creating a list of airports
    in the form  when selecting the hotel company
    """
    def __init__(self, box, name, maxLength, airportField):
        Cfh.String.__init__(self, box, name, maxLength)
        self.airportField = airportField

    def check(self, hoteltext):
        checkString = Cfh.String.check(self,hoteltext)
        if not checkString and not self.airportField == '':
            bookingManager = H.HotelBookingManager()
            airportList = [(airp[0], airp[1]) for airp in bookingManager.getAirports(hoteltext)]
            airportList.sort()
            airports = 'Airport;' + ';'.join(['%s:%s: %s' % (airpId, airpId, name)
                                              for (airpId, name) in airportList])
            self.airportField.setMenuString(airports)
            return None
        else:
            return checkString

class CfhTransportString(Cfh.String):
    """
    this class is used for creating a list of airports
    in the form  when selecting the transport company
    """
    def __init__(self, box, name, maxLength, airportField):
        Cfh.String.__init__(self, box, name, maxLength)
        self.airportField = airportField

    def check(self, transporttext):
        checkString = Cfh.String.check(self,transporttext)
        if not checkString and not self.airportField == '':
            bookingManager = T.TransportBookingManager()
            airportList = [(airp[0], airp[1]) for airp in bookingManager.getAirports(transporttext)]
            airportList.sort()
            airports = 'Airport;' + ';'.join(['%s:%s: %s' % (airpId, airpId, name)
                                              for (airpId, name) in airportList])
            self.airportField.setMenuString(airports)
            return None
        else:
            return checkString

class CfhAirportHotelString(Cfh.String):
    """
    this class is used for creating a list of hotels
    in the form  when selecting the airport
    """
    def __init__(self, box, name, maxLength, hotelField):
        Cfh.String.__init__(self, box, name, maxLength)
        self.hotelField = hotelField

    def check(self, airporttext):
        checkString = Cfh.String.check(self,airporttext)
        if not checkString and not self.hotelField == '':
            if airporttext == 'DEFAULT':
                hotels = 'Hotel;DEFAULT:(Missing);NONE:(None)'
            else:
                bookingManager = H.HotelBookingManager()
                hotelList = [(hotel.name, hotel.city, hotel.country, hotel.id)
                            for hotel in bookingManager.getHotels(airporttext)]
                hotelList.sort()
                hotelmenu = ['%s:%s: %s %s %s' % (hotelId, hotelId, name, city, country) for (name, city, country, hotelId) in hotelList]
                if not hotelmenu:
                    hotelmenu = ["DEFAULT:(No hotels defined)"]
                hotels = 'Hotel;' + ';'.join(hotelmenu)
                       
            self.hotelField.setMenuString(hotels)
            return None
        else:
            return checkString
            
class CfhAirportTransportString(Cfh.String):
    """
    this class is used for creating a list of transport
    companies in the form  when selecting the airport
    """
    def __init__(self, box, name, maxLength, transportField):
        Cfh.String.__init__(self, box, name, maxLength)
        self.transportField = transportField

    def check(self, airporttext):
        checkString = Cfh.String.check(self,airporttext)
        if not checkString and not self.transportField == '':
            bookingManager = T.TransportBookingManager()
            transportList = [(transport.name, transport.city, transport.country, transport.id)
                            for transport in bookingManager.getTransports(airporttext)]
            transportList.sort()
            transports = 'Transport;' + ';'.join(['%s:%s: %s %s %s' % (transportId, transportId, name, city, country)
                                                  for (name, city, country, transportId) in transportList])
            self.transportField.setMenuString(transports)
            return None
        else:
            return checkString
            
class CfhDateInRange(Cfh.Date):
    """
    this class is used for checking the date input to be
    only in the planning period
    """
    def __init__(self, box, name, initialValue, fromDate, toDate):
        self.toDate = toDate
        self.fromDate = fromDate
        Cfh.Date.__init__(self, box, name, initialValue)

    def check(self,dateStr):
        s = Cfh.Date.check(self,dateStr)
        if s: return s
        if self.fromDate and AbsTime(dateStr) < self.fromDate:
            return "Minimum date is %s" % str(self.fromDate)[:10]
        if self.toDate and AbsTime(dateStr) > self.toDate:
            return "Maximum value is %s" % str(self.toDate)[:10]

        return None
    
def separateMails(emails):
    """ 
    returns list of emails separated by comma, and without ' '
    """
    result = ''
    if len(D(emails,[])) == 0:
        return [result]
    elif (emails.count('@') <= 1):
        for i in emails.split():
            result += i
        return [result]
    elif (emails.count(',') < 1):
        return [x for x in emails.split() if '@' in x]
    else: 
        emailsWithNoSpaces = emails.replace(' ','')
        return emailsWithNoSpaces.split(',')
    
def getFirstEmail(email):
    """
    in case the field email in hotel_customer table has 
    more than one email, this method gets the first one
    """
    emails = separateMails(email)
    return emails[0]

def createFileName(name, region, hotel, date, isUpdate=False, isHotel=True,fileFormat = "PDF"):
    """
    this creates a directory for every month, in case it doesn't exists,
    and a filename with region, hotel and date as suffix and title as
    prefix. If filename exists, it adds a number as suffix.
    """
    if isHotel:
        dir = H.getExportDir()
    else:
        dir = T.getExportDir()
    (year, month, day) = AbsDate(date).split()
    # (in case a folder wants to be created)
    #path = dir + '/%s' % dateStr[2:]
    #if not os.path.exists(path):
    #    os.mkdir(path)
    baseName = dir + '/%d%02d%02d.%s.%s.%s' % (
        year, month, day, name, region, hotel)
    i = 1
    if isUpdate:
        if fileFormat == "PDF":
            fileName = baseName + '.U%d.pdf' % i
        else:
            fileName = baseName + '.U%d.txt' % i

        while os.path.exists(fileName):
            i += 1
            if fileFormat == "PDF":
                fileName = baseName + '.U%d.pdf' % i
            else:
                fileName = baseName + '.U%d.txt' % i
    else:
        if fileFormat == "PDF":
            fileName = baseName + '.pdf'
        else:
            fileName = baseName + '.txt'

        i = 1
        while os.path.exists(fileName):
            i += 1

            if fileFormat == "PDF":
                fileName = baseName + '-%d.pdf' % i
            else:
                fileName = baseName + '-%d.txt' % i

    return fileName

def getHeaderItems(fromStudio, isAllRegions, isLandscape=False):
    """
    this will create a subheader remarking that its a draft report
    if the report has been created from Studio, not from the batch job
    """
    
    headerItemsDict = {}
    if fromStudio: 
        try:
            user = R.eval('user')[0]
        except:
            # [acosta:08/094@16:28] Non-Studio env
            import utils.Names as Names
            user = Names.username()
        nowTime, = R.eval('fundamental.%now%')
        headerItemsDict = {'By user: ':user, 'Manually created: ':nowTime, 'Type: ':'draft report'}
        if not isAllRegions: 
            studioRegion, = R.eval('planning_area.%filter_company_p%')
            # This text must be short to fit in the report
            warnText = ' Only %s, flights may be incomplete (use ALL regions)' % (studioRegion)
            headerItemsDict['Warning! '] = warnText
    return headerItemsDict


