@planning @tracking
# Jira and SKCMS-2119

Feature: Test that new hire with lacking experience is paired with TRI qualified instructor

  Background: set up
    Given Rostering_FC
    Given planning period from 1feb2018 to 28feb2018

  @SCENARIO1 @LIFUS
  Scenario: Check that rule is legal when pilot has TRI and trainee is new hire

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018

    Given crew member 1 has the following training need
    | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | FULL TR plus OCC | LC         | 01FEB2018  | 28FEB2018  | 4       | 0        | A3     |

    Given crew member 1 has restriction "TRAINING+FOC" from 1FEB2018 to 28FEB2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2018
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2018
    Given crew member 3 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |




    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 3 in position FU

    When I show "crew" in window 1
    and I load rule set "Rostering_FC"
    Then the rule "rules_training_ccr.trng_unexperienced_lifus_trainee_require_supernum_fp" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2 @LIFUS
  Scenario: Check that rule fails if pilot instructor does not have TRI when trainee is new hire

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2018

    Given crew member 1 has the following training need
    | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | FULL TR plus OCC | LC         | 01FEB2018  | 28FEB2018  | 4       | 0        | A3     |

    Given crew member 1 has restriction "TRAINING+FOC" from 1FEB2018 to 28FEB2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |



    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"

    When I show "crew" in window 1
    and I load rule set "Rostering_FC"
    Then the rule "rules_training_ccr.trng_unexperienced_lifus_trainee_require_supernum_fp" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO3 @LIFUS
  Scenario: Check that rule fails if pilot instructor does not have TRI when trainee is new hire

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 28FEB2018

    Given crew member 1 has the following training need
    | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | FULL TR plus OCC | LC         | 01JAN2018  | 28FEB2018  | 4       | 0        | A3     |

    Given crew member 1 has restriction "TRAINING+FOC" from 1JAN2018 to 28FEB2018


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2075 |            |          |
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1FEB2018 to 28FEB2018

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 01FEB2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | 320    |

    Given table crew_training_log additionally contains the following
         | crew          | typ   | code | tim             |
         | crew member 1 | LIFUS | A2   | 25JAN2018 10:00 |
         | crew member 1 | LIFUS | A2   | 25JAN2018 12:00 |
         | crew member 1 | LIFUS | A2   | 26JAN2018 10:00 |
         | crew member 1 | LIFUS | A2   | 26JAN2018 12:00 |


    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"

    When I show "crew" in window 1
    and I load rule set "Rostering_FC"
    and I set parameter "fundamental.%start_para%" to "1FEB2018 00:00"
    and I set parameter "fundamental.%end_para%" to "28FEB2018 00:00"
    and I set parameter "training.%number_lifus_legs_extra_guidance_need_for_trainee_extra_fu_need%" to "5"
    Then the rule "rules_training_ccr.trng_unexperienced_lifus_trainee_require_supernum_fp" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_unexperienced_lifus_trainee_require_supernum_fp" shall pass on leg 2 on trip 1 on roster 1
