# -*- coding: iso-8859-1 -*-

""" This a report the just extract variables from RAVE that concerns meal.
    The idea is that this report may be used before and after making a change in order to
    verify that only the wanted changes in meal code allocation has been done.

"""

import carmensystems.publisher.api as p
import carmensystems.rave.api as R

class Report(p.Report):
    """ This is the main class of the report """

    def create(self):
        """ This is the method called when a report is to be created """
        
        try:
            self.writeRosterInfo("SKN")
            self.writeRosterInfo("SKS")
            self.writeRosterInfo("SKD")
        except:
            import traceback
            traceback.print_exc()
            raise

    def writeRosterInfo(self, region):
        
        
        rosters_from_rave, = R.eval('sp_crew',
                                    R.foreach(R.iter('iterators.roster_set', 
                                                     where='crew_contract.%%region_at_plan_start%% = "%s"' % (region),
                                                     sort_by='crew.%id%'),
                                              'crew.%id%',
                                              'crew_contract.%region_at_plan_start%',
                                              'crew.%ce_is_pilot_in_pp%',
                                              'crew.%ce_is_cabin_in_pp%',
                                              R.foreach(R.iter('iterators.duty_set',
                                                               where='duty.%%region%% = "%s"' % (region)),
                                                        'duty.%has_active_flight%',
                                                        'meal.%duty_requires_two_meal_breaks%',
                                                        'meal.%two_required_meals_duty_time%',
                                                        'duty.%region%',
                                                        'report_common.%duty_duty_time%',
                                                        R.foreach(R.iter('iterators.leg_set'),
                                                                  'leg.%flight_descriptor%',
                                                                  'leg.%start_station%',
                                                                  'leg.%end_station%',
                                                                  'leg.%start_UTC%',
                                                                  'leg.%block_time%',
                                                                  'leg.%is_deadhead%',
                                                                  'meal.%leg_cnx_time%',
                                                                  'report_meal.%meal_code%',
                                                                  'report_meal.%consumption_code_normal%',
                                                                  'meal.%first_best_meal_break%',
                                                                  'meal.%second_best_meal_break%',
                                                                  'meal.%third_best_meal_break%',
                                                                  'meal.%leg_is_prevented_by_correction%',
                                                                  'report_meal.%update_load_time%',
                                                                  'report_meal.%update_load_stn%',
                                                                  'report_meal.%update_load_supplier_id%',
                                                                  'report_meal.%update_load_flight_nr%',
                                                                  'report_meal.%update_load_udor_str%',
                                                                  'rules_meal_ccp.%fail%',
                                                                  'meal.%meal_region%',
                                                                  'report_meal.%load_date%',
                                                                  'report_meal.%load_udor%',
                                                                  'report_meal.%load_flight_nr%', 
                                                                  'report_meal.%load_stn%',
                                                                  'report_meal.%load_supplier_id%'
                                                                  ))))
                                                        
                
        for (dummy, crew_id, crew_region, is_pilot, is_cabin, duties) in rosters_from_rave:

            if is_pilot:
                role = "Pilot"
            elif is_cabin:
                role = "Cabin"
            else:
                role = "Error, neither pilot of cabin"

            chain_structure = "Roster, %s, %s, %s\n" % (crew_id, crew_region, role)

            for (dummy, flight_duty, duty_req_two_meals, meal_duty_time, region, duty_time, legs) in duties:

                if not flight_duty:
                    continue
            
                chain_structure += " Duty, %s, %s, %s, %s\n" % (duty_req_two_meals, meal_duty_time, region, duty_time)

                for (dummy, fd, start_station, end_station, date, block_time, is_deadhead, cnx_time, code, cons_code, first, second, third, corr, up_load_time, up_load_stn, up_supplier, up_flight_nr, up_load_udor, 
                     rule_fail, region, load_date, load_udor, load_flight_nr, load_stn, load_supplier_id) in legs:
                    cnx_time = cnx_time or "N/A"
                    
                    chain_structure += "  Flight, %s, %s-%s, %s, %s, %s, %s, %s, Fail: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % \
                        (fd, start_station, end_station, date, block_time, cnx_time, code, cons_code, rule_fail, first, second, third,  corr,
                         up_load_time, up_load_stn, up_supplier, up_flight_nr, up_load_udor, region)
                    chain_structure += "Ordinary Load: %s, %s, %s, %s, %s\n" % (load_date, load_udor, load_flight_nr, load_stn, load_supplier_id)

            chain_info = p.Column()
            chain_info.add(p.Text(chain_structure))
            self.add(chain_info)

