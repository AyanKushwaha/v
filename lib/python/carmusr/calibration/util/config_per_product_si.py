'''
Created on 18 Dec 2020

@author: steham
'''

from collections import namedtuple

from carmusr.calibration import mappings


SIComponentDef = namedtuple("SIComponentDef", "name, level, calib_component_rule_ref, fallback")
SIFallbackDef = namedtuple("SIFallbackDef", "rule_name, rule_label, valid_str, lhs_str, rhs_str, rave_modules")

MIN_REST_TIME = SIComponentDef(name="min_rest_time",
                               level=mappings.LEVEL_DUTY,
                               calib_component_rule_ref='(Calib 2a)',
                               fallback=SIFallbackDef(rule_name="fallback",
                                                      rule_label="No min rest time rule registered",
                                                      valid_str="not is_last(duty(trip))",
                                                      lhs_str="next(duty(chain), first(leg(duty), departure)) - last(leg(duty), arrival)",
                                                      rhs_str="void_reltime",
                                                      rave_modules=set(["levels"])))

MIN_CONN_TIME = SIComponentDef(name="min_connection_time",
                               level=mappings.LEVEL_LEG,
                               calib_component_rule_ref='(Calib 1a)',
                               fallback=SIFallbackDef(rule_name="fallback",
                                                      rule_label="No min connection time rule registered",
                                                      valid_str="aircraft_change",
                                                      lhs_str="next(leg(duty), departure) - arrival",
                                                      rhs_str="void_reltime",
                                                      rave_modules=set(["levels"])))

MAX_DUTY_TIME = SIComponentDef(name="max_duty_time",
                               level=mappings.LEVEL_DUTY,
                               calib_component_rule_ref='(Calib 3a)',
                               fallback=SIFallbackDef(rule_name="fallback",
                                                      rule_label="No max duty time rule registered",
                                                      valid_str="any(leg(duty), flight_duty and not deadhead)",
                                                      lhs_str="last(leg(duty), arrival) - first(leg(duty), departure)",
                                                      rhs_str="void_reltime",
                                                      rave_modules=set(["levels"])))
