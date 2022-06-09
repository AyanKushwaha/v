Feature: Crew should not check out late before summer vacation.

  @SCENARIO1
  Scenario: SKN CC passes early checkout 2F + 19VA
    Given Tracking
    Given planning period from 1JUL2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | region          | SKN        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | AH         | 28JAN2014  | 01JAN2036 |
           | contract        | SNK_V301   | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2019 09:10 | 11JUL2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2019 22:55 | 13JUL2019 06:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 13JUL2019 22:00 and ends at 15JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 15JUL2019 22:00 and ends at 31JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2019 22:00 and ends at 03AUG2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: SKN CC fails late checkout 2F + 19VA
    Given Tracking
    Given planning period from 1JUL2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | region          | SKN        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | AH         | 28JAN2014  | 01JAN2036 |
           | contract        | V301       | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2019 09:10 | 11JUL2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2019 22:55 | 13JUL2019 17:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 13JUL2019 22:00 and ends at 15JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 15JUL2019 22:00 and ends at 31JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2019 22:00 and ends at 03AUG2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall fail on leg 1 on trip 3 on roster 1


  @SCENARIO3
  Scenario: SKN CC passes late checkout 3F + 19VA
    Given Tracking
    Given planning period from 1JUL2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | region          | SKN        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | AH         | 28JAN2014  | 01JAN2036 |
           | contract        | SNK_V301   | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2019 09:10 | 11JUL2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2019 22:55 | 13JUL2019 17:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 13JUL2019 22:00 and ends at 16JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 16JUL2019 22:00 and ends at 31JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2019 22:00 and ends at 04AUG2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall pass on leg 1 on trip 3 on roster 1


  @SCENARIO4
  Scenario: SKN FD passes early checkout
    Given Tracking
    Given planning period from 1JUL2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 28JAN2014  | 01JAN2036 |
           | region          | SKI        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | FP         | 28JAN2014  | 01JAN2036 |
           | contract        | V00004     | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+A3" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2019 09:10 | 11JUL2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2019 22:55 | 13JUL2019 06:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position FP

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 13JUL2019 22:00 and ends at 16JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 16JUL2019 22:00 and ends at 31JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2019 22:00 and ends at 03AUG2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO5
  Scenario: SKN FD fails late checkout
    Given Tracking
    Given planning period from 1JUL2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 28JAN2014  | 01JAN2036 |
           | region          | SKI        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | FC         | 28JAN2014  | 01JAN2036 |
           | contract        | V00004     | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2019 09:10 | 11JUL2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2019 22:55 | 13JUL2019 17:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 13JUL2019 22:00 and ends at 16JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 16JUL2019 22:00 and ends at 31JUL2019 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2019 22:00 and ends at 03AUG2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall fail on leg 1 on trip 3 on roster 1

@SCENARIO6
Scenario: SKN CC vacation period start after MON 23rd week and sunday of 37th week.
    Given Tracking
    Given planning period from 1JAN2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 28JAN2014  | 01JAN2036 |
           | region          | SKN        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | AH         | 28JAN2014  | 01JAN2036 |
           | contract        | SNK_V301   | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 11JUL2020 09:10 | 11JUL2020 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 12JUL2020 22:55 | 13JUL2020 06:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 15JUL2020 22:00 and ends at 31JUL2020 22:00
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 31JUL2020 22:00 and ends at 03AUG2020 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall pass on leg 1 on trip 1 on roster 1
    and rave "freedays.%is_summer_vacation%(True)" shall be "True" on leg 1 on trip 2 on roster 1
@SCENARIO7
Scenario: SKN CC fails vacation period start before 23rd week and sunday of 37th week.
    Given Tracking
    Given planning period from 1MAY2019 to 31AUG2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 28JAN2014  | 01JAN2036 |
           | region          | SKN        | 28JAN2014  | 01JAN2036 |
           | base            | OSL        | 28JAN2014  | 01JAN2036 |
           | title rank      | AH         | 28JAN2014  | 01JAN2036 |
           | contract        | SNK_V301     | 01OCT2015  | 01JAN2036 |
           | published       | 01MAR2021  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+AL" from 10JUN2016 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000907  | OSL     | EWR     | 27MAY2019 09:10 | 28MAY2019 17:15 | 33B     |         |
           | leg     | SK      | 000908  | EWR     | OSL     | 29MAY2019 22:55 | 30MAY2019 17:20 | 33B     |         |
    Given trip 1 is assigned to crew member 1 in position AH
     
    Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 01JUN2019 00:00 and ends at 19JUN2019 22:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 19JUN2019 22:00 and ends at 23JUN2019 22:00

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_check_out_before_summer_va" shall pass on leg 1 on trip 2 on roster 1
    and rave "freedays.%is_summer_vacation%(True)" shall be "False" on leg 1 on trip 2 on roster 1