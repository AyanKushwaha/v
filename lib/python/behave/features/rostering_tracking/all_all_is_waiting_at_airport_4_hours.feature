@TRACKING @ROSTERING
Feature: leg.%is_waiting_at_airport% should always return false in Rostering.

##########################
# JIRA - SKCMS-2278
##########################

  Background: set up

  @SCENARIO_1 @tracking
  Scenario: Crew are allowed to stand by at airport for more than 4 hours despite rule.
    Given Tracking
    Given planning period from 1DEC2019 to 28DEC2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | region          | SKD       |            |          |

    Given crew member 1 has a personal activity "A" at station "CPH" that starts at 14DEC2019 07:00 and ends at 14DEC2019 15:00

    When I load rule set "rule_set_jct"
    and I show "crew" in window 1
    Then the rule "rules_standby_common.stb_max_duration_airport_standby_CC_SKD_SKN_SKL" shall pass on leg 1 on trip 1 on roster 1
    and rave "leg.%is_waiting_at_airport%" shall be "True" on leg 1 on trip 1 on roster 1
##########################################################################################

  @SCENARIO_2 @tracking
  Scenario: Crew allowed to stand by at airport for 4 hours or less.
    Given Tracking
    Given planning period from 1DEC2019 to 28DEC2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | region          | SKD       |            |          |

    Given crew member 1 has a personal activity "A" at station "CPH" that starts at 14DEC2019 07:00 and ends at 14DEC2019 09:00

    When I load rule set "rule_set_jct"
    and I show "crew" in window 1

    Then rave "base_product.%is_tracking%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "wop.%has_airport_standby%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "leg.%is_waiting_at_airport%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_standby_common.stb_max_duration_airport_standby_CC_SKD_SKN_SKL" shall pass on leg 1 on trip 1 on roster 1

##########################################################################################

  @SCENARIO_3 @planning
  Scenario: rule will fail regardless of duration spent as standby.
    Given Rostering_CC
    Given planning period from 1DEC2019 to 28DEC2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | region          | SKD       |            |          |

    Given crew member 1 has a personal activity "A" at station "CPH" that starts at 14DEC2019 07:00 and ends at 14DEC2019 12:00
        
    When I show "crew" in window 1
    and I load rule set "Rostering_CC"
    When I set parameter "fundamental.%start_para%" to "1DEC2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31DEC2019 00:00"

    Then rave "base_product.%is_tracking%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "wop.%has_airport_standby%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "leg.%is_waiting_at_airport%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_standby_common.stb_max_duration_airport_standby_CC_SKD_SKN_SKL" shall fail on leg 1 on trip 1 on roster 1

##########################################################################################
