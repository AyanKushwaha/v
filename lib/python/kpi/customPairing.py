from collections import defaultdict

import carmensystems.kpi as kpi
import carmensystems.rave.api as rave
import AbsTime
import RelTime
import carmusr.fatigue.kpi as fatigue_kpi
import carmusr.calibration.rule_kpis as calib_rule_kpi
import carmensystems.studio.private.teaming.teaming as teaming

class CustomKPI(kpi.KPI):

    def create(self):
	if calib_rule_kpi.use_only_these_kpis_for_legs_or_acrots(self, add_matrix=True, add_vectors=True):
            return
        # Get the planning objects to generate KPIs for
        bags = self.get_bags()
        trips_bag = bags['trips']

        self.bases = sorted(rave.set("active_bases").members())

        self.add(kpi.KpiValue("Duty days", 		trips_bag.kpi.sum_duty_days()))
        self.add(kpi.KpiValue("Avg. BLH per day", 	trips_bag.kpi.avg_block_per_day()))
        self.add(kpi.KpiValue("Avg. duty time per day",	trips_bag.kpi.avg_duty_per_day()))
        self.add(kpi.KpiValue("Deadhead time", 		trips_bag.kpi.sum_deadhead_time()))
        self.add(kpi.KpiValue("AC BLH",			trips_bag.kpi.ac_block_time()))
        self.add(kpi.KpiValue("Crew BLH", 		trips_bag.kpi.sum_crew_block()))
        self.add(kpi.KpiValue("Airport hotels",		trips_bag.kpi.sum_airport_hotels()))
        self.add(kpi.KpiValue("City hotels",		trips_bag.kpi.sum_city_hotels()))
        self.add(kpi.KpiValue("Short stops",		trips_bag.kpi.sum_short_stops()))
        self.add(kpi.KpiValue("Extended duties",	trips_bag.kpi.sum_extensions()))
        self.add(kpi.KpiValue("Duty days cost",		trips_bag.kpi.sum_duty_day_cost()))
        self.add(kpi.KpiValue("Hotel cost",		trips_bag.kpi.sum_hotel_cost()))
        self.add(kpi.KpiValue("Per diem cost",		trips_bag.kpi.sum_per_diem_cost()))
        self.add(kpi.KpiValue("Passive cost",        	trips_bag.kpi.sum_passive_cost()))
        self.add(kpi.KpiValue("Local transport cost",	trips_bag.kpi.sum_transport_cost()))
        self.add(kpi.KpiValue("Total Real cost",        trips_bag.kpi.sum_total_real_cost()))
        self.add(kpi.KpiValue("Sensitivity index (SI)", trips_bag.kpi.sum_sensitivity_index()))
        self.add(kpi.KpiValue("Calibration penalty",	trips_bag.kpi.sum_penalty_calibration()))
        self.add(kpi.KpiValue("Total cost (without SI cost)",      trips_bag.kpi.sum_total_cost_excl_si()))
 

        self.add(kpi.KpiValue("Number of Shift Changes", trips_bag.kpi.sum_shift_changes()))
        shift_change_trip_length = trips_bag.shift_change.minimum_days_to_check()
        self.add(kpi.KpiValue("Number of Shift Changes ({0}+ day trip)".format(shift_change_trip_length),
                              trips_bag.kpi.sum_shift_changes_checked()))
        self.add(kpi.KpiValue("Number of Excess Shift Changes", trips_bag.kpi.sum_excess_shift_changes()))
        self.add(kpi.KpiValue("Calibration: Violations of the minimum connection rule", trips_bag.kpi.total_connection_violations()))
        self.add(kpi.KpiValue("Calibration: Time overshooting the minimum connection rule", trips_bag.kpi.total_connection_overshooting_time()))
        self.add(kpi.KpiVector("Duties close to min Rest", DutiesCloseToLimit(trips_bag,'kpi.%time_above_min_rest_after_dp%').get_kpi_data(),
                               "Time","No of Duties"))
        self.add(kpi.KpiVector("Duties close to max FDP", DutiesCloseToLimit(trips_bag,'kpi.time_under_max_fdp').get_kpi_data(),
                               "Time","No of Duties"))
        self.add(kpi.KpiVector("AC changes", ShortACChanges(trips_bag).get_kpi_data(),
                               "Time","No of AC changes"))
        self.add(kpi.KpiMatrix("Trip length", 
                              TripDutyDaysDistributionPerBase(trips_bag).get_kpi_data(),
                              "No days", "Bases", "No of Trips"
                              ))

        self.add(fatigue_kpi.get_fatigue_kpis(trips_bag))
        
        calib_rule_kpi.add_kpis(self, trips_bag, add_matrix=True, add_vectors=True)
        teaming.add_teaming_kpi_to_report(self, trips_bag, kpi)

class Table(object):
    
    No_of_rows = 3
    
    def dictionary_of_zeros(self):
        dictionary = {}
        for index in xrange(self.No_of_rows):
            dictionary[index] = 0
        return dictionary


class ShortACChanges(Table):
    '''
    Sorts the AC-Changes into a table according to how long it is
    '''
    
    def __init__(self,trip_bag):
        self._data = self._calc_data(trip_bag)
        
    def get_kpi_data(self):
        no_in_each_margin = self.dictionary_of_zeros()
        for time in self._data:
            if int(time) >= 75:                 #75 minutes
                no_in_each_margin[2] += 1
            else:
                interval_index = int(time)/45   #45 minutes
                no_in_each_margin[interval_index] += 1
        result = []
        for key in no_in_each_margin.keys():
            if key == 0:
                time_interval_str = '00:00 - 00:44'
            elif key == 1:
                time_interval_str = '00:45 - 01:14'
            elif key == 2:
                time_interval_str = '01:15 +'
            result.append((time_interval_str,no_in_each_margin[key]))
        result.append(('Total',sum(no_in_each_margin.values())))
        return result
    
    def _calc_data(self,bag):
        ac_changes_list = []
        for trip_bag in bag.iterators.trip_set():
            for leg_bag in trip_bag.iterators.leg_set(where="leg.%is_ac_change% and duty.%is_short_ac_change%"):
                no_assigned_on_leg, = rave.eval(leg_bag,'crew_pos.leg_assigned')
                ac_change_time, = rave.eval(leg_bag,'kpi.ac_change_time')
                if (ac_change_time is not None) and (ac_change_time >= RelTime.RelTime("0:00")):
                    for _ in xrange(no_assigned_on_leg):
                        ac_changes_list.append(ac_change_time)
        return ac_changes_list

class DutiesCloseToLimit(Table):
    ''' 
    Used to show the Number of duties close to a min/max rule
    '''
    
    def __init__(self,trip_bag,variable):
        self.interval_size = 15
        self.No_of_rows = 4
        self._data = self._calc_data(trip_bag,variable)

    def get_kpi_data(self):
        no_in_each_margin = self.dictionary_of_zeros()
        broken_rule_counter = 0
        for time in self._data:
            if int(time) < 0:
                broken_rule_counter += 1
            else:
                interval_index = int(time) / self.interval_size
                no_in_each_margin[interval_index] += 1
        result = []
        result.append(('Rule broken', broken_rule_counter))
        for key in no_in_each_margin.keys():
            start_int = RelTime.RelTime(key * self.interval_size)
            end_int = RelTime.RelTime((key + 1) * self.interval_size - 1)
            time_interval_str = str(start_int) + ' - ' + str(end_int)
            result.append((time_interval_str, no_in_each_margin[key]))
        return result

    def _calc_data(self,bag,variable):
        time_from_limit_list = []
        for trip_bag in bag.iterators.trip_set():
            no_assigned_on_trip, = rave.eval(trip_bag,'crew_pos.trip_assigned')
            for duty_bag in trip_bag.iterators.duty_set():
                time_from_limit, = rave.eval(duty_bag,variable)
                if time_from_limit is not None and int(time_from_limit) < self.No_of_rows*self.interval_size:
                    for _ in xrange(no_assigned_on_trip):
                        time_from_limit_list.append(time_from_limit)
        return time_from_limit_list


class TripDutyDaysDistributionPerBase(object):
    ''' Used to show the trip length per Base in a KpiMatrix '''

    def __init__(self, trips_bag):
        self.trip_days_range = self._calc_trip_days_range(trips_bag)
        self.base_set = set()   #Fills in _calc_data()
        self._data = self._calc_data(trips_bag)

    def get_kpi_data(self):
        trip_length_list = []
        for day in self.trip_days_range:
            for base in self.base_set:
                if self._data[(day, base)]:
                    trip_length_list.append((("{}".format(day), "{}".format(base)),
                                             self._data[(day, base)]))
        return trip_length_list

    def _calc_trip_days_range(self,bag):
        longest_trip = 0        
        for trip_bag in bag.iterators.trip_set():
            num_days = trip_bag.trip.days()
            if num_days > longest_trip:
                longest_trip = num_days
        return xrange(1,longest_trip+1)
            
    def _calc_data(self, bag):
        _data = defaultdict(int)
        
        for trip_bag in bag.iterators.trip_set():
            if trip_bag.trip.starts_in_pp():
                base = trip_bag.trip.homebase()
                self.base_set.add(base)
                num_days = trip_bag.trip.days()
                _data[(num_days, base)] += 1

        for day in self.trip_days_range:
            total_trips_this_day = 0
            for base in self.base_set:
                total_trips_this_day += _data[(day, base)]
            _data[(day,'Total No Trips')] = total_trips_this_day
        self.base_set.add('Total No Trips') 
        return _data
        

# If run from Admin Tools > Python File Manager in Studio
if __name__ == '__main__':
 
    # For debugging in Studio.
    # Uses the Studio window where the cursor was last in as default_context.
    # Shows xml output in a text message window.
    # Prints xml output to a file, and shows it in the log.
        
    import os
 
    import Cui
    from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
 
    import carmstd.cfh_extensions as cfhe
 
    # Activate the default_context
    CuiContextLocator(Cui.CuiWhichArea, "window").reinstate()
 
    # Show the xml result on screen
    # Note: will wait for [Ok] to be pressed
    cfhe.show(kpi.getKPI('customPairing'))
 
    # Print the xml result on file
    kpi_file = '/tmp/KpiTempFile.xml'
    kpi.writeKPI('customPairing', kpi_file)
 
    # Show xml result in log
    os.system('cat %s' % kpi_file)
 
    os.unlink(kpi_file)

