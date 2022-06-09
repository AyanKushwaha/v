Feature: Test ZFTT LIFUS special schedule

  Background: set up for tracking
    Given Tracking
    Given planning period from 1MAY2017 to 31MAY2017

  Scenario: Crew with qualification INSTRUCTOR+TRI and INSTRUCTOR+LIFUS 
    on zftt lifus or zftt x legs must not have forbidden activity ZFTT in table special_schedules. 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    
    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+LIFUS" from 27FEB2017 to 01JAN2036 
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 27FEB2017 to 01JAN2036 
    Given crew member 1 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 
    Given crew member 2 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 

    Given table special_schedules additionally contains the following
    | crewid         | typ          | validfrom   | str_val | validto   |
    | crew member 1  | ForbiddenAct | 01MAY2017   | ZFTT    | 15MAY2017 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 09MAY2017 | 10:25 | 21:45 | SK  | 34A |
    | leg | 0002 | SFO     | CPH     | 11MAY2017 | 00:35 | 11:15 | SK  | 34A |
    Given trip 1 is assigned to crew member 1 in position FP with attribute INSTRUCTOR="ZFTT LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | JFK     | 16MAY2017 | 10:00 | 11:00 | SK  |
    | leg | 0002 | JFK     | OSL     | 17MAY2017 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
    
    When I show "crew" in window 1
    Then the rule "rules_training_ccr.special_schedule_zftt" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.special_schedule_zftt" shall pass on leg 1 on trip 2 on roster 1