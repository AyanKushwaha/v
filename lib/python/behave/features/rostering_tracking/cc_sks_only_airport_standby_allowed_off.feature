@tracking @ALL @JCRT
Feature:
############
# SKCMS-2066
############

  Background: set up for tracking
    Given Tracking
    Given planning period from 1OCT2018 to 31OCT2018

   Scenario: Temporary cabin crew want to have standby at home.
     Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | region          | SKS       |            |          |

  Given crew member 1 has contract "V00863"

      Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R83   | ARN     | ARN     | 9OCT2018  | 00:00 | 23:59 |


   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load ruleset "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1OCT2018 00:00"
   When I set parameter "fundamental.%end_para%" to "31OCT2018 00:00"

   Then rave "rule_on(rules_standby_common.stb_only_airport_standby_allowed_temp_CC_SKS)" shall be "False"


