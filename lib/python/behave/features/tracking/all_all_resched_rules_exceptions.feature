
#####################
# JIRA - skcms-2242
#####################
@TRACKING  @SH @CC @FD 

Feature: Testing exceptions to resheduling rules before time off (SKCMS-2242)

    Background: Setup for tracking
      Given Tracking
      Given planning period from 1SEP2019 to 3OCT2019

    @SCENARIO_1 @SKD
    Scenario: SKS, SKN, SKD FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 1

     Given a crew member with
     | attribute       | value     | valid from | valid to |
     | employee number | 23271     |            |          |
     | base            | CPH       |            |          |
     | title rank      | FD        |            |          |
     | region          | SKD       |            |          |
    Given crew member 1 has contract "V131"
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 13SEP2019 10:20 and ends at 13SEP2019 20:20
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 14SEP2019 10:20 and ends at 14SEP2019 20:20
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 16SEP2019 23:00 and ends at 16SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 14SEP2019 10:20 and end at 14SEP2019 23:20

    Then rave "leg.%start_utc%" shall be "14SEP2019 10:20" on leg 2 on trip 1
    and rave "leg.%end_utc%" shall be "14SEP2019 23:20" on leg 2 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 2 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 2 on trip 1


    @SCENARIO_2 @SKN
    Scenario: SKD FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 2

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 38382     |            |          |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V131"
    Given crew member 1 has a personal activity "R2" at station "CPH" that starts at 13SEP2019 09:40 and ends at 13SEP2019 19:40
    Given crew member 1 has a personal activity "R2" at station "CPH" that starts at 14SEP2019 10:00 and ends at 14SEP2019 20:00
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 14SEP2019 23:00 and ends at 16SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 14SEP2019 10:00 and end at 14SEP2019 22:00

    Then rave "leg.%start_utc%" shall be "14SEP2019 10:00" on leg 2 on trip 1
    and rave "leg.%end_utc%" shall be "14SEP2019 22:00" on leg 2 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 2 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 2 on trip 1


    @SCENARIO_3 @SKS
    Scenario: SKN FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 3

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 19515     |            |          |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |
    Given crew member 1 has contract "V00286-FLEX"
    Given crew member 1 has a personal activity "R3" at station "OSL" that starts at 13SEP2019 08:50 and ends at 13SEP2019 18:50
    Given crew member 1 has a personal activity "R3" at station "OSL" that starts at 14SEP2019 10:55 and ends at 14SEP2019 20:55
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 14SEP2019 23:00 and ends at 17SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 14SEP2019 10:55 and end at 14SEP2019 22:55

    Then rave "leg.%start_utc%" shall be "14SEP2019 10:55" on leg 2 on trip 1
    and rave "leg.%end_utc%" shall be "14SEP2019 22:55" on leg 2 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 2 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 2 on trip 1


    @SCENARIO_4 @SKN
    Scenario: SKN CC should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 4

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 63507     |            |          |
    | base            | OSL       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V1020"
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 14SEP2019 04:00 and ends at 14SEP2019 14:00
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 15SEP2019 04:00 and ends at 15SEP2019 14:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 15SEP2019 23:00 and ends at 18SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 15SEP2019 04:00 and end at 15SEP2019 16:00

    Then rave "leg.%start_utc%" shall be "15SEP2019 04:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "15SEP2019 16:00" on leg 1 on trip 2
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 1 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 1 on trip 2


##########################################################################################
# Scenarios that shall fail
##########################################################################################

    @SCENARIO_5 @SKD
    Scenario: SKD CC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 5

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 29226     |            |          |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V339"
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 14SEP2019 10:00 and ends at 14SEP2019 20:00
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 15SEP2019 10:00 and ends at 15SEP2019 20:00
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 15SEP2019 23:00 and ends at 17SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 15SEP2019 10:00 and end at 15SEP2019 22:00


    Then rave "leg.%start_utc%" shall be "15SEP2019 10:00" on leg 2 on trip 1
    and rave "leg.%end_utc%" shall be "15SEP2019 22:00" on leg 2 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "True" on leg 2 on trip 1

    @SCENARIO_6 @SKS
    Scenario: SKS CC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 6

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 10314     |            |          |
    | base            | STO       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKS       |            |          |
    Given crew member 1 has contract "V322"
    Given crew member 1 has a personal activity "R" at station "CPH" that starts at 13SEP2019 02:45 and ends at 13SEP2019 12:45
    Given crew member 1 has a personal activity "R" at station "CPH" that starts at 14SEP2019 10:00 and ends at 14SEP2019 20:00
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 14SEP2019 23:00 and ends at 16SEP2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 14SEP2019 10:00 and end at 14SEP2019 22:00

    Then rave "leg.%start_utc%" shall be "14SEP2019 10:00" on leg 2 on trip 1
    and rave "leg.%end_utc%" shall be "14SEP2019 22:00" on leg 2 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "True" on leg 2 on trip 1

    
    @SCENARIO_7 @SKN @OSL
    Scenario: SKN CC RC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 7
    #RC being re-rescheduled >2 hours

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 63507     |            |          |
    | base            | OSL       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V1020"
    Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 14SEP2019 04:00 and ends at 14SEP2019 14:00
    Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 15SEP2019 04:00 and ends at 15SEP2019 14:00
    Given personal activity 1 of crew member 1 is unlocked
    Given personal activity 2 of crew member 1 is unlocked
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 1 of crew member 1 to start at 14SEP2019 08:00 and end at 14SEP2019 19:00

    Then rave "rules_resched_cct.%trip_inf_is_last_in_wop_with_co%" shall be "False" on leg 1 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "True" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall fail on leg 1 on trip 1

    @SCENARIO_8 @SKN @OSL
    Scenario: SKN CC R should be exempt even though RC comes after.
    #SKCMS 2242 Jira provided case 8

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 63507     |            |          |
    | base            | OSL       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V1020"
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 14SEP2019 04:00 and ends at 14SEP2019 14:00
    Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 15SEP2019 04:00 and ends at 15SEP2019 14:00
    Given personal activity 1 of crew member 1 is unlocked
    Given personal activity 2 of crew member 1 is unlocked
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 1 of crew member 1 to start at 14SEP2019 08:00 and end at 14SEP2019 19:00

    Then rave "rules_resched_cct.%trip_inf_is_last_in_wop_with_co%" shall be "False" on leg 1 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "False" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 1 on trip 1

    @SCENARIO_9 @SKN @OSL
    Scenario: SKN CC RC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2242 Jira provided case 7
    #RC being re-rescheduled <2 hours

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 63507     |            |          |
    | base            | OSL       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V1020"
    Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 14SEP2019 04:00 and ends at 14SEP2019 14:00
    Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 15SEP2019 04:00 and ends at 15SEP2019 14:00
    Given personal activity 1 of crew member 1 is unlocked
    Given personal activity 2 of crew member 1 is unlocked
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 1 of crew member 1 to start at 14SEP2019 05:00 and end at 14SEP2019 15:00

    Then rave "rules_resched_cct.%trip_inf_is_last_in_wop_with_co%" shall be "False" on leg 1 on trip 1
    and rave "rules_resched_cct.%resched_later_check_out_homebase_ALL_valid%" shall be "True" on leg 1 on trip 1
    and the rule "rules_resched_cct.resched_later_check_out_homebase_sh_ALL" shall pass on leg 1 on trip 1



