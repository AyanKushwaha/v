Feature: MFF pilots needing PC or OPC are assigned in pos A (assist)
Background: Set up for Tracking

Given Tracking
Given planning period from 1APR2022 to 31MAY2022
Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | region     | STO   |
      | base       | ARN   |
    

@PASS_1
Scenario: crew should not be in Assist postion
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1AUG2019 to 30APR2035
	Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 30APR2035
	
    Given crew member 1 has document "REC+PC" from 8FEB2019 to 30APR2022 and has qualification "A2" 
	Given crew member 1 has document "REC+OPCA5" from 8FEB2019 to 30APR2022

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S5   | ARN     | ARN     | 02APR2022| 10:00 | 12:00 |
	| ground | S5   | ARN     | ARN     | 02APR2022 | 14:00 | 16:00 |
	
    Given trip 1 is assigned to crew member 1 in position 1

    When I show "crew" in window 1

    Then rave "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall be "True" on leg 1 on trip 1 on roster 1
    Then rave "training.%assigned_as_assist%" shall be "False" on leg 1 on trip 1 on roster 1
    Then rave "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall be "True" on leg 1 on trip 1 on roster 1
    
  #########################################
  
  