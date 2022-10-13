Feature: A3A5 pilots in need of LPCA3A5 training, should get S5 converted to Y5.
Background: Set up for Tracking

Given Tracking
Given planning period from 1MAR2022 to 31MAR2022
Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | region     | STO   |
      | base       | ARN   |
    

@PASS_1
Scenario: leg_is_lpc shall be True
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1AUG2019 to 30APR2022
	Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 30APR2022
	
    Given crew member 1 has document "REC+LPCA3A5" from 8FEB2019 to 30APR2022


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S5   | ARN     | ARN     | 13mar2022| 10:00 | 12:00 |
	| ground | S5   | ARN     | ARN     | 13mar2022 | 14:00 | 16:00 |
	
    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "training.%leg_is_lpc%" shall be "True" on leg 1 on trip 1 on roster 1
    Then rave "leg.%code%" shall be "S5" on leg 1 on trip 1 on roster 1
    Then rave "training.%leg_code_redefined%" shall be "Y5" on leg 1 on trip 1 on roster 1
    
  #########################################
@PASS_2
  Scenario: leg_is_lpc shall be False

    
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1AUG2019 to 28FEB2022
	Given crew member 1 has qualification "ACQUAL+A5" from 1AUG2019 to 28FEB2022
	
    Given crew member 1 has document "REC+LPCA3A5" from 8FEB2019 to 28FEB2022


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S5   | ARN     | ARN     | 13mar2022 | 10:00 | 12:00 |
	| ground | S5   | ARN     | ARN     | 13mar2022 | 14:00 | 16:00 |
	
    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "training.%leg_is_lpc%" shall be "False" on leg 1 on trip 1 on roster 1
    Then rave "leg.%code%" shall be "S5" on leg 1 on trip 1 on roster 1
    