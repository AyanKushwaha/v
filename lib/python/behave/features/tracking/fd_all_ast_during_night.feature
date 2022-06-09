Feature: Test AST during night is allowed for A3A4 pilots rule

  Background: set up for tracking
    Given Tracking
    Given planning period from 1AUG2018 to 31AUG2018

@SCENARIO1
Scenario: Check that qualification that is not A3 and A4 is not allowed AST between 3-7 am.
    
    Given a crew member with homebase "ARN"
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2019

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | K2   | ARN     | ARN     | 07AUG2018 | 00:00 | 04:00 |

    Given trip 1 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1
    Then the rule "rules_studio_ccp.ast_allowed_time_of_day" shall fail on leg 1 on trip 1 on roster 1

@SCENARIO2
Scenario: Check that qualifications A3 and A4 are exempt from rule forbidding AST between 3-7 am.
    
    Given a crew member with homebase "ARN"
    Given crew member 1 has qualification "ACQUAL+A4" from 1FEB2018 to 28FEB2019
    

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | K4   | ARN     | ARN     | 07AUG2018 | 00:00 | 04:00 |



    Given trip 1 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1
    Then the rule "rules_studio_ccp.ast_allowed_time_of_day" shall pass on leg 1 on trip 1 on roster 1
    