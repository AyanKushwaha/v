import carmensystems.rave.api as R
import Attributes
import Cui
import AbsTime
import carmensystems.rave.api as rave
from tm import TM




def init_cabin_in_charge_cimber():
    default_bag = R.context('sp_crew').bag()
    for roster_bag in default_bag.iterators.roster_set(where='crew.%has_agmt_group_qa_cc%'):
        seniority = roster_bag.crew.seniority()
        crew_id = roster_bag.crew.id()
        for leg_bag in roster_bag.iterators.leg_set():
            if leg_bag.leg.is_flight_duty():
                min_seniority = leg_bag.crew_pos.seniority_cc()
                if min_seniority == seniority:
                    Attributes.SetCrewFlightDutyAttr(crew_id, leg_bag.leg.udor(), leg_bag.leg.flight_descriptor(), leg_bag.leg.start_station(),"IN_CHARGE", refresh=False, str ="C")

def remove_in_charge_for_this_flight(udor, flight_descriptor, airport):
    # Find all crew_flight_duty_attr for this leg and remove.
    flight_search_str = "(&(udor=%s)(fd=%s)(adep=%s))" % (udor.yyyymmdd(), flight_descriptor,airport)

    flights = TM.flight_leg.search(flight_search_str)
    for flight in flights:
        crew_flight_duties = flight.referers('crew_flight_duty','leg')
        for crew_flight_duty in crew_flight_duties:
            crew_flight_duty_attrs = crew_flight_duty.referers('crew_flight_duty_attr','cfd')
            for attr in crew_flight_duty_attrs:
                if attr.attr.id == "IN_CHARGE":
                    attr.remove()



def set_selected_crew_in_charge():
    marked_legs = Cui.CuiGetLegs(Cui.gpc_info, Cui.CuiWhichArea, "marked")
    for leg in marked_legs:
        Cui.CuiSetSelectionObject(Cui.gpc_info, Cui.CuiWhichArea, Cui.LegMode, str(leg))
        crewid = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object",'crew.%id%')
        udor = Cui.CuiCrcEvalAbstime(Cui.gpc_info,Cui.CuiWhichArea,"object",'leg.%udor%')
        flight_descriptor = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "leg.%flight_descriptor%")
        airport = Cui.CuiCrcEvalString(Cui.gpc_info, Cui.CuiWhichArea, "object", "leg.%start_station%")
        remove_in_charge_for_this_flight( AbsTime.AbsTime(udor), flight_descriptor, airport)
        Attributes.SetCrewFlightDutyAttr(crewid, udor, flight_descriptor, airport, "IN_CHARGE", refresh=True, str="C")

