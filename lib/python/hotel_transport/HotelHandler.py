"""
HotelHandler

Functions to handle hotel booking assignment attributes.
"""

import modelserver
import carmensystems.rave.api as R
from utils.selctx import SingleCrewFilter
import Cui
from AbsTime import AbsTime
from AbsDate import AbsDate
from tm import TM
import carmstd.studio.cfhExtensions as cfhExtensions 
import carmusr.Attributes as Attributes
import utils.mnu as mnu
import Gui

def getPreviousBooking(crew, checkIn, airport=None):
    print "Looking for a booking on", crew, checkIn, airport
    TM("airport_hotel")
    TM("hotel")
    for hb in crew.referers('hotel_booking','crew'):
        if hb.checkin == AbsTime(checkIn):
            print "Matching checkin for crew"
            if airport == None: return hb
            for ah in hb.hotel.referers('airport_hotel','hotel'):
                if ah.airport.id == airport: return hb
    return None

def getCrewEmployment(crew, date):
    for ce in crew.referers('crew_employment','crew'):
        if ce.validfrom < date and ce.validto >= date:
            return ce
def getHotelDescription(crew, now, hotel, airport):
    if not hotel: return ""
    if isinstance(hotel, str):
        hotel = TM.hotel.find(hotel)
    if airport:
        ce = getCrewEmployment(crew, now)
        if ce:
            for phe in hotel.referers('preferred_hotel_exc','hotel'):
                if phe.airport.id == airport and ce.crewrank.maincat == phe.maincat and ce.region == phe.region and phe.validfrom < now and phe.validto >= now:
                        if phe.airport_hotel:
                            return "%s (airport hotel)" % hotel.id
                        else:
                            break
            return "%s (city hotel)" % hotel.id
    return hotel.id


def handleLegHotelSwitch(area, crewId, leg, airportId, attr):
    import carmusr.modcrew as modcrew
            
    Attributes.setSelectionObject(area, Cui.LegMode, leg)
    if attr:
        Attributes.SetAssignmentAttrCurrent("HOTEL_BOOKING", str=attr)
    else:
        Attributes.RemoveAssignmentAttrCurrent("HOTEL_BOOKING")
    modcrew.add(crewId)

def hotelMenu(menu):
    print "Hotel menu",menu
    TM("preferred_hotel")
    TM("preferred_hotel_exc")
    now = R.eval("fundamental.%now%")[0]
    
    area = Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea)
    
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    if len(marked_legs) > 1:
        return
    leg = str(marked_legs[0])
    
    Cui.CuiSetSelectionObject(Cui.gpc_info, area, Cui.LegMode, leg)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, "object")
    crew, stn, htl, rgn, flight_id, next_flight_id = R.eval(R.selected(R.Level.atom()), "crew.%id%", "leg.%end_station%", "report_hotel.%layover_hotel_id%", "leg.%region%", "hotel.%flight_id%", "hotel.%next_flight_id%")

    if not htl is None and TM.hotel.find(htl) is None:
        Gui.GuiWarning("Reference error: report_hotel.%%layover_hotel_id%% returns value %s that does not exist in table hotel" % htl)
        return

    airport = TM.airport.find(stn)
    if airport == None: return
    
    cityHotel = None
    defaultCityHotel = None
    airportHotel = None

    mnu.Button("Auto (%s)" % htl, action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "")).attach(menu)
    mnu.Button("No hotel", action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "H-")).attach(menu)
    mnu.Separator().attach(menu)


    for f in airport.referers("preferred_hotel_exc","airport"):
        if f.region.id != rgn: continue
        if f.validfrom > now or f.validto < now:
            continue

        if f.arr_flight_nr <> "*" and f.arr_flight_nr <> "":
            if flight_id <> f.arr_flight_nr:
                continue
        if f.dep_flight_nr <> "*" and f.dep_flight_nr <> "":
            if next_flight_id <> f.dep_flight_nr:
                continue

        try:
            if f.airport_hotel:
                airportHotel = f.hotel.id
            else:
                cityHotel = f.hotel.id
        except modelserver.ReferenceError as e:
            print e
            Gui.GuiWarning(str(e))


    for f in airport.referers("preferred_hotel","airport"):
        if f.validfrom > now or f.validto < now:
            continue
        try:
            defaultCityHotel = f.hotel.id
        except modelserver.ReferenceError as e:
            print e
            Gui.GuiWarning(str(e))
        break
    
    #Check that the hotels have valid contracts
    cityHotel, = R.eval(R.selected(R.Level.atom()), 'hotel.%%hotel_contract_hotel_id%%("%s", leg.%%end_utc%%)' % cityHotel)
    defaultCityHotel, = R.eval(R.selected(R.Level.atom()), 'hotel.%%hotel_contract_hotel_id%%("%s", leg.%%end_utc%%)' % defaultCityHotel)
    airportHotel, = R.eval(R.selected(R.Level.atom()), 'hotel.%%hotel_contract_hotel_id%%("%s", leg.%%end_utc%%)' % airportHotel)

    if cityHotel == None and defaultCityHotel == None:
        pass
    elif cityHotel == airportHotel or airportHotel == None:
        if cityHotel <> None:
            mnu.Button("%s (city)" % cityHotel, action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "H="+cityHotel)).attach(menu)
        if defaultCityHotel <> None and defaultCityHotel <> cityHotel:
            mnu.Button("%s (city)" % defaultCityHotel, action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "H="+defaultCityHotel)).attach(menu)
    else:
        mnu.Button("%s (airport)" % airportHotel, action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "H="+airportHotel)).attach(menu)
        mnu.Button("%s (city)" % defaultCityHotel, action=lambda: handleLegHotelSwitch(area, crew, leg, stn, "H="+defaultCityHotel)).attach(menu)
    
    
        

def handleHotels(area, crewId, legs):
    """Find out all the hotel layovers associated with the
    specified legs, and run handleHotelsImpl for them"""
    
    starts = [AbsTime(leg.leg_start) for leg in legs]
    
    prevLeg = (None, False)
    legSet = set()
    for _,needHotel,start in R.eval(SingleCrewFilter(crewId).context(), R.foreach(R.iter('iterators.leg_set'),
                        'report_hotel.%need_hotel%',
                        'leg.%start_utc%'))[0]:
        if needHotel and start in starts:
            legSet.add(start)
        elif prevLeg[1] and start in starts:
            legSet.add(prevLeg[0])
        prevLeg = (start, needHotel)
        
    if len(legSet) > 0:
        handleHotelsImpl(area, crewId, list(legSet))

def handleHotelsImpl(area, crewId, start_times):
    assert len(start_times) >= 1, "Invalid start_times"
    conds = ['(leg.%start_utc%='+' or leg.%start_utc%='.join([str(start_time) for start_time in start_times])+')']
    conds.append('report_hotel.%need_hotel%')

    now = R.eval("fundamental.%now%")[0]
    for _,leg,assignment,flt,airportId,hotelId,checkIn in R.eval(SingleCrewFilter(crewId).context(), R.foreach(R.iter('iterators.leg_set', where=tuple(conds)),
                              'leg_identifier',
                              'leg.%code%',
                              'leg.%flight_id%',                                                           
                              'leg.%end_station%',
                              'report_hotel.%layover_hotel_id%',
                              'report_hotel.%check_in%'))[0]:
        crew = TM.crew.find(crewId)
        if assignment == "FLT":
            assignment = str(flt).strip()
        bk = getPreviousBooking(crew, checkIn, airportId)
        if bk:
            if bk.hotel.id != hotelId:
                oldHotel = getHotelDescription(crew, now, bk.hotel, airportId)
                newHotel = getHotelDescription(crew, now, hotelId, airportId)
                ret = cfhExtensions.ask("Assignment of %s on %s.\nCrew %s is booked on hotel %s, but \nthe assignment needs a booking on %s. \nWhat do you want to do?" % (assignment, str(AbsDate(checkIn)), crewId, oldHotel, newHotel) ,buttons=[("change","_Change"),("keep","_Keep"),("no","_No hotel"),("CANCEL","_Cancel")],default_button="change",title="Hotel booking change")
                if ret == "CANCEL": return 1
                if ret == "no":
                    attr="H-"
                elif ret == "keep":
                    attr="H="+bk.hotel.id
                else:
                    attr=""
                handleLegHotelSwitch(area, crewId, leg, airportId, attr)
    return 0

