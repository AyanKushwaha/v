@TRACKING @SH
Feature: Testing exceptions to resheduling rules before time off (SKCMS-2068)

    Background: Setup for tracking
      Given Tracking
      Given planning period from 1FEB2019 to 1MAR2019

      Given table agreement_validity additionally contains the following
       | id         | validfrom | validto   | si |
       | resched_SB | 10Feb2019 | 31Dec2035 |    |

##########################################################################################
# Scenarios that shall pass
##########################################################################################

    @FD @SKS
    Scenario: SKS FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 1

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FC     |
    | region     | SKS    |
    Given crew member 1 has contract "V133"
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 24FEB2019 10:20 and ends at 24FEB2019 20:20
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 25FEB2019 10:20 and ends at 25FEB2019 20:20
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 25FEB2019 23:00 and ends at 28FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 25FEB2019 10:20 and end at 25FEB2019 22:20

    Then rave "leg.%start_utc%" shall be "25FEB2019 10:20" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "25FEB2019 22:20" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall pass on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall pass on leg 1 on trip 2


    @FD @SKD
    Scenario: SKD FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 2

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FP     |
    | region     | SKD    |
    Given crew member 1 has contract "V131"
    Given crew member 1 has a personal activity "R2" at station "CPH" that starts at 23FEB2019 09:40 and ends at 23FEB2019 19:40
    Given crew member 1 has a personal activity "R2" at station "CPH" that starts at 24FEB2019 10:00 and ends at 24FEB2019 20:00
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 24FEB2019 23:00 and ends at 26FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 24FEB2019 10:00 and end at 24FEB2019 22:00

    Then rave "leg.%start_utc%" shall be "24FEB2019 10:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "24FEB2019 22:00" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall pass on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall pass on leg 1 on trip 2


    @FD @SKN
    Scenario: SKN FD should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 3

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FC     |
    | region     | SKN    |
    Given crew member 1 has contract "V00286-FLEX"
    Given crew member 1 has a personal activity "R3" at station "OSL" that starts at 23FEB2019 08:50 and ends at 23FEB2019 18:50
    Given crew member 1 has a personal activity "R3" at station "OSL" that starts at 24FEB2019 10:55 and ends at 24FEB2019 20:55
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 24FEB2019 23:00 and ends at 27FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 24FEB2019 10:55 and end at 24FEB2019 22:55

    Then rave "leg.%start_utc%" shall be "24FEB2019 10:55" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "24FEB2019 22:55" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall pass on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall pass on leg 1 on trip 2


    @CC @SKN
    Scenario: SKN CC should be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 4

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V1004"
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 24FEB2019 04:00 and ends at 24FEB2019 14:00
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 25FEB2019 04:00 and ends at 25FEB2019 14:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 25FEB2019 23:00 and ends at 28FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 25FEB2019 04:00 and end at 25FEB2019 16:00

    Then rave "leg.%start_utc%" shall be "25FEB2019 04:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "25FEB2019 16:00" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall pass on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall pass on leg 1 on trip 2


##########################################################################################
# Scenarios that shall fail
##########################################################################################

    @CC @SKS
    Scenario: SKS CC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 5

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | AH     |
    | region     | SKS    |
    Given crew member 1 has contract "V340"
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 24FEB2019 10:00 and ends at 24FEB2019 20:00
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 25FEB2019 10:00 and ends at 25FEB2019 20:00
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 25FEB2019 23:00 and ends at 27FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 25FEB2019 10:00 and end at 25FEB2019 22:00

    Then rave "leg.%start_utc%" shall be "25FEB2019 10:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "25FEB2019 22:00" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall fail on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall fail on leg 1 on trip 2


    @CC @SKD
    Scenario: SKD CC should not be exempt from rules restricting rescheduling of short haul standby before time off
    #SKCMS 2068 Jira provided case 6

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | AH     |
    | region     | SKD    |
    Given crew member 1 has contract "V304"
    Given crew member 1 has a personal activity "R" at station "CPH" that starts at 23FEB2019 02:45 and ends at 23FEB2019 12:45
    Given crew member 1 has a personal activity "R" at station "CPH" that starts at 24FEB2019 10:00 and ends at 24FEB2019 20:00
    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 24FEB2019 23:00 and ends at 26FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 24FEB2019 10:00 and end at 24FEB2019 22:00

    Then rave "leg.%start_utc%" shall be "24FEB2019 10:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "24FEB2019 22:00" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall fail on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_standby_before_time_off_sh_ALL" shall fail on leg 1 on trip 2


    @CC @SKN
    Scenario: Exceptions from short haul standby rescheduling resctrictions should not be active if standby is at airport

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | AH     |
    | region     | SKN    |
    Given crew member 1 has contract "V1004"

    Given crew member 1 has the following personal activities
    | code | stn  | start_date | start_time | end_date  | end_time | lock  | duty |
    | A    | OSL  | 24FEB2019  | 04:00      | 24FEB2019 | 14:00    | True  | On   |
    | A    | OSL  | 25FEB2019  | 04:00      | 25FEB2019 | 14:00    | False | On   |
    | F    | OSL  | 25FEB2019  | 23:00      | 28FEB2019 | 23:00    | True  | Off  |

    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 25FEB2019 04:00 and end at 25FEB2019 16:00

    Then rave "leg.%start_utc%" shall be "25FEB2019 04:00" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "25FEB2019 16:00" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall fail on leg 1 on trip 2


    @FD @SKS
    Scenario: SKS FD should not be exempt from rescheduling rules if validity parameter is not yet valid

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FC     |
    | region     | SKS    |
    Given crew member 1 has contract "V133"
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 07FEB2019 10:20 and ends at 07FEB2019 20:20
    Given crew member 1 has a personal activity "R2" at station "ARN" that starts at 08FEB2019 10:20 and ends at 08FEB2019 20:20
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 08FEB2019 23:00 and ends at 11FEB2019 23:00
    Given personal activity 2 of crew member 1 is unlocked
    Given personal activity 3 of crew member 1 is off-duty
    Given the roster is published

    When I show "rosters" in window 1
    When I reschedule personal activity 2 of crew member 1 to start at 08FEB2019 10:20 and end at 08FEB2019 22:20

    Then rave "leg.%start_utc%" shall be "08FEB2019 10:20" on leg 1 on trip 2
    and rave "leg.%end_utc%" shall be "08FEB2019 22:20" on leg 1 on trip 2
    and the rule "rules_resched_cct.resched_check_out_homebase_before_timeoff_sh_ALL" shall fail on leg 1 on trip 2
    and rave "rules_resched_cct.%_valid_when_resched_sb_is_live%(rules_resched_cct.%_ag_not_exempt_resched_sh_sb_before_timeoff%, trip.%start_UTC%)" shall be "True" on leg 1 on trip 2

