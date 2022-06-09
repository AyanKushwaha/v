Feature: JCRT OM: ILC at Commander Upgrade requires normal crew composition
  Background: set up for tracking
    Given Tracking


    ##############################################################################
    @FP_PASS_1
    Scenario: Case passes if FP is assigned to FP position during Skill test

    Given planning period from 1JAN2019 to 31JAN2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FP      |             |           |
    | region     | SKS     |             |           |

    Given crew member 1 has restriction "TRAINING+CAPT" from 1JAN2019 to 31DEC2019

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S2   | ARN     | ARN     | 9Jan2019  | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ILC"
    #Given crew member 1 has restriction "TRAINING+CAPT" from 1JAN2019 to 31DEC2019

    When I show "crew" in window 1
    Then rave "leg.%is_ilc%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1


    ##############################################################################
    @FP_FAIL_1
    Scenario: Case fail if FC is assigned to FP position during Skill test

    Given planning period from 1JAN2019 to 31JAN2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FC      |             |           |
    | region     | SKS     |             |           |

    #Given crew member 1 has acqual restriction "ACQUAL+AL+TRAINING+CAPT" from 1JAN2019 to 31DEC2019
    Given crew member 1 has restriction "TRAINING+CAPT" from 1JAN2019 to 31DEC2019

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S2   | ARN     | ARN     | 9Jan2019  | 00:00 | 23:59 |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ILC"
    #Given crew member 1 has restriction "TRAINING+CAPT" from 1JAN2019 to 31DEC2019

    When I show "crew" in window 1
    Then rave "leg.%is_ilc%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 1


    ##############################################################################
