# The rules rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all
# and rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all
# behave differently depending on if crew are published or not (rostering vs tracking).
# When crew are published, the instructor tag is checked and when crew are not
# published the instructor qualification is checked.
Feature: Test FAM FLT training flights

  Background: set up for tracking
    Given Tracking
    Given planning period from 1JUN2020 to 30JUN2020

  @SCENARIO1
  Scenario: Check that LR REFRESH trainee in FP position has good companion when pilot has LIFUS qualification

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that LR REFRESH trainee in FP position has no good companion when pilot has no LIFUS qualification

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check that LR REFRESH trainee in FP position has no good companion when pilot has POSITION+LCP qualification and no INSTRUCTOR tag

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 
    Given crew member 1 has qualification "POSITION+LCP" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO4
  Scenario: Check that FC LR REFRESH trainee has good companion when instructor has TRI qualification both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2020 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUN2020 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO5
  Scenario: Check that FC LR REFRESH trainee has good companion when instructor has no LIFUS qualification both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2020 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2020 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO6
  Scenario: Check that FC LR REFRESH trainee has no good companion when instructor has SFE qualification but no INSTRUCTOR tag both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2020 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2020 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FP
    Given trip 1 is assigned to crew member 2 in position FC with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall fail on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO7
  Scenario: Check that LR REFRESH trainee in FP position has good companion when pilot has LIFUS qualification for A2

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JUN2020 to 30JUN2020 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JUN2020 to 30JUN2020 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01JUN2020 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | LHR     | OSL     | 01JUN2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1
