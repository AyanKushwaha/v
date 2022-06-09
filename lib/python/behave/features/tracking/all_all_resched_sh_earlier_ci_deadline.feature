@tracking @SH @CC @FD
Feature: Test resheduling rules of earlier check in after ground duty 

    Background: Setup for tracking
      Given Tracking
      Given planning period from 1APR2020 to 30APR2020

##########################################################################################
# Scenarios that shall pass
##########################################################################################

    @SCENARIO1
    Scenario: Earlier check in after ground duty should pass on short haul duties if rescheduled during the ground duty

      Given a crew member with
      | attribute       | value     | valid from | valid to |
      | employee number | 24885     |            |          |
      | base            | CPH       |            |          |
      | title rank      | AH        |            |          |
      | region          | SKD       |            |          |

      
      Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | ARN     | 15APR2020 10:40 | 15APR2020 12:10 | 320     |         |
      | leg     | SK      | 102 | ARN     | CPH     | 15APR2020 13:40 | 15APR2020 15:10 | 320     |         |
      Given trip 1 is assigned to crew member 1 in position AH

      Given crew member 1 has a personal activity "CX7" at station "CPH" that starts at 14APR2020 10:20 and ends at 14APR2020 20:20

      Given the roster is published
      When I show "rosters" in window 1
      When I set parameter "fundamental.%use_now_debug%" to "TRUE"
      When I set parameter "fundamental.%now_debug%" to "14APR2020 18:00"
      and I select leg 1
      When I reschedule leg 2 of crew member 1 flight 101 to depart from CPH 15APR2020 09:40 and arrive at ARN 15APR2020 11:10

      Then rave "leg.%start_utc%" shall be "15APR2020 09:40" on leg 1 on trip 2
      and rave "leg.%end_utc%" shall be "15APR2020 11:10" on leg 1 on trip 2
      and the rule "rules_resched_cct.resched_earlier_check_in_homebase_deadline_sh_ALL" shall pass on leg 1 on trip 2

    @SCENARIO2
    Scenario: Earlier check in after ground duty should pass on short haul duties if rescheduled during previous trip

      Given a crew member with
      | attribute       | value     | valid from | valid to |
      | employee number | 24885     |            |          |
      | base            | CPH       |            |          |
      | title rank      | AH        |            |          |
      | region          | SKD       |            |          |

      Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | ARN     | 10APR2020 10:40 | 10APR2020 12:10 | 320     |         |
      | leg     | SK      | 102 | ARN     | CPH     | 10APR2020 13:40 | 10APR2020 15:10 | 320     |         |
      Given trip 1 is assigned to crew member 1 in position AH

      Given another trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 103 | CPH     | ARN     | 15APR2020 10:40 | 15APR2020 12:10 | 320     |         |
      | leg     | SK      | 104 | ARN     | CPH     | 15APR2020 13:40 | 15APR2020 15:10 | 320     |         |
      Given trip 2 is assigned to crew member 1 in position AH

      Given crew member 1 has a personal activity "F" at station "CPH" that starts at 10APR2020 22:00 and ends at 13APR2020 22:00
      Given crew member 1 has a personal activity "CX7" at station "CPH" that starts at 14APR2020 10:20 and ends at 14APR2020 20:20

      Given the roster is published
      When I show "rosters" in window 1
      When I set parameter "fundamental.%use_now_debug%" to "TRUE"
      When I set parameter "fundamental.%now_debug%" to "10APR2020 14:00"
      When I reschedule leg 4 of crew member 1 flight 103 to depart from CPH 15APR2020 09:40 and arrive at ARN 15APR2020 11:10

      Then rave "leg.%start_utc%" shall be "15APR2020 09:40" on leg 1 on trip 4
      and rave "leg.%end_utc%" shall be "15APR2020 11:10" on leg 1 on trip 4
      and the rule "rules_resched_cct.resched_earlier_check_in_homebase_deadline_sh_ALL" shall pass on leg 1 on trip 4


    @SCENARIO3
    Scenario: Earlier check in after ground duty should pass on short haul duties if rescheduled during vacation

      Given a crew member with
      | attribute       | value     | valid from | valid to |
      | employee number | 24885     |            |          |
      | base            | CPH       |            |          |
      | title rank      | AH        |            |          |
      | region          | SKD       |            |          |

      Given a trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 101 | CPH     | ARN     | 10APR2020 10:40 | 10APR2020 12:10 | 320     |         |
      | leg     | SK      | 102 | ARN     | CPH     | 10APR2020 13:40 | 10APR2020 15:10 | 320     |         |
      Given trip 1 is assigned to crew member 1 in position AH

      Given another trip with the following activities
      | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
      | leg     | SK      | 103 | CPH     | ARN     | 15APR2020 10:40 | 15APR2020 12:10 | 320     |         |
      | leg     | SK      | 104 | ARN     | CPH     | 15APR2020 13:40 | 15APR2020 15:10 | 320     |         |
      Given trip 2 is assigned to crew member 1 in position AH

      Given crew member 1 has a personal activity "F" at station "CPH" that starts at 10APR2020 22:00 and ends at 13APR2020 22:00
      Given crew member 1 has a personal activity "CX7" at station "CPH" that starts at 14APR2020 10:20 and ends at 14APR2020 20:20

      Given the roster is published
      When I show "rosters" in window 1
      When I set parameter "fundamental.%use_now_debug%" to "TRUE"
      When I set parameter "fundamental.%now_debug%" to "13APR2020 14:00"
      When I reschedule leg 4 of crew member 1 flight 103 to depart from CPH 15APR2020 09:40 and arrive at ARN 15APR2020 11:10

      Then rave "leg.%start_utc%" shall be "15APR2020 09:40" on leg 1 on trip 4
      and rave "leg.%end_utc%" shall be "15APR2020 11:10" on leg 1 on trip 4
      and the rule "rules_resched_cct.resched_earlier_check_in_homebase_deadline_sh_ALL" shall pass on leg 1 on trip 4
