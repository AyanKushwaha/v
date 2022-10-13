#!/bin/env python
# -*- coding: latin-1 -*-
# extracted from DAVE rtl_test at 2007-06-13 

"""
provide specific aradiff model and match type initialization
use aradiff -t <this python module> ...
"""

import os
from carmensystems.daveloadtools.ara import AraModel, AraNode
from carmensystems.daveloadtools.ara import AraMatchConfig

def defaultConfig():
    cfg = AraMatchConfig.AraMatchConfig()
    cfg.selectBy(1,"period_start","date")
    cfg.selectBy(2,"period_end","date")

    # register matching of aircraft
    #comp = cfg.compare("aircraft")
    #comp.action("insert")
    #comp.action("update")

    # register matching of crew
    #comp = cfg.compare("crew")
    #comp.action("insert")
    #comp.action("update")

    # register matching of flight_leg
    #comp = cfg.compare("flight_leg")
    #comp.action("insert")
    #comp.action("update")
    #comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    #matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "sibt", {'tolabs': '1:00'})
    #matchIt.matchField( "match", "udor", {})
    #matchIt.matchField( "match", "sobt", {'tolabs': '1:00'})
    #matchIt.matchField( "match", "fd", {'sublen': '9'})
    #comp.addRule(matchIt)

    # register matching of ground_task
    comp = cfg.compare("ground_task", allowPK=False, uuidField="id")
    comp.action("insert")
    comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 ")
    #comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 and \
    #      not exists (select * from crew_ground_duty where \
    #                           task_udor=udor and task_id=id and \
    #                           next_revid=0 and deleted='N') and \
    #      exists (select * from ground_task_attr gta where \
    #                           task_udor=udor and task_id=id and \
    #                           attr='OAAID' and next_revid=0 and deleted='N')")

    #comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 and \
    #      exists (select * from ground_task_attr gta where \
    #                           task_udor=udor and task_id=id and \
    #                           attr='OAAID' and next_revid=0 and deleted='N')")

    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 and \
          activity in (select id from activity_set where grp in ('OPC/OTS','ASF','AST', 'FFS', 'SIM') and \
                                    statcode<>'C' and \
                        ((substr(id,2,1) in ('1','2','3','4','5','6','7','8','9','0') and substr(id, 2,1)<> '7') or \
                        (substr(id,2,1) not in ('1','2','3','4','5','6','7','8','9','0') and \
                        (length(id)<3 or substr(id, 3,1)<> '7'))) \
                        and next_revid=0 and deleted='N') \
                        and id= \
                        (select max(id) from ground_task g2 where ground_task_0.activity=g2.activity and \
                         ground_task_0.udor=g2.udor and ground_task_0.st=g2.st and ground_task_0.et=g2.et and \
                         ground_task_0.adep=g2.adep and ground_task_0.ades=g2.ades and \
                         g2.next_revid=0 and g2.deleted='N')")

    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "adep", {})
    matchIt.matchField( "match", "udor", {})
    matchIt.matchField( "match", "st", {})
    matchIt.matchField( "match", "activity", {})
    matchIt.matchField( "match", "et", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    comp.addRule(matchIt)

    #matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "udor", {})
    #matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    #matchIt.matchField( "match", "activity", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    #comp.addRule(matchIt)

    # register matching of rotation
    #RTL comp = cfg.compare("rotation", allowPK=False, uuidField="id")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2")

    #RTL matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    #RTL matchIt.matchField( "match", "si", {})
    #RTL comp.addRule(matchIt)

    # register matching of ground_task_attr
    comp = cfg.compare("ground_task_attr")
    comp.action("insert")
    comp.action("update")
    comp.action("delete")
    comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2 and $.attr='OAAID' and \
          exists (select * from ground_task g1 where task_id=id and task_udor=udor and \
          activity in (select id from activity_set where grp in ('OPC/OTS','ASF','AST', 'FFS', 'SIM') and \
                        ((substr(id,2,1) in ('1','2','3','4','5','6','7','8','9','0') and substr(id, 2,1)<> '7') or \
                        (substr(id,2,1) not in ('1','2','3','4','5','6','7','8','9','0') and \
                        (length(id)<3 or substr(id, 3,1)<> '7'))) \
                        and next_revid=0 and deleted='N') and statcode<>'C' and next_revid=0 and deleted='N'  \
                        and id= \
                        (select max(id) from ground_task g2 where g1.activity=g2.activity and \
                         g1.udor=g2.udor and g1.st=g2.st and g1.et=g2.et and \
                         g1.adep=g2.adep and g1.ades=g2.ades and \
                         g2.next_revid=0 and g2.deleted='N'))")



    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "task_udor", {})
    matchIt.matchField( "match", "task_id", {})
    matchIt.matchField( "match", "attr", {})
    comp.addRule(matchIt)
    # register matching of rotation_ground_duty
    #RTL comp = cfg.compare("rotation_ground_duty")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")

    # register matching of rotation_flight_duty
    #RTL comp = cfg.compare("rotation_flight_duty")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of crew_need_exception
    #RTL comp = cfg.compare("crew_need_exception")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.flight_udor >= %:1 and $.flight_udor <= %:2")

    # register matching of flight_leg_delay
    #RTL comp = cfg.compare("flight_leg_delay")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of flight_leg_message
    #RTL comp = cfg.compare("flight_leg_message")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of flight_leg_pax
    #RTL comp = cfg.compare("flight_leg_pax")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of trip
    comp = cfg.compare("trip", allowPK=False, uuidField="id")
    comp.action("insert")
    comp.action("update")
    #comp.action("delete")

    #comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 and ($.adhoc like 'OAA%' or \
    #       exists (select * from trip_ground_duty, ground_task_attr where trip_id=id and \
    #               trip_ground_duty.task_id = ground_task_attr.task_id and $.udor=ground_task_attr.task_udor and ground_task_attr.attr='OAAID' \
    #               and ground_task_attr.next_revid=0 and ground_task_attr.deleted='N'))")

    comp.selectBy(['period_start','period_end'],"$.udor >= %:1 and $.udor <= %:2 and \
           exists (select * from trip_ground_duty, ground_task where trip_id=$.id and \
                   trip_ground_duty.task_id = ground_task.id and $.udor=ground_task.udor and ground_task.activity in \
                   (select id from activity_set where grp in ('OPC/OTS','ASF','AST', 'FFS', 'SIM') and \
                        ((substr(id,2,1) in ('1','2','3','4','5','6','7','8','9','0') and substr(id, 2,1)<> '7') or \
                        (substr(id,2,1) not in ('1','2','3','4','5','6','7','8','9','0') and \
                        (length(id)<3 or substr(id, 3,1)<> '7'))) and \
                                    next_revid=0 and deleted='N') \
                   and ground_task.next_revid=0 and ground_task.deleted='N')")

    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "udor", {})
    matchIt.matchField( "match", "base", {})
    #matchIt.matchField( "match", "adhoc", {})
    comp.addRule(matchIt)

    # register matching of trip_activity
    #comp = cfg.compare("trip_activity")
    #comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2")

    # register matching of trip_ground_duty
    comp = cfg.compare("trip_ground_duty")
    #comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2 and \
    #       exists (select * from ground_task_attr where \
    #               $.task_id = ground_task_attr.task_id and $.task_udor=ground_task_attr.task_udor and ground_task_attr.attr='OAAID' \
    #               and ground_task_attr.next_revid=0 and ground_task_attr.deleted='N')")

    comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2 and \
           exists (select * from ground_task where \
                   $.task_id = ground_task.id and $.task_udor=ground_task.udor and ground_task.activity in \
                   (select id from activity_set where grp in ('OPC/OTS','ASF','AST', 'FFS', 'SIM') and \
                        ((substr(id,2,1) in ('1','2','3','4','5','6','7','8','9','0') and substr(id, 2,1)<> '7') or \
                        (substr(id,2,1) not in ('1','2','3','4','5','6','7','8','9','0') and \
                        (length(id)<3 or substr(id, 3,1)<> '7'))) and \
                                    next_revid=0 and deleted='N') \
                   and ground_task.next_revid=0 and ground_task.deleted='N')")

    matchIt = AraMatchConfig.AraNodeMatchingRule(0)
    matchIt.matchField( "match", "trip_udor", {})
    matchIt.matchField( "match", "task_udor", {})
    matchIt.matchField( "match", "base", {})
    comp.addRule(matchIt)

    # register matching of trip_flight_duty
    #comp = cfg.compare("trip_flight_duty")
    #comp.selectBy(['period_start','period_end'],"$.trip_udor >= %:1 and $.trip_udor <= %:2")

    # register matching of aircraft_activity
    #comp = cfg.compare("aircraft_activity")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.st >= %:1* 1440 and $.st <= (%:2 +1)* 1440")

    #matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "st", {})
    #matchIt.matchField( "match", "activity", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    #comp.addRule(matchIt)

    #matchIt = AraMatchConfig.AraNodeMatchingRule(2)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    #matchIt.matchField( "match", "activity", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    #comp.addRule(matchIt)

    # register matching of aircraft_flight_duty
    #RTL comp = cfg.compare("aircraft_flight_duty")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of aircraft_ground_duty
    #RTL comp = cfg.compare("aircraft_ground_duty")
    #RTL comp.action("insert")
    #RTL comp.action("update")
    #RTL comp.action("delete")
    #RTL comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")

    # register matching of sched_ac_flight_duty
    #comp = cfg.compare("sched_ac_flight_duty")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of crew_landing
    #comp = cfg.compare("crew_landing")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")

    # register matching of crew_rest
    #comp = cfg.compare("crew_rest")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.flight_udor >= %:1 and $.flight_udor <= %:2")

    # register matching of crew_flight_duty
    #comp = cfg.compare("crew_flight_duty")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2")
    #comp.selectBy(['period_start','period_end'],"$.leg_udor >= %:1 and $.leg_udor <= %:2 and $.crew like '101%'")

    # register matching of crew_flight_attr
    #comp = cfg.compare("crew_flight_attr")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.flight_udor >= %:1 and $.flight_udor <= %:2")

    # register matching of passive_booking
    #comp = cfg.compare("passive_booking")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.flight_udor >= %:1 and $.flight_udor <= %:2")

    # register matching of crew_activity
    #comp = cfg.compare("crew_activity")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.st >= %:1* 1440 and $.st <= (%:2 +1)* 1440")

    #matchIt = AraMatchConfig.AraNodeMatchingRule(1)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "st", {})
    #matchIt.matchField( "match", "activity", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    #comp.addRule(matchIt)

    #matchIt = AraMatchConfig.AraNodeMatchingRule(2)
    #matchIt.matchField( "match", "adep", {})
    #matchIt.matchField( "match", "st", {'tolabs': '1:00'})
    #matchIt.matchField( "match", "activity", {})
    #matchIt.matchField( "match", "et", {'tolabs': '1:00'})
    #comp.addRule(matchIt)

    # register matching of crew_ground_duty
    #comp = cfg.compare("crew_ground_duty")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2")
    #comp.selectBy(['period_start','period_end'],"$.task_udor >= %:1 and $.task_udor <= %:2 and \
    #       exists (select * from ground_task where \
    #               $.task_id = ground_task.id and $.task_udor=ground_task.udor and ground_task.activity in \
    #               (select id from activity_set where grp in ('OPC/OTS','ASF','AST', 'FFS') and \
    #                                next_revid=0 and deleted='N') \
    #               and ground_task.next_revid=0 and ground_task.deleted='N')")

    # register matching of crew_flight_base_break
    #comp = cfg.compare("crew_flight_base_break")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.crew_duty_leg_udor >= %:1 and $.crew_duty_leg_udor <= %:2")

    # register matching of aircraft_connection
    #comp = cfg.compare("aircraft_connection")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.legfrom_udor >= %:1 and $.legfrom_udor <= %:2")

    # register matching of meal_order_line
    #comp = cfg.compare("meal_order_line")
    #comp.action("insert")
    #comp.action("update")
    #comp.action("delete")
    #comp.selectBy(['period_start','period_end'],"$.load_flight_udor >= %:1 and $.load_flight_udor <= %:2")

    return cfg


def defaultModel():
    model = AraModel.AraModel()

    # register type aircraft
    nt1 = AraNode.AraType("aircraft","R")
    nt1.addProperty("id","S")
    nt1.addProperty("actype","S")
    nt1.addProperty("si","S")
    nt1.addProperty("altid","S")
    nt1.addProperty("nationality","S")
    nt1.addProperty("owner","S")
    nt1.addProperty("ilscat","S")
    nt1.addProperty("seatconfig","S")
    nt1.addProperty("st","A")
    nt1.addProperty("et","A")
    model.registerType(nt1)

    # register list type aircraft_list
    lt2 = AraNode.AraType("aircraft_list","L" )
    lt2.childTypes.append(nt1)
    lt2.addProperty("deltamode","B")
    model.registerType(lt2)

    # register type crew
    nt3 = AraNode.AraType("crew","R")
    nt3.addProperty("id","S")
    nt3.addProperty("empno","S")
    nt3.addProperty("sex","C")
    nt3.addProperty("birthday","D")
    nt3.addProperty("title","S")
    nt3.addProperty("name","S")
    nt3.addProperty("forenames","S")
    nt3.addProperty("logname","S")
    nt3.addProperty("si","S")
    nt3.addProperty("maincat","S")
    nt3.addProperty("bcity","S")
    nt3.addProperty("bstate","S")
    nt3.addProperty("bcountry","S")
    nt3.addProperty("alias","S")
    nt3.addProperty("employmentdate","D")
    nt3.addProperty("retirementdate","D")
    model.registerType(nt3)

    # register list type crew_list
    lt4 = AraNode.AraType("crew_list","L" )
    lt4.childTypes.append(nt3)
    lt4.addProperty("deltamode","B")
    model.registerType(lt4)

    # register type flight_leg
    nt5 = AraNode.AraType("flight_leg","A")
    nt5.addProperty("udor","D")
    nt5.addProperty("fd","S")
    nt5.addProperty("adep","S")
    nt5.addProperty("ades","S")
    nt5.addProperty("stc","C")
    nt5.addProperty("sobt","A")
    nt5.addProperty("sibt","A")
    nt5.addProperty("eobt","A")
    nt5.addProperty("eibt","A")
    nt5.addProperty("aobt","A")
    nt5.addProperty("aibt","A")
    nt5.addProperty("actype","S")
    nt5.addProperty("statcode","C")
    nt5.addProperty("aco","S")
    nt5.addProperty("cpe","S")
    nt5.addProperty("cae","S")
    nt5.addProperty("si","S")
    nt5.addProperty("seq","I")
    nt5.addProperty("altn1","S")
    nt5.addProperty("altn2","S")
    nt5.addProperty("altn3","S")
    nt5.addProperty("etot","A")
    nt5.addProperty("eldt","A")
    nt5.addProperty("atot","A")
    nt5.addProperty("aldt","A")
    nt5.addProperty("eades","S")
    nt5.addProperty("maxholdtime","R")
    nt5.addProperty("flightval","I")
    nt5.addProperty("ppax","S")
    nt5.addProperty("bpax","S")
    nt5.addProperty("locktype","S")
    nt5.addProperty("ruleexception","S")
    nt5.addProperty("opdefconstraint","S")
    nt5.addProperty("acver","S")
    model.registerType(nt5)

    # register list type flight_leg_list
    lt6 = AraNode.AraType("flight_leg_list","L" )
    lt6.childTypes.append(nt5)
    lt6.addProperty("period_start","D")
    lt6.addProperty("deltamode","B")
    lt6.addProperty("period_end","D")
    model.registerType(lt6)

    # register type ground_task
    nt7 = AraNode.AraType("ground_task","A")
    nt7.addProperty("udor","D")
    nt7.addProperty("id","U")
    nt7.addProperty("st","A")
    nt7.addProperty("et","A")
    nt7.addProperty("adep","S")
    nt7.addProperty("ades","S")
    nt7.addProperty("activity","S")
    nt7.addProperty("statcode","S")
    nt7.addProperty("si","S")
    model.registerType(nt7)

    # register list type ground_task_list
    lt8 = AraNode.AraType("ground_task_list","L" )
    lt8.childTypes.append(nt7)
    lt8.addProperty("period_start","D")
    lt8.addProperty("deltamode","B")
    lt8.addProperty("period_end","D")
    model.registerType(lt8)

    # register type rotation
    nt9 = AraNode.AraType("rotation","A")
    nt9.addProperty("udor","D")
    nt9.addProperty("id","U")
    nt9.addProperty("adhoc","S")
    nt9.addProperty("actype","S")
    nt9.addProperty("si","S")
    model.registerType(nt9)

    # register list type rotation_list
    lt10 = AraNode.AraType("rotation_list","L" )
    lt10.childTypes.append(nt9)
    lt10.addProperty("period_start","D")
    lt10.addProperty("deltamode","B")
    lt10.addProperty("period_end","D")
    model.registerType(lt10)

    # register type ground_task_attr
    nt11 = AraNode.AraType("ground_task_attr","E")
    nt11.refTypes["task"] = model.types["ground_task"]
    nt11.idRefs.append("task")
    nt11.addProperty("task_udor","D")
    nt11.addProperty("task_id","U")
    nt11.addProperty("attr","S")
    nt11.addProperty("value_rel","R")
    nt11.addProperty("value_abs","A")
    nt11.addProperty("value_int","I")
    nt11.addProperty("value_str","S")
    nt11.addProperty("si","S")
    model.registerType(nt11)

    # register type rotation_ground_duty
    nt12 = AraNode.AraType("rotation_ground_duty","E")
    nt12.refTypes["task"] = model.types["ground_task"]
    nt12.idRefs.append("task")
    nt12.refTypes["rot"] = model.types["rotation"]
    nt12.addProperty("task_udor","D")
    nt12.addProperty("task_id","U")
    nt12.addProperty("pos","S")
    nt12.addProperty("rot_udor","D")
    nt12.addProperty("rot_id","U")
    nt12.addProperty("si","S")
    nt12.addProperty("urmtrail","S")
    nt12.addProperty("annotation","S")
    nt12.addProperty("st","A")
    nt12.addProperty("et","A")
    nt12.addProperty("adep","S")
    nt12.addProperty("ades","S")
    model.registerType(nt12)

    # register list type ground_task_attr_list
    lt12 = AraNode.AraType("ground_task_attr_list","L" )
    lt12.childTypes.append(nt11)
    lt12.addProperty("period_start","D")
    lt12.addProperty("period_end","D")
    model.registerType(lt12)

    # register type rotation_flight_duty
    nt13 = AraNode.AraType("rotation_flight_duty","E")
    nt13.refTypes["rot"] = model.types["rotation"]
    nt13.refTypes["leg"] = model.types["flight_leg"]
    nt13.idRefs.append("leg")
    nt13.addProperty("leg_udor","D")
    nt13.addProperty("leg_fd","S")
    nt13.addProperty("leg_adep","S")
    nt13.addProperty("pos","S")
    nt13.addProperty("rot_udor","D")
    nt13.addProperty("rot_id","U")
    nt13.addProperty("si","S")
    nt13.addProperty("urmtrail","S")
    nt13.addProperty("annotation","S")
    nt13.addProperty("st","A")
    nt13.addProperty("et","A")
    nt13.addProperty("adep","S")
    nt13.addProperty("ades","S")
    model.registerType(nt13)

    # register type crew_need_exception
    nt14 = AraNode.AraType("crew_need_exception","E")
    nt14.refTypes["flight"] = model.types["flight_leg"]
    nt14.idRefs.append("flight")
    nt14.addProperty("flight_udor","D")
    nt14.addProperty("flight_fd","S")
    nt14.addProperty("flight_adep","S")
    nt14.addProperty("pos6","I")
    nt14.addProperty("pos7","I")
    model.registerType(nt14)

    # register type flight_leg_delay
    nt15 = AraNode.AraType("flight_leg_delay","E")
    nt15.refTypes["leg"] = model.types["flight_leg"]
    nt15.idRefs.append("leg")
    nt15.addProperty("leg_udor","D")
    nt15.addProperty("leg_fd","S")
    nt15.addProperty("leg_adep","S")
    nt15.addProperty("seq","U")
    nt15.addProperty("code","S")
    nt15.addProperty("subcode","S")
    nt15.addProperty("duration","S")
    nt15.addProperty("reasontext","S")
    model.registerType(nt15)

    # register type flight_leg_message
    nt16 = AraNode.AraType("flight_leg_message","E")
    nt16.refTypes["leg"] = model.types["flight_leg"]
    nt16.idRefs.append("leg")
    nt16.addProperty("leg_udor","D")
    nt16.addProperty("leg_fd","S")
    nt16.addProperty("leg_adep","S")
    nt16.addProperty("msgtype","S")
    nt16.addProperty("logtime","A")
    nt16.addProperty("msgtext","S")
    model.registerType(nt16)

    # register type flight_leg_pax
    nt17 = AraNode.AraType("flight_leg_pax","E")
    nt17.refTypes["leg"] = model.types["flight_leg"]
    nt17.idRefs.append("leg")
    nt17.addProperty("leg_udor","D")
    nt17.addProperty("leg_fd","S")
    nt17.addProperty("leg_adep","S")
    nt17.addProperty("svc","C")
    nt17.addProperty("ppax","I")
    nt17.addProperty("bpax","I")
    nt17.addProperty("apax","I")
    model.registerType(nt17)

    # register list type flight_leg_attr_list
    lt18 = AraNode.AraType("flight_leg_attr_list","L" )
    lt18.childTypes.append(nt13)
    lt18.childTypes.append(nt14)
    lt18.childTypes.append(nt15)
    lt18.childTypes.append(nt16)
    lt18.childTypes.append(nt17)
    lt18.addProperty("period_start","D")
    lt18.addProperty("period_end","D")
    model.registerType(lt18)

    # register type trip
    nt19 = AraNode.AraType("trip","T")
    nt19.addProperty("udor","D")
    nt19.addProperty("id","U")
    nt19.addProperty("adhoc","S")
    nt19.addProperty("base","S")
    nt19.addProperty("cc_0","I")
    nt19.addProperty("cc_1","I")
    nt19.addProperty("cc_2","I")
    nt19.addProperty("cc_3","I")
    nt19.addProperty("cc_4","I")
    nt19.addProperty("cc_5","I")
    nt19.addProperty("cc_6","I")
    nt19.addProperty("cc_7","I")
    nt19.addProperty("cc_8","I")
    nt19.addProperty("cc_9","I")
    nt19.addProperty("cc_10","I")
    nt19.addProperty("cc_11","I")
    nt19.addProperty("locktype","C")
    nt19.addProperty("si","S")
    nt19.addProperty("status","C")
    model.registerType(nt19)

    # register list type trip_list
    lt20 = AraNode.AraType("trip_list","L" )
    lt20.childTypes.append(nt19)
    lt20.addProperty("period_start","D")
    lt20.addProperty("period_end","D")
    model.registerType(lt20)

    # register type trip_activity
    nt21 = AraNode.AraType("trip_activity","P")
    nt19.childTypes.append(nt21)
    nt21.refTypes["trip"] = model.types["trip"]
    nt21.idRefs.append("trip")
    nt21.addProperty("trip_udor","D")
    nt21.addProperty("trip_id","U")
    nt21.addProperty("st","A")
    nt21.addProperty("activity","S")
    nt21.addProperty("base","S")
    nt21.addProperty("et","A")
    nt21.addProperty("adep","S")
    nt21.addProperty("ades","S")
    nt21.addProperty("locktype","C")
    nt21.addProperty("si","S")
    nt21.addProperty("urmtrail","S")
    nt21.addProperty("annotation","S")
    nt21.addProperty("bookref","S")
    model.registerType(nt21)

    # register type trip_ground_duty
    nt22 = AraNode.AraType("trip_ground_duty","S")
    nt19.childTypes.append(nt22)
    nt22.refTypes["task"] = model.types["ground_task"]
    nt22.idRefs.append("task")
    nt22.refTypes["trip"] = model.types["trip"]
    nt22.idRefs.append("trip")
    nt22.addProperty("trip_udor","D")
    nt22.addProperty("trip_id","U")
    nt22.addProperty("task_udor","D")
    nt22.addProperty("task_id","U")
    nt22.addProperty("base","S")
    nt22.addProperty("pos","S")
    nt22.addProperty("locktype","C")
    nt22.addProperty("si","S")
    nt22.addProperty("urmtrail","S")
    nt22.addProperty("annotation","S")
    nt22.addProperty("st","A")
    nt22.addProperty("et","A")
    nt22.addProperty("adep","S")
    nt22.addProperty("ades","S")
    model.registerType(nt22)

    # register type trip_flight_duty
    nt23 = AraNode.AraType("trip_flight_duty","S")
    nt19.childTypes.append(nt23)
    nt23.refTypes["trip"] = model.types["trip"]
    nt23.idRefs.append("trip")
    nt23.refTypes["leg"] = model.types["flight_leg"]
    nt23.idRefs.append("leg")
    nt23.addProperty("trip_udor","D")
    nt23.addProperty("trip_id","U")
    nt23.addProperty("leg_udor","D")
    nt23.addProperty("leg_fd","S")
    nt23.addProperty("leg_adep","S")
    nt23.addProperty("base","S")
    nt23.addProperty("pos","S")
    nt23.addProperty("locktype","C")
    nt23.addProperty("si","S")
    nt23.addProperty("urmtrail","S")
    nt23.addProperty("annotation","S")
    nt23.addProperty("st","A")
    nt23.addProperty("et","A")
    nt23.addProperty("adep","S")
    nt23.addProperty("ades","S")
    nt23.addProperty("bookref","S")
    model.registerType(nt23)

    # register type aircraft_activity
    nt24 = AraNode.AraType("aircraft_activity","P")
    nt24.refTypes["ac"] = model.types["aircraft"]
    nt24.idRefs.append("ac")
    nt24.refTypes["rot"] = model.types["rotation"]
    nt24.addProperty("st","A")
    nt24.addProperty("ac","S")
    nt24.addProperty("activity","S")
    nt24.addProperty("et","A")
    nt24.addProperty("adep","S")
    nt24.addProperty("ades","S")
    nt24.addProperty("rot_udor","D")
    nt24.addProperty("rot_id","U")
    nt24.addProperty("si","S")
    nt24.addProperty("urmtrail","S")
    nt24.addProperty("annotation","S")
    nt24.addProperty("actid","S")
    nt24.addProperty("est","A")
    nt24.addProperty("eet","A")
    nt24.addProperty("ast","A")
    nt24.addProperty("aet","A")
    nt24.addProperty("locktype","S")
    nt24.addProperty("ruleexception","S")
    nt24.addProperty("opdefconstraint","S")
    model.registerType(nt24)

    # register type aircraft_flight_duty
    nt25 = AraNode.AraType("aircraft_flight_duty","S")
    nt25.refTypes["ac"] = model.types["aircraft"]
    nt25.idRefs.append("ac")
    nt25.refTypes["rot"] = model.types["rotation"]
    nt25.refTypes["leg"] = model.types["flight_leg"]
    nt25.idRefs.append("leg")
    nt25.addProperty("leg_udor","D")
    nt25.addProperty("leg_fd","S")
    nt25.addProperty("leg_adep","S")
    nt25.addProperty("ac","S")
    nt25.addProperty("rot_udor","D")
    nt25.addProperty("rot_id","U")
    nt25.addProperty("pos","S")
    nt25.addProperty("si","S")
    nt25.addProperty("urmtrail","S")
    nt25.addProperty("annotation","S")
    nt25.addProperty("st","A")
    nt25.addProperty("et","A")
    nt25.addProperty("adep","S")
    nt25.addProperty("ades","S")
    model.registerType(nt25)

    # register type aircraft_ground_duty
    nt26 = AraNode.AraType("aircraft_ground_duty","S")
    nt26.refTypes["ac"] = model.types["aircraft"]
    nt26.idRefs.append("ac")
    nt26.refTypes["task"] = model.types["ground_task"]
    nt26.idRefs.append("task")
    nt26.refTypes["rot"] = model.types["rotation"]
    nt26.addProperty("task_udor","D")
    nt26.addProperty("task_id","U")
    nt26.addProperty("ac","S")
    nt26.addProperty("rot_udor","D")
    nt26.addProperty("rot_id","U")
    nt26.addProperty("si","S")
    nt26.addProperty("urmtrail","S")
    nt26.addProperty("annotation","S")
    nt26.addProperty("st","A")
    nt26.addProperty("et","A")
    nt26.addProperty("adep","S")
    nt26.addProperty("ades","S")
    model.registerType(nt26)

    # register type sched_ac_flight_duty
    nt27 = AraNode.AraType("sched_ac_flight_duty","S")
    nt27.refTypes["ac"] = model.types["aircraft"]
    nt27.idRefs.append("ac")
    nt27.refTypes["leg"] = model.types["flight_leg"]
    nt27.idRefs.append("leg")
    nt27.addProperty("leg_udor","D")
    nt27.addProperty("leg_fd","S")
    nt27.addProperty("leg_adep","S")
    nt27.addProperty("ac","S")
    nt27.addProperty("si","S")
    model.registerType(nt27)

    # register list type aircraft_assignments
    lt28 = AraNode.AraType("aircraft_assignments","L" )
    lt28.childTypes.append(nt24)
    lt28.childTypes.append(nt25)
    lt28.childTypes.append(nt26)
    lt28.childTypes.append(nt27)
    lt28.addProperty("period_start","D")
    lt28.addProperty("period_end","D")
    model.registerType(lt28)

    # register type crew_landing
    nt29 = AraNode.AraType("crew_landing","S")
    nt29.refTypes["crew"] = model.types["crew"]
    nt29.idRefs.append("crew")
    nt29.refTypes["leg"] = model.types["flight_leg"]
    nt29.idRefs.append("leg")
    nt29.addProperty("leg_udor","D")
    nt29.addProperty("leg_fd","S")
    nt29.addProperty("leg_adep","S")
    nt29.addProperty("crew","S")
    nt29.addProperty("airport","S")
    nt29.addProperty("nr_landings","I")
    nt29.addProperty("activ","B")
    model.registerType(nt29)

    # register type crew_rest
    nt30 = AraNode.AraType("crew_rest","S")
    nt30.refTypes["flight"] = model.types["flight_leg"]
    nt30.idRefs.append("flight")
    nt30.refTypes["crew"] = model.types["crew"]
    nt30.idRefs.append("crew")
    nt30.addProperty("crew","S")
    nt30.addProperty("flight_udor","D")
    nt30.addProperty("flight_fd","S")
    nt30.addProperty("flight_adep","S")
    nt30.addProperty("reststart","A")
    nt30.addProperty("restend","A")
    nt30.addProperty("si","S")
    model.registerType(nt30)

    # register type crew_flight_duty
    nt31 = AraNode.AraType("crew_flight_duty","S")
    nt31.refTypes["crew"] = model.types["crew"]
    nt31.idRefs.append("crew")
    nt31.refTypes["trip"] = model.types["trip"]
    nt31.refTypes["leg"] = model.types["flight_leg"]
    nt31.idRefs.append("leg")
    nt31.addProperty("leg_udor","D")
    nt31.addProperty("leg_fd","S")
    nt31.addProperty("leg_adep","S")
    nt31.addProperty("crew","S")
    nt31.addProperty("pos","S")
    nt31.addProperty("trip_udor","D")
    nt31.addProperty("trip_id","U")
    nt31.addProperty("locktype","C")
    nt31.addProperty("si","S")
    nt31.addProperty("urmtrail","S")
    nt31.addProperty("annotation","S")
    nt31.addProperty("st","A")
    nt31.addProperty("et","A")
    nt31.addProperty("adep","S")
    nt31.addProperty("ades","S")
    nt31.addProperty("personaltrip","U")
    nt31.addProperty("bookref","S")
    model.registerType(nt31)

    # register type crew_flight_attr
    # nt32 = AraNode.AraType("crew_flight_attr","S")
    # nt32.refTypes["flight"] = model.types["flight_leg"]
    # nt32.idRefs.append("flight")
    # nt32.refTypes["crew"] = model.types["crew"]
    # nt32.idRefs.append("crew")
    # nt32.addProperty("crew","S")
    # nt32.addProperty("flight_udor","D")
    # nt32.addProperty("flight_fd","S")
    # nt32.addProperty("flight_adep","S")
    # nt32.addProperty("attr","S")
    # model.registerType(nt32)

    # register type passive_booking
    nt34 = AraNode.AraType("passive_booking","S")
    nt34.refTypes["flight"] = model.types["flight_leg"]
    nt34.idRefs.append("flight")
    nt34.refTypes["crew"] = model.types["crew"]
    nt34.idRefs.append("crew")
    nt34.addProperty("crew","S")
    nt34.addProperty("flight_udor","D")
    nt34.addProperty("flight_fd","S")
    nt34.addProperty("flight_adep","S")
    nt34.addProperty("typ","C")
    nt34.addProperty("book_class","C")
    nt34.addProperty("cancelled","B")
    nt34.addProperty("sent","B")
    model.registerType(nt34)

    # register type crew_activity
    nt35 = AraNode.AraType("crew_activity","P")
    nt35.refTypes["trip"] = model.types["trip"]
    nt35.refTypes["crew"] = model.types["crew"]
    nt35.idRefs.append("crew")
    nt35.addProperty("st","A")
    nt35.addProperty("crew","S")
    nt35.addProperty("activity","S")
    nt35.addProperty("et","A")
    nt35.addProperty("adep","S")
    nt35.addProperty("ades","S")
    nt35.addProperty("trip_udor","D")
    nt35.addProperty("trip_id","U")
    nt35.addProperty("locktype","C")
    nt35.addProperty("si","S")
    nt35.addProperty("urmtrail","S")
    nt35.addProperty("annotation","S")
    nt35.addProperty("personaltrip","U")
    nt35.addProperty("bookref","S")
    model.registerType(nt35)

    # register type crew_ground_duty
    nt36 = AraNode.AraType("crew_ground_duty","S")
    nt36.refTypes["task"] = model.types["ground_task"]
    nt36.idRefs.append("task")
    nt36.refTypes["trip"] = model.types["trip"]
    nt36.refTypes["crew"] = model.types["crew"]
    nt36.idRefs.append("crew")
    nt36.addProperty("task_udor","D")
    nt36.addProperty("task_id","U")
    nt36.addProperty("crew","S")
    nt36.addProperty("pos","S")
    nt36.addProperty("trip_udor","D")
    nt36.addProperty("trip_id","U")
    nt36.addProperty("locktype","C")
    nt36.addProperty("si","S")
    nt36.addProperty("urmtrail","S")
    nt36.addProperty("annotation","S")
    nt36.addProperty("st","A")
    nt36.addProperty("et","A")
    nt36.addProperty("adep","S")
    nt36.addProperty("ades","S")
    nt36.addProperty("personaltrip","U")
    model.registerType(nt36)

    # register list type crew_assignments
    lt37 = AraNode.AraType("crew_assignments","L" )
    lt37.childTypes.append(nt29)
    lt37.childTypes.append(nt30)
    lt37.childTypes.append(nt31)
    #lt37.childTypes.append(nt32)
    lt37.childTypes.append(nt34)
    lt37.childTypes.append(nt35)
    lt37.childTypes.append(nt36)
    lt37.addProperty("period_start","D")
    lt37.addProperty("period_end","D")
    model.registerType(lt37)

    # register type crew_flight_base_break
    #nt38 = AraNode.AraType("crew_flight_base_break","E")
    #nt38.refTypes["crew_duty"] = model.types["crew_flight_duty"]
    #nt38.idRefs.append("crew_duty")
    #nt38.addProperty("crew_duty_leg_udor","D")
    #nt38.addProperty("crew_duty_leg_fd","S")
    #nt38.addProperty("crew_duty_leg_adep","S")
    #nt38.addProperty("crew_duty_crew","S")
    #nt38.addProperty("last_in_trip","B")
    #nt38.addProperty("first_in_trip","B")
    #model.registerType(nt38)

    # register list type crew_flight_duty_attr_list
    lt39 = AraNode.AraType("crew_flight_duty_attr_list","L" )
    #lt39.childTypes.append(nt38)
    lt39.addProperty("period_start","D")
    lt39.addProperty("period_end","D")
    model.registerType(lt39)

    # register type aircraft_connection
    nt40 = AraNode.AraType("aircraft_connection","C")
    nt40.addProperty("legfrom_udor","D")
    nt40.addProperty("legfrom_fd","S")
    nt40.addProperty("legfrom_adep","S")
    nt40.addProperty("legto_udor","D")
    nt40.addProperty("legto_fd","S")
    nt40.addProperty("legto_adep","S")
    nt40.addProperty("si","S")
    model.registerType(nt40)

    # register list type aircraft_connection_list
    lt41 = AraNode.AraType("aircraft_connection_list","L" )
    lt41.childTypes.append(nt40)
    lt41.addProperty("period_start","D")
    lt41.addProperty("period_end","D")
    model.registerType(lt41)

    # register type meal_order_line
    nt42 = AraNode.AraType("meal_order_line","C")
    nt42.addProperty("order_order_number","I")
    nt42.addProperty("order_forecast","B")
    nt42.addProperty("load_flight_udor","D")
    nt42.addProperty("load_flight_fd","S")
    nt42.addProperty("load_flight_adep","S")
    nt42.addProperty("cons_flight_udor","D")
    nt42.addProperty("cons_flight_fd","S")
    nt42.addProperty("cons_flight_adep","S")
    nt42.addProperty("maincat","C")
    nt42.addProperty("meal_code","C")
    nt42.addProperty("amount","I")
    model.registerType(nt42)

    # register list type meal_order_line_list
    lt43 = AraNode.AraType("meal_order_line_list","L" )
    lt43.childTypes.append(nt42)
    lt43.addProperty("period_start","D")
    lt43.addProperty("period_end","D")
    model.registerType(lt43)

    return model



