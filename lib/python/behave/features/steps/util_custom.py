"""
Values that may be customized

"""

pp_start_str = '01jan2018'
pp_end_str = '31jan2018'
handled_months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

homebases = ('OSL', 'ARN', 'CPH', 'SVG', 'TRD') 

crew_id = 'Crew'
# base needs to match active bases in BaseDefinitions file
crew_homebase = 'GOT'

trip_name = 'Trip'
# base needs to match active bases in BaseDefinitions file
trip_homebase = 'GOT'

activity_carrier = 'SK'
handled_carriers = ['SK']
activity_flight_num = 3711
activity_date_str = '20180126'
activity_stn1 = 'GOT'
activity_stn2 = 'ARN'

#
# mappings to carmusr
#

rule_set_rotations = 'BuildAcRotations'
rule_set_pairing_cc = 'Pairing_CC'
rule_set_pairing_fc = 'Pairing_FC'
rule_set_rostering_cc = 'Rostering_CC'
rule_set_rostering_fc = 'Rostering_FC'
rule_set_tracking = 'Tracking'

map_num_marked_trips = 'studio_sno.%num_marked_trips%'
map_num_marked_legs = 'studio_sno.%num_marked_legs%'

map_trip_set_iterator = 'iterators.trip_set'
