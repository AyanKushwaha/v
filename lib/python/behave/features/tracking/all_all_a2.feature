##########################
# Developed in SKCMS-2615
##########################
@TRACKING @NEW_ACTYPE_RESTRICTION
Feature: Test NEW restriction

  Background: set up for tracking
    Given Tracking
    Given planning period from 1may2021 to 31may2021

  @SCENARIO1
  Scenario: Test that allowed number of NEW restricted crew passes for A2 qual flights except A319 aircraft_type
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03JAN2021  | 01JAN2036 |
           | region          | SKN        | 03JAN2021  | 01JAN2036 |
           | base            | OSL        | 03JAN2021  | 01JAN2036 |
           | title rank      | AH         | 03JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+A2" from 11APR2021 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15MAY2021 to 12JUN2022

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+A2" from 11APR2021 to 01JAN2036
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15MAY2021 to 14JUN2022
    
    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | OSL     | AMS     | 23MAY2021 11:45 | 23MAY2021 12:50 | 321     |         |
           | leg     | SK      | 000178  | AMS     | OSL     | 23MAY2021 13:15 | 23MAY2021 14:15 | 32U     |         |
           | leg     | SK      | 000673  | OSL     | AMS     | 23MAY2021 16:00 | 23MAY2021 18:10 | 31W     |         |
           | leg     | SK      | 000674  | AMS     | OSL     | 23MAY2021 18:50 | 23MAY2021 20:55 | 319     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH    
    

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 4 on trip 1 on roster 1

  @SCENARIO2
  Scenario: Test that allowed number of NEW restricted crew fails for A2 qual flights 
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03JAN2021  | 01JAN2036 |
           | region          | SKN        | 03JAN2021  | 01JAN2036 |
           | base            | OSL        | 03JAN2021  | 01JAN2036 |
           | title rank      | AH         | 03JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+A2" from 11APR2021 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15MAY2021 to 12JUN2022

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+A2" from 11APR2021 to 01JAN2036
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15MAY2021 to 14JUN2022
    
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2022  | 01JAN1986  |           |
    Given crew member 3 has qualification "ACQUAL+A2" from 11APR2021 to 01JAN2036
    Given crew member 3 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15MAY2021 to 14JUN2022

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | OSL     | AMS     | 23MAY2021 11:45 | 23MAY2021 12:50 | 321     |         |
           | leg     | SK      | 000178  | AMS     | OSL     | 23MAY2021 13:15 | 23MAY2021 14:15 | 32U     |         |
           | leg     | SK      | 000673  | OSL     | AMS     | 23MAY2021 16:00 | 23MAY2021 18:10 | 31W     |         |
           | leg     | SK      | 000674  | AMS     | OSL     | 23MAY2021 18:50 | 23MAY2021 20:55 | 319     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH    
    Given trip 1 is assigned to crew member 3 in position AH

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 4 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Regressive test  to see that allowed number of NEW restricted crew passes for AL qual flights passes
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03JAN2021  | 01JAN2036 |
           | region          | SKN        | 03JAN2021  | 01JAN2036 |
           | base            | OSL        | 03JAN2021  | 01JAN2036 |
           | title rank      | AH         | 03JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 11APR2021 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 15MAY2021 to 12JUN2022

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+AL" from 11APR2021 to 01JAN2036
    Given crew member 2 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 15MAY2021 to 14JUN2022
    
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2022  | 01JAN1986  |           |
    Given crew member 3 has qualification "ACQUAL+AL" from 11APR2021 to 01JAN2036
    Given crew member 3 has acqual restriction "ACQUAL+AL+NEW+ACTYPE" from 15MAY2021 to 14JUN2022

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | OSL     | AMS     | 23MAY2021 11:45 | 23MAY2021 12:50 | 34L     |         |
           | leg     | SK      | 000178  | AMS     | OSL     | 23MAY2021 13:15 | 23MAY2021 14:15 | 343     |         |
           | leg     | SK      | 000673  | OSL     | AMS     | 23MAY2021 16:00 | 23MAY2021 18:10 | 33A     |         |
           | leg     | SK      | 000674  | AMS     | OSL     | 23MAY2021 18:50 | 23MAY2021 20:55 | 33E     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH    
    Given trip 1 is assigned to crew member 3 in position AH

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 4 on trip 1 on roster 1

 @SCENARIO4
  Scenario: Test that allowed number of NEW restricted crew fails for flights except A2 and AL Qual flights 
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03JAN2021  | 01JAN2036 |
           | region          | SKN        | 03JAN2021  | 01JAN2036 |
           | base            | OSL        | 03JAN2021  | 01JAN2036 |
           | title rank      | AH         | 03JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 11APR2021 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+38+NEW+ACTYPE" from 15MAY2021 to 12JUN2022

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20JAN2021  | 01JAN2036 |
           | region          | SKN        | 20JAN2021  | 01JAN2036 |
           | base            | OSL        | 20JAN2021  | 01JAN2036 |
           | title rank      | AH         | 20JAN2021  | 01JAN2036 |
           | published       | 01JUL2020  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+38" from 11APR2021 to 01JAN2036
    Given crew member 2 has acqual restriction "ACQUAL+38+NEW+ACTYPE" from 15MAY2021 to 14JUN2022
   

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | OSL     | AMS     | 23MAY2021 11:45 | 23MAY2021 12:50 | 73W     |         |
           | leg     | SK      | 000178  | AMS     | OSL     | 23MAY2021 13:15 | 23MAY2021 14:15 | 73P     |         |
           | leg     | SK      | 000673  | OSL     | AMS     | 23MAY2021 16:00 | 23MAY2021 18:10 | 73J     |         |
           | leg     | SK      | 000674  | AMS     | OSL     | 23MAY2021 18:50 | 23MAY2021 20:55 | 73I     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH    


    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 4 on trip 1 on roster 1
