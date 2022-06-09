#!/bin/env python


"""
SKCMS-921 Adding new parameters to period filter in order to stop cutting off trips that overlap the period end
"""


import adhoc.fixrunner as fixrunner


__version__ = '1'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    #Add trip and leg parameters to period filter
    ops.append(fixrunner.createop('dave_selparam', 'N', {'selection':'period', 'pind':8, 'name':'trip_start', 'dtype':'D', 'lbl':'Trip start date'}))
    ops.append(fixrunner.createop('dave_selparam', 'N', {'selection':'period', 'pind':9, 'name':'trip_end', 'dtype':'D', 'lbl':'Trip end date'}))
    ops.append(fixrunner.createop('dave_selparam', 'N', {'selection':'period', 'pind':10, 'name':'leg_start', 'dtype':'D', 'lbl':'Leg start date'}))
    ops.append(fixrunner.createop('dave_selparam', 'N', {'selection':'period', 'pind':11, 'name':'leg_end', 'dtype':'D', 'lbl':'Leg end date'}))

    #Modify relevant entity filters
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_aircraft_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_aircraft_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_aircraft_ground_duty', 'where_condition':'$.task_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_aircraft_ground_duty', 'where_condition':'$.task_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg', 'where_condition':'$.udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg_attr', 'where_condition':'$.leg_udor>=%:1 and $.leg_udor<=%2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg_attr', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip', 'where_condition':'$.udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_activity', 'where_condition':'$.trip_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_activity', 'where_condition':'$.trip_udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_flight_duty', 'where_condition':'$.trip_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_flight_duty', 'where_condition':'$.trip_udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_ground_duty', 'where_condition':'$.trip_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_trip_ground_duty', 'where_condition':'$.trip_udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_activity_connection', 'where_condition':'$.udor2 BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_activity_connection', 'where_condition':'$.udor2 BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_activity_group_period', 'where_condition':'$.validfrom<=%:4 and $.validto>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_activity_set_period', 'where_condition':'$.validfrom<=%:4 and $.validto>=%:3'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_adhoc_flight', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_adhoc_flight', 'where_condition':'$.udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_aircraft_activity', 'where_condition':'$.st<=%:4 and $.et>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_alert_time_exception', 'where_condition':'$.startdate>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_bought_days', 'where_condition':'$.start_time>=%:5 and $.start_time<=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_ci_frozen', 'where_condition':'$.dutystart>=(%:3-1440) and $.dutystart <=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_cio_event', 'where_condition':'$.ciotime>=%:3 and $.ciotime <=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_activity', 'where_condition':'$.st<=%:4 and $.et>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_activity_1', 'where_condition':'$.st<=%:4 and $.et>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_activity_attr_1', 'where_condition':None}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_base_break', 'where_condition':'$.st>=%:3 and $.st<=%:4'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ext_publication', 'where_condition':'$.udor>=%:1 and $.udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ext_publication', 'where_condition':'$.udor>=%:10 and $.udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_flight_duty_attr', 'where_condition':'$.cfd_leg_udor>=%:1 and $.cfd_leg_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_flight_duty_attr', 'where_condition':'$.cfd_leg_udor>=%:10 and $.cfd_leg_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ground_duty', 'where_condition':'$.task_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ground_duty', 'where_condition':'$.task_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ground_duty_attr', 'where_condition':'$.cgd_task_udor>=%:1 and $.cgd_task_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_ground_duty_attr', 'where_condition':'$.cgd_task_udor>=%:10 and $.cgd_task_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_landing', 'where_condition':'$.leg_udor>=%:1 and $.leg_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_landing', 'where_condition':'$.leg_udor>=%:10 and $.leg_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_log_acc', 'where_condition':'$.tim>=%:3 and $.tim<=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_log_acc_mod', 'where_condition':'$.tim>=%:3 - 1051200 and $.tim<=%:4'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_need_exception', 'where_condition':'$.flight_udor>=%:1 and $.flight_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_need_exception', 'where_condition':'$.flight_udor>=%:10 and $.flight_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_notification', 'where_condition':'($.st is null and $.deadline>=%:3) or ($.st is not null and $.st >=%:3)'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_oag_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_oag_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_passport', 'where_condition':'$.validto>=%:6 and $.validfrom<=%:7'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_publish_info', 'where_condition':'$.end_date>=%:1 and $.start_date<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_publish_info', 'where_condition':'$.end_date>=%:10 and $.start_date<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_rest', 'where_condition':'$.flight_udor>=%:1 and $.flight_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_rest', 'where_condition':'$.flight_udor>=%:10 and $.flight_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_training_log', 'where_condition':'$.tim>=%:5 and $.tim<=%:4'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_trip', 'where_condition':'$.trip_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_crew_trip', 'where_condition':'$.trip_udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_cs_flight_leg', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_cs_flight_leg', 'where_condition':'$.udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_do_not_publish', 'where_condition':'$.end_time>=%:3 and $.start_time<=%:4'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_equipment_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_equipment_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_equipment_ground_duty', 'where_condition':'$.task_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_equipment_ground_duty', 'where_condition':'$.task_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_est_filter_driver', 'where_condition':'$.validfrom <= %:2*1440 AND $.validto >= %:1*1440'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_est_std_paramtable', 'where_condition':'$.validfrom <= %:2*1440 AND $.validto >= %:1*1440'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_exchange_rate', 'where_condition':'$.validfrom<=%:4 and $.validto>=%:3'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg_pax', 'where_condition':'$.leg_udor>=%:1 and $.leg_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_flight_leg_pax', 'where_condition':'$.leg_udor>=%:10 and $.leg_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_ground_task', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_ground_task', 'where_condition':'$.udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_ground_task_attr', 'where_condition':'$.task_udor>=%:1 and $.task_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_ground_task_attr', 'where_condition':'$.task_udor>=%:10 and $.task_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_hotel_booking', 'where_condition':'$.checkout>=(%:1-1)'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_hotel_contract', 'where_condition':'$.validfrom<=%:4 and $.validto>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_informed', 'where_condition':'$.enddate>=%:3 and $.startdate<=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_meal_order', 'where_condition':'$.order_date>=%:1-30'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_meal_order_line', 'where_condition':None}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_meal_valid', 'where_condition':'$.crewflight_leg_udor>=%:1 AND $.crewflight_leg_udor<=%:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_meal_valid', 'where_condition':'$.crewflight_leg_udor>=%:10 AND $.crewflight_leg_udor<=%:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_oag_flight_leg', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_oag_flight_leg', 'where_condition':'$.udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_oag_ssim', 'where_condition':'$.bdor <= %:2 AND $.edor >= %:1'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_oag_ssim', 'where_condition':'$.bdor <= %:11 AND $.edor >= %:10'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_pairing_distribution', 'where_condition':'$.validfrom <= %:2*1440 AND $.validto >= %:1*1440'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_pairing_distribution', 'where_condition':'$.validfrom <= %:11*1440 AND $.validto >= %:10*1440'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_passive_booking', 'where_condition':'$.flight_udor>=(%:1-1)'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_preferred_hotel', 'where_condition':'$.validfrom<=%:4 and $.validto>=%:3'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_published_roster', 'where_condition':'$.pubstart<=%:7 and $.pubend>=%:6'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_published_standbys', 'where_condition':'$.sby_end>=%:3 and $.sby_start<=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_resource_def', 'where_condition':'$.validfrom <= %:2*1440 AND $.validto >= %:1*1440'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation', 'where_condition':'$.udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation', 'where_condition':'$.udor BETWEEN %:8 AND %:9'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation_activity', 'where_condition':'$.st<=%:4 and $.et>=%:3'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation_ground_duty', 'where_condition':'$.task_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rotation_ground_duty', 'where_condition':'$.task_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_rule_exception', 'where_condition':'$.starttime>=%:6 and $.starttime<=%:4'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_sched_ac_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:1 AND %:2'}))
    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_sched_ac_flight_duty', 'where_condition':'$.leg_udor BETWEEN %:10 AND %:11'}))

    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_spec_local_trans', 'where_condition':'(TO_DATE(REGEXP_SUBSTR($.leg,'[0-9]{2}[A-Za-z]{3}[0-9]{4}'))-TO_DATE('1JAN1986')) >= %:1'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_track_alert', 'where_condition':'$.exceptionstarttime>=%:6 and $.exceptionstarttime<=%:4'}))
    # ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'period_transport_booking', 'where_condition':'$.flight_day>=(%:1-1)'}))

    # sed expression to mangle input rows:
    # sed "s/\([^ ]*\) \([^ ]*\) \(.*\)/    ops.append(fixrunner.createop('dave_entity_filter', 'U', {'selection':'period', 'id':'\1', 'where_condition':'\3'}))/g"

    return ops


    """
period_activity_connection activity_connection $.udor2 BETWEEN %:1 AND %:2
period_activity_group_period activity_group_period $.validfrom<=%:4 and $.validto>=%:3
period_activity_set_period activity_set_period $.validfrom<=%:4 and $.validto>=%:3
period_adhoc_flight adhoc_flight $.udor BETWEEN %:1 AND %:2
period_aircraft_activity aircraft_activity $.st<=%:4 and $.et>=%:3
period_alert_time_exception alert_time_exception $.startdate>=%:3
period_bought_days bought_days $.start_time>=%:5 and $.start_time<=%:4
period_ci_frozen ci_frozen $.dutystart>=(%:3-1440) and $.dutystart <=%:4
period_cio_event cio_event $.ciotime>=%:3 and $.ciotime <=%:4
period_crew_activity crew_activity $.st<=%:4 and $.et>=%:3
period_crew_activity_1 crew_activity $.st<=%:4 and $.et>=%:3
period_crew_activity_attr_1 crew_activity_attr 
period_crew_base_break crew_base_break $.st>=%:3 and $.st<=%:4
period_crew_ext_publication crew_ext_publication $.udor>=%:1 and $.udor<=%:2
period_crew_flight_duty crew_flight_duty $.leg_udor BETWEEN %:1 AND %:2
period_crew_flight_duty_attr crew_flight_duty_attr $.cfd_leg_udor>=%:1 and $.cfd_leg_udor<=%:2
period_crew_ground_duty crew_ground_duty $.task_udor BETWEEN %:1 AND %:2
period_crew_ground_duty_attr crew_ground_duty_attr $.cgd_task_udor>=%:1 and $.cgd_task_udor<=%:2
period_crew_landing crew_landing $.leg_udor>=%:1 and $.leg_udor<=%:2
period_crew_log_acc crew_log_acc $.tim>=%:3 and $.tim<=%:4
period_crew_log_acc_mod crew_log_acc_mod $.tim>=%:3 - 1051200 and $.tim<=%:4
period_crew_need_exception crew_need_exception $.flight_udor>=%:1 and $.flight_udor<=%:2
period_crew_notification crew_notification ($.st is null and $.deadline>=%:3) or ($.st is not null and $.st >=%:3)
period_crew_oag_duty crew_oag_duty $.leg_udor BETWEEN %:1 AND %:2
period_crew_passport crew_passport $.validto>=%:6 and $.validfrom<=%:7
period_crew_publish_info crew_publish_info $.end_date>=%:1 and $.start_date<=%:2
period_crew_rest crew_rest $.flight_udor>=%:1 and $.flight_udor<=%:2
period_crew_training_log crew_training_log $.tim>=%:5 and $.tim<=%:4
period_crew_trip crew_trip $.trip_udor BETWEEN %:1 AND %:2
period_cs_flight_leg cs_flight_leg $.udor BETWEEN %:1 AND %:2
period_do_not_publish do_not_publish $.end_time>=%:3 and $.start_time<=%:4
period_equipment_flight_duty equipment_flight_duty $.leg_udor BETWEEN %:1 AND %:2
period_equipment_ground_duty equipment_ground_duty $.task_udor BETWEEN %:1 AND %:2
period_est_filter_driver est_filter_driver $.validfrom <= %:2*1440 AND $.validto >= %:1*1440
period_est_std_paramtable est_std_paramtable $.validfrom <= %:2*1440 AND $.validto >= %:1*1440
period_exchange_rate exchange_rate $.validfrom<=%:4 and $.validto>=%:3
period_flight_leg_pax flight_leg_pax $.leg_udor>=%:1 and $.leg_udor<=%:2
period_ground_task ground_task $.udor BETWEEN %:1 AND %:2
period_ground_task_attr ground_task_attr $.task_udor>=%:1 and $.task_udor<=%:2
period_hotel_booking hotel_booking $.checkout>=(%:1-1)
period_hotel_contract hotel_contract $.validfrom<=%:4 and $.validto>=%:3
period_informed informed $.enddate>=%:3 and $.startdate<=%:4
period_meal_order meal_order $.order_date>=%:1-30
period_meal_order_line meal_order_line 
period_meal_valid meal_valid $.crewflight_leg_udor>=%:1 AND $.crewflight_leg_udor<=%:2
period_oag_flight_leg oag_flight_leg $.udor BETWEEN %:1 AND %:2
period_oag_ssim oag_ssim $.bdor <= %:2 AND $.edor >= %:1
period_pairing_distribution pairing_distribution $.validfrom <= %:2*1440 AND $.validto >= %:1*1440
period_passive_booking passive_booking $.flight_udor>=(%:1-1)
period_preferred_hotel preferred_hotel $.validfrom<=%:4 and $.validto>=%:3
period_published_roster published_roster $.pubstart<=%:7 and $.pubend>=%:6
period_published_standbys published_standbys $.sby_end>=%:3 and $.sby_start<=%:4
period_resource_def resource_def $.validfrom <= %:2*1440 AND $.validto >= %:1*1440
period_rotation rotation $.udor BETWEEN %:1 AND %:2
period_rotation_activity rotation_activity $.st<=%:4 and $.et>=%:3
period_rotation_flight_duty rotation_flight_duty $.leg_udor BETWEEN %:1 AND %:2
period_rotation_ground_duty rotation_ground_duty $.task_udor BETWEEN %:1 AND %:2
period_rule_exception rule_exception $.starttime>=%:6 and $.starttime<=%:4
period_sched_ac_flight_duty sched_ac_flight_duty $.leg_udor BETWEEN %:1 AND %:2
period_spec_local_trans spec_local_trans (TO_DATE(REGEXP_SUBSTR($.leg,'[0-9]{2}[A-Za-z]{3}[0-9]{4}'))-TO_DATE('1JAN1986')) >= %:1
period_track_alert track_alert $.exceptionstarttime>=%:6 and $.exceptionstarttime<=%:4
period_transport_booking transport_booking $.flight_day>=(%:1-1)
"""




    return ops


if __name__ == '__main__':
    fixit.program = 'skcms_921_period_filter.py (%s)' % __version__
    fixit()
