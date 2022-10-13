@TRACKING @LPC @CCQ @FD
Feature: Check if CCQ Skill test rule has valid LPC document

  Background: set up for tracking
    Given Tracking
    Given planning period from 1SEP2019 to 1OCT2019

    @SCENARIO1_A2A3
    Scenario: Check if A3 CCQ Skill test should be performed before expiry of original LPC doc
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A3" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019
    Given crew member 1 has document "REC+LPC" from 01SEP2019 to 30JUN2020 and has qualification "A2"

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto    | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019  | CCQ from SH | LIFUS     | 2       | 0       | A3     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S6      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO1_A2A5
    Scenario: Check if A5 CCQ Skill test should be performed before expiry of original LPC doc
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A5" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019
    Given crew member 1 has document "REC+LPC" from 01SEP2019 to 30JUN2020 and has qualification "A2"

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto    | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019  | CCQ from SH | LIFUS     | 2       | 0       | A5     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S5      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO2_A2A3
    Scenario: Missing LPCA2 document at A3 CCQ
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A3" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto   | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019 | CCQ from SH | LIFUS     | 2       | 0       | A3     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S6      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO2_A2A5
    Scenario: Missing LPCA2 document at A5 CCQ
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A5" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto   | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019 | CCQ from SH | LIFUS     | 2       | 0       | A5     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S5      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO3_A2A3
    Scenario: A3 CCQ crew has no valid lpc document on september
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A3" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019
    Given crew member 1 has document "REC+LPC" from 01OCT2019 to 25NOV2020 and has qualification "A2"

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto   | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019 | CCQ from SH | LIFUS     | 2       | 0       | A3     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S6      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall fail on leg 1 on trip 1 on roster 1


    @SCENARIO3_A2A5
    Scenario: A5 CCQ crew has no valid lpc document on september
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A5" from 09SEP2019 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+SMI" from 22JUL2017 to 31AUG2020
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019
    Given crew member 1 has document "REC+LPC" from 01OCT2019 to 25NOV2020 and has qualification "A2"

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto   | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019 | CCQ from SH | LIFUS     | 2       | 0       | A5     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S5      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall fail on leg 1 on trip 1 on roster 1



    @SCENARIO4_A3A5A2
Scenario: Check if A2 CCQ Skill test should be performed before expiry of original LPC doc
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 26MAY2008  | 09SEP2019 |
           | base            | CPH        | 26MAY2008  | 09SEP2019 |
           | region          | SKI        | 09SEP2019  | 20OCT2019 |
           | base            | CPH        | 09SEP2019  | 20OCT2019 |
           | title rank      | FC         | 09SEP2019  | 20OCT2019 |
    Given crew member 1 has qualification "ACQUAL+A3" from 26MAR2008 to 09SEP2019
    Given crew member 1 has qualification "ACQUAL+A5" from 15JUL2008 to 18OCT2019
    Given crew member 1 has restriction "TRAINING+DCT" from 09SEP2019 to 25NOV2019
    Given crew member 1 has document "REC+LPCA3A5" from 15SEP2008 to 09DEC2019

    Given table crew_training_need additionally contains the following
    | crew           | part | validfrom | validto    | course      | attribute | flights | maxdays | acqual |
    | crew member 1  | 1    | 09Sep2019 | 29Nov2019  | CCQ from SH | LIFUS     | 2       | 0       | A2     |

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | ground  |         |         | CPH     | CPH     | 29SEP2019 02:30 | 29SEP2019 07:30 |         | S5      |
    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SKILL TEST"

    When I show "crew" in window 1
    Then rave "rules_training_ccr.%prev_typerate_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_ccq_skilltest_requires_valid_lpc_doc" shall pass on leg 1 on trip 1 on roster 1

