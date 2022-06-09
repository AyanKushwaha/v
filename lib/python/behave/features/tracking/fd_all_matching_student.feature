Feature: Test matching student rule

  Background: set up for tracking
    Given Tracking
    Given planning period from 1JUN2019 to 30JUN2019

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

  @SCENARIO1
  Scenario: Check that FAM FLT instructor in FC position has matching student

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019
    Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+LIFUS" from 1JUN2019 to 30JUN2019 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 01JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_instructor_has_matching_student_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that FAM FLT instructor in FC position has no matching student

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019 
    Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+TRE" from 1JUN2019 to 30JUN2019 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A5" from 1JUN2019 to 30JUN2019 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 01JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 1 is assigned to crew member 2 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_instructor_has_matching_student_all" shall fail on leg 1 on trip 1 on roster 1
