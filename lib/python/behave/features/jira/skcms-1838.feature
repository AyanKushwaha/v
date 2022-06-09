Feature: Test rule ind_training_earliest_ci_after_night_simulators that prohibits early check-in after two consecutive night sim sessions.

  Background: set up for tracking
    Given Tracking
    Given planning period from 1OCT2018 to 31OCT2018

  # Disabled this scenario because it is not valid. No checkin before 12:00. Period.
  # Scenario: Check that rule does not fail when checking in before 6:00 the day after two consecutive night sim sessions 

  #   Given a crew member with homebase "OSL"
  #   Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 

  #   Given a trip with the following activities
  #   | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
  #   | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
  #   | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
  #   | ground | 0003 | OSL     | OSL     | 03OCT2018 | 05:00 | 09:00 | S2   |    
  #   Given trip 1 is assigned to crew member 1 in position FC
    
  #   When I show "crew" in window 1
  #   Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall pass on leg 3 on trip 1 on roster 1
    
  Scenario: Check that rule fails when checking in between 6:00 and 12:00 the day after two consecutive sim night shifts
  
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    | ground | 0003 | OSL     | OSL     | 03OCT2018 | 08:00 | 09:00 | S2   |    
    Given trip 1 is assigned to crew member 1 in position FC    

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall fail on leg 3 on trip 1 on roster 1    
    

  Scenario: Check that rule does not fail before it is valid
    Given planning period from 1SEP2018 to 30SEP2018
  
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1SEP2018 to 30SEP2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01SEP2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02SEP2018 | 01:00 | 04:00 | S2   |
    | ground | 0003 | OSL     | OSL     | 03SEP2018 | 08:00 | 09:00 | S2   |    
    Given trip 1 is assigned to crew member 1 in position FC    

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall pass on leg 3 on trip 1 on roster 1    


  Scenario: Check that rule does not fail when checking in between 6:00 and 12:00 on the same day as the sim night shift
  
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    | ground | 0003 | OSL     | OSL     | 02OCT2018 | 08:00 | 09:00 | S2   |    
    Given trip 1 is assigned to crew member 1 in position FC    

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall pass on leg 3 on trip 1 on roster 1


  Scenario: Check that rule does not fail with a freeday - F - the day after two consecutive sim night shifts
  
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall pass on leg 1 on trip 2 on roster 1    
    

  Scenario: Check that rule does not fail with a freeday - F3 - the day after two consecutive sim night shifts

    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 

    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    Given trip 1 is assigned to crew member 1 in position FC
    Given crew member 1 has a personal activity "F3" at station "OSL" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.ind_training_earliest_ci_after_night_simulators" shall pass on leg 1 on trip 2 on roster 1    
    
