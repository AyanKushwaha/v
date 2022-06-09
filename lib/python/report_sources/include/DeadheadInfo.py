"""
 $Header$

 Deadhead Report

 Lists all deadheads and ground transports in the plan,
 if there any. Default time is Local Time and is changed
 by changing crg_deadhead.%time_mode%.

 Created:    2006-09-20
 By:         Jeppesen Systems AB

"""


# imports ================================================================{{{1
import carmensystems.rave.api as rave
from carmensystems.publisher.api import *
from report_sources.include.SASReport import SASReport


# constants =============================================================={{{1
CONTEXT = 'default_context'
TITLE = 'Deadhead Info'
NUM_LEGS_PER_SECTION = 5


# classes ================================================================{{{1

# DeadheadInfo------------------------------------------------------------{{{2
class DeadheadInfo(SASReport):
    """
    Create the report using the Python Publisher API.
    """

    def create(self):
        SASReport.create(self, TITLE, usePlanningPeriod=True)
        
        fontSizeHead = 9


        # Check if there are any deadheads or ground transports
        check = rave.eval(CONTEXT, 'not crg_deadhead.%any_deadheads% and not crg_deadhead.%any_ground_transports%')

        if check[0]:
            self.add(Row(Text('NO DEADHEADS REQUIRED')))
            self.add(Row(Text('NO GROUND TRANSPORTS REQUIRED')))

        else:
            # Deadheads
            #self.content('DH', fontSizeHead, fontSizeBody)
    
            # Ground transports
            #self.content('GT', fontSizeHead, fontSizeBody)        
        
            types = ['DH', 'GT']

            for positioningtype in types:
                
                # Create iterators to extract information from the plan
                carrier_iterator = rave.iter('iterators.flight_carrier_set',
                                             where='crg_deadhead.%any_of_this_positioning_type%(crg_deadhead.' + positioningtype + ')',
                                             sort_by='leg.%flight_carrier%')

                leg_details_iterator = rave.iter('iterators.unique_leg_set',
                                                 where='crg_deadhead.%is_this_positioning_type%(crg_deadhead.' + positioningtype + ')',
                                                 sort_by=('crg_deadhead.%leg_start%', 'leg.%flight_nr%'))

                
                if positioningtype == 'DH':
                    carrierhdrtext = 'Deadheads'
                else:
                    carrierhdrtext = 'Ground Transports'

                # Create a foreach object to find all deadhead legs divided by carrier
                fe = rave.foreach(carrier_iterator,
                                  'leg.%flight_carrier%',
                                  rave.foreach(leg_details_iterator,
                                               'leg.%flight_nr%',
                                               'crg_basic.%leg_number%',
                                               'crg_basic.%flight_suffix%',
                                               'aircraft_type',
                                               'crg_date.%print_date%(crg_deadhead.%leg_start%)',
                                               'crg_date.%print_time%(crg_deadhead.%leg_start%)',
                                               'leg.%start_station%',
                                               'leg.%end_station%',
                                               'crg_date.%print_time%(crg_deadhead.%leg_end%)',
                                               'crg_crew_pos.%leg_assigned_sum%(crg_crew_pos.AllCat, crg_crew_pos.SumLegSet)',
                                               'crg_crew_pos.%leg_assigned_vector%(crg_crew_pos.Cockpit, crg_crew_pos.SumLegSet)',
                                               'crg_crew_pos.%leg_assigned_vector%(crg_crew_pos.Cabin, crg_crew_pos.SumLegSet)',
                                               'crg_basic.%print_figure%(crg_deadhead.%total_crew_dh_cost_leg%)',
                                               'trip.%in_pp%'
                                               )
                                  )


                # Evaluate the foreach
                carriers, = rave.eval(CONTEXT, fe)

                # Loop over all carriers with deadheads
                carriercounter = 0
                for carrierlegs in carriers:
                    legs = carrierlegs[-1]
                    carrier = carrierlegs[1]
                                        
                    # Make every carrier begin on a new page
                    carriercounter += 1
                    if carriercounter > 1:
                        self.newpage()

                    # Create the carrier specific header
                    carrierhdr = Row(Text(carrierhdrtext + " with carrier %s" % carrier,
                                          align=LEFT,
                                          colspan=5,
                                          font=Font(weight=BOLD)
                                          ))
                    carrierhdr.set(font=Font(size=self.FONTSIZEHEAD, style=ITALIC))

                    # Set up list header
                    listhdr = self.getTableHeader(("Flight", "Eqp", "Date", "Departure/Arrival", "Required Seats", "Total Cost"))

                    # Add the header
                    hdr = Column(carrierhdr, listhdr)
                    self.add(hdr)

                    # Loop over all deadhead legs for this carrier and create and add rows
                    legcounter = 0
                    normalmargin = padding(top=2, left=2, bottom=2, right=2)
                    firstmargin = padding(top=5, left=2, bottom=2, right=2)
                    smallmargin = padding(top=0, left=0, bottom=0, right=0)
                    previousdate = ''

                    for leg in legs:
                        if leg[14]:
                            # Add a blank row every NUM_LEGS_PER_SECTION legs
                            #if legcounter > 0 and legcounter % NUM_LEGS_PER_SECTION == 0:
                            #    self.add(Row(smallmargin,""))
                            thisdate = leg[5]
                            if legcounter > 0:
                                # Add a blank row if this leg departs on a later date than
                                # the previous one
                                if thisdate <> previousdate:
                                    self.add(Row(Text("",padding=smallmargin)))
                                    self.page0()
                                thisPadding = normalmargin
                            else:
                                # The very first row gets a larger top margin to increase readability
                                thisPadding = firstmargin

                            flight = Text("%s %4.3i%s%s" % (carrier, leg[1], leg[2], leg[3]), padding=thisPadding)
                            equip = Text("%s" % leg[4], padding=thisPadding)
                            date = Text("%s" % leg[5], padding=thisPadding)
                            deparr = Text("%s %3s-%3s %s" % (leg[6], leg[7], leg[8], leg[9]), padding=thisPadding)
                            crew = Text("%2i [%s][%s]" % (leg[10], leg[11], leg[12]), padding=thisPadding)
                            cost = Text("%s" % leg[13], padding=thisPadding)

                            thisRow = Row(flight, equip, date, deparr, crew, cost)
                            self.add(thisRow)
                            #if legcounter == 0:
                            #    self.page0()

                            legcounter += 1
                            previousdate = thisdate

        # End of file

