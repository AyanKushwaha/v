##########################
# Developed in SKCMS-2053
##########################
@TRACKING @NEW_ACTYPE_RESTRICTION
Feature: Test NEW restriction

  Background: set up for tracking
    Given Tracking
    Given planning period from 1dec2018 to 31dec2018

  @SCENARIO1
  Scenario: Test that more than max number of NEW restricted crew fails
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03SEP2018  | 01JAN2036 |
           | region          | SKS        | 03SEP2018  | 01JAN2036 |
           | base            | STO        | 03SEP2018  | 01JAN2036 |
           | title rank      | AH         | 03SEP2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 03SEP2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036
    Given crew member 1 has restriction "NEW+6M" from 17OCT2018 to 28APR2019
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 13DEC2018 to 12JAN2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20AUG2018  | 01JAN2036 |
           | region          | SKS        | 20AUG2018  | 01JAN2036 |
           | base            | STO        | 20AUG2018  | 01JAN2036 |
           | title rank      | AH         | 20AUG2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+38" from 20AUG2018 to 01JAN2036
    Given crew member 2 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036
    Given crew member 2 has restriction "NEW+6M" from 14SEP2018 to 11MAR2019
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15DEC2018 to 14JAN2019

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | ARN     | AGH     | 23DEC2018 11:45 | 23DEC2018 12:50 | 73K     |         |
           | leg     | SK      | 000178  | AGH     | ARN     | 23DEC2018 13:15 | 23DEC2018 14:15 | 73K     |         |
           | leg     | SK      | 000673  | ARN     | FRA     | 23DEC2018 16:00 | 23DEC2018 18:10 | 32G     |         |
           | leg     | SK      | 000674  | FRA     | ARN     | 23DEC2018 18:50 | 23DEC2018 20:55 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 4 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 3 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall fail on leg 4 on trip 1 on roster 2

  @SCENARIO2
  Scenario: Test that allowed number of NEW restricted crew passes
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03SEP2018  | 01JAN2036 |
           | region          | SKS        | 03SEP2018  | 01JAN2036 |
           | base            | STO        | 03SEP2018  | 01JAN2036 |
           | title rank      | AH         | 03SEP2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 03SEP2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20AUG2018  | 01JAN2036 |
           | region          | SKS        | 20AUG2018  | 01JAN2036 |
           | base            | STO        | 20AUG2018  | 01JAN2036 |
           | title rank      | AH         | 20AUG2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+38" from 20AUG2018 to 01JAN2036
    Given crew member 2 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036
    Given crew member 2 has restriction "NEW+6M" from 14SEP2018 to 11MAR2019
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15DEC2018 to 14JAN2019

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | ARN     | AGH     | 23DEC2018 11:45 | 23DEC2018 12:50 | 73K     |         |
           | leg     | SK      | 000178  | AGH     | ARN     | 23DEC2018 13:15 | 23DEC2018 14:15 | 73K     |         |
           | leg     | SK      | 000673  | ARN     | FRA     | 23DEC2018 16:00 | 23DEC2018 18:10 | 32G     |         |
           | leg     | SK      | 000674  | FRA     | ARN     | 23DEC2018 18:50 | 23DEC2018 20:55 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 4 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 3 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 4 on trip 1 on roster 2


  @CC @AU @SCENARIO3
  Scenario: Test that cabin crew in supernum (AU) positions aren't considered for the rule
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 03SEP2018  | 01JAN2036 |
           | region          | SKS        | 03SEP2018  | 01JAN2036 |
           | base            | STO        | 03SEP2018  | 01JAN2036 |
           | title rank      | AH         | 03SEP2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 03SEP2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036
    Given crew member 1 has restriction "NEW+6M" from 17OCT2018 to 28APR2019
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 13DEC2018 to 12JAN2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 20AUG2018  | 01JAN2036 |
           | region          | SKS        | 20AUG2018  | 01JAN2036 |
           | base            | STO        | 20AUG2018  | 01JAN2036 |
           | title rank      | AH         | 20AUG2018  | 01JAN2036 |
           | published       | 01FEB2019  | 01JAN1986  |           |
    Given crew member 2 has qualification "ACQUAL+38" from 20AUG2018 to 01JAN2036
    Given crew member 2 has qualification "ACQUAL+A2" from 11DEC2018 to 01JAN2036
    Given crew member 2 has restriction "NEW+6M" from 14SEP2018 to 11MAR2019
    Given crew member 2 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 15DEC2018 to 14JAN2019

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000177  | ARN     | AGH     | 23DEC2018 11:45 | 23DEC2018 12:50 | 73K     |         |
           | leg     | SK      | 000178  | AGH     | ARN     | 23DEC2018 13:15 | 23DEC2018 14:15 | 73K     |         |
           | leg     | SK      | 000673  | ARN     | FRA     | 23DEC2018 16:00 | 23DEC2018 18:10 | 32G     |         |
           | leg     | SK      | 000674  | FRA     | ARN     | 23DEC2018 18:50 | 23DEC2018 20:55 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position 8
    Given trip 1 is assigned to crew member 2 in position 8

    When I show "crew" in window 1

    Then the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 3 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 4 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 2 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 3 on trip 1 on roster 2
    and the rule "rules_training_ccr.comp_max_restricted_new_all" shall pass on leg 4 on trip 1 on roster 2

