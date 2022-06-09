# The rules rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all
# and rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all
# behave differently depending on if crew are published or not (rostering vs tracking).
# When crew are published, the instructor tag is checked and when crew are not
# published the instructor qualification is checked.
Feature: Test LIFUS training flights

  Background: set up for tracking
    Given Tracking
    Given planning period from 1feb2018 to 28feb2018

  @SCENARIO1
  Scenario: Check that trainee has good companion when pilot has LIFUS qualification

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
#    Given crew member 1 has qualification "INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that trainee has no good companion when pilot has no LIFUS qualification

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check that trainee has no good companion when pilot has LIFUS qualification but no INSTRUCTOR tag

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
#    Given crew member 1 has qualification "INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO4
  Scenario: Check that trainee has good companion when pilot has LIFUS qualification both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
#    Given crew member 1 has qualification "INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO5
  Scenario: Check that trainee has no good companion when pilot has no LIFUS qualification both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall fail on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO6
  Scenario: Check that trainee has no good companion when pilot has LIFUS qualification but no INSTRUCTOR tag both published

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 
#    Given crew member 1 has qualification "INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 01mar2018 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall fail on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO7
  Scenario: Check that trainee has good companion when pilot has LIFUS qualification for AWB

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2018 
#    Given crew member 1 has qualification "INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018 

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1FEB2018 to 28FEB2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 33A    |
    
    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.comp_crew_with_training_flight_has_good_companion_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_crew_with_training_flight_is_good_companion_all" shall pass on leg 1 on trip 1 on roster 1
