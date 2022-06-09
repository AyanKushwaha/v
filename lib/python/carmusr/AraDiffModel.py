import os
from carmensystems.daveloadtools.ara import AraModel, AraNode
from carmensystems.daveloadtools.ara import AraMatchConfig

import carmensystems.daveloadtools.ara.AraModelAir as AraModelAir

def defaultConfig():
#    cfg = AraModelAir.defaultConfig()
    cfg = AraMatchConfig.AraMatchConfig()
    cfg.selectBy(1,"period_start","date")
    cfg.selectBy(2,"period_end","date")

    # register matching of aircraft
    comp = cfg.compare("aircraft")
    comp.action("insert")
    comp.action("update")

    # register matching of crew
    comp = cfg.compare("crew")
    comp.action("insert")
    comp.action("update")

    # register matching of flight_leg
    comp = cfg.compare("flight_leg")
    comp.action("insert")
    comp.action("update")
    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "sibt", {'tolabs': '1:00'})
    matchIt.matchField( "match", "udor", {})
    matchIt.matchField( "match", "sobt", {'tolabs': '1:00'})
    matchIt.matchField( "match", "fd", {'sublen': '9'})
    comp.addRule(matchIt)

    # register matching of ground_task
    comp = cfg.compare("ground_task", allowPK=False, uuidField="id")
    comp.action("insert")
    comp.action("update")
    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "udor", {})
    matchIt.matchField( "match", "st", {})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "udor", {})
    matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)
    
    # register matching of rotation
    comp = cfg.compare("rotation")
    comp.action("insert")
    comp.action("update")
    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "si", {})
    comp.addRule(matchIt)

    # register matching of rotation_ground_duty
    comp = cfg.compare("rotation_ground_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")

    # register matching of rotation_flight_duty
    comp = cfg.compare("rotation_flight_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of trip
    comp = cfg.compare("trip", allowPK=False, uuidField="id")
    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    # register matching of trip_ground_duty
    comp = cfg.compare("trip_ground_duty")
    comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2")

    # register matching of trip_activity
    comp = cfg.compare("trip_activity")
    comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2")

    # register matching of trip_flight_duty
    comp = cfg.compare("trip_flight_duty")
    comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2")

    # register matching of sched_ac_flight_duty
    comp = cfg.compare("sched_ac_flight_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of aircraft_flight_duty
    comp = cfg.compare("aircraft_flight_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of aircraft_activity
    comp = cfg.compare("aircraft_activity")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.st >= %:1* 1440 and $.st <= (%:2 +1)* 1440")

    matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "st", {})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    matchIt = AraMatchConfig.AraNodeMatchingRule(2)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    # register matching of aircraft_ground_duty
    comp = cfg.compare("aircraft_ground_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")

    # register matching of crew_flight_duty
    comp = cfg.compare("crew_flight_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of crew_activity
    comp = cfg.compare("crew_activity")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.st >= %:1* 1440 and $.st <= (%:2 +1)* 1440")

    matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "st", {})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    matchIt = AraMatchConfig.AraNodeMatchingRule(2)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    # register matching of crew_ground_duty
    comp = cfg.compare("crew_ground_duty")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")

    # register matching of aircraft_connection
    comp = cfg.compare("aircraft_connection")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.legfrom_udor >= %:1 and $.legfrom_udor <= %:2")



    
    return cfg

def defaultModel():
    model = AraModelAir.defaultModel()
    return model 
