Feature: Test that number of short haul(SH) days before long haul to (1) and max FDP 11h/9:30h CC SKD
    Background: A change to max number of SH days before LH to 1  amd max FDP 11h/9:30h have been implemented in SKCMS-1879.

    ###################################################################################
    @SCENARIO1
    Scenario: Check that rule ind_max_sh_duty_days_before_lh is successful, when crew is SKD and maximum short haul days
              before long equal to 1 (SH-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 16DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO2
    Scenario: Check that rule ind_max_sh_duty_days_before_lh is successful, when crew is SKD and maximum short haul days
              before long equal to 1 (STBY-SH-LH)
    # This is tested for Rostering CC because the standby is not considered an SH trip in tracking.
    Given Rostering_CC
    Given planning period from 1dec2018 to 31dec2018
    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"
    and crew member 1 has a personal activity "A" at station "CPH" that starts at 14DEC2018 07:00 and ends at 14DEC2018 15:00

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 16DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |

    # Please note that Behaviour framework does not count the standby trip created using
    # crew member 1 has a personal activity "A" at station "CPH" that starts at 16DEC2018 07:00 and ends at 16DEC2018 15:00
    # So the rave trip numbers are not same as the behaviour trip numbers

    #               |---------------------------|
    #               |   STBY | SH      |   LH   |
    #-------------------------------------------|
    # RAVE TRIP     |    1   |   2     |   3    |
    #---------------|--------|---------|--------|
    # BEHAVE  TRIP  |        |    1    |   2    |
    #---------------|--------|---------|--------|

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 2 on roster 1

    and rave "crew.%is_skd%" shall be "True" on leg 1 on trip 3 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 3 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 3 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 2 on trip 3 on roster 1

    ###################################################################################
    @SCENARIO3
    Scenario: Check that rule ind_max_sh_duty_days_before_lh is unsuccessful, when creating trip combination (SH-SH-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 16DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 16DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0006 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH
    Given trip 3 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 2 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 3 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 3 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 3 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 2 on trip 3 on roster 1

    ###################################################################################
    @SCENARIO4
    Scenario: Check that it is not allowed to create trip combination (SH-STBY-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    # Please note that Behaviour framework does not count the standby trip created using
    # crew member 1 has a personal activity "A" at station "CPH" that starts at 16DEC2018 07:00 and ends at 16DEC2018 15:00
    # So the rave trip numbers are not same as the behaviour trip numbers

    #               |---------------------------|
    #               |   SH   | STBY   |   LH    |
    #-------------------------------------------|
    # RAVE TRIP     |    1   |   2     |   3    |
    #---------------|--------|---------|--------|
    # BEHAVE  TRIP  |    1   |         |   2    |
    #---------------|--------|---------|--------|

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH
    #Given trip 3 is assigned to crew member 1 in position AH
    and crew member 1 has a personal activity "A" at station "CPH" that starts at 16DEC2018 07:00 and ends at 16DEC2018 15:00

    Given crew member 1 has a personal activity "A" at station "STO" that starts at 16DEC2018 07:00 and ends at 16DEC2018 15:00

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1

    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 3 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 1 on trip 3 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 3 on roster 1

    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall fail on leg 2 on trip 3 on roster 1

    ##################################################################################
    @SCENARIO5
    Scenario: Check that it is allowed to create trip combination (SH-LH) as legacy
    Given Rostering_CC
    Given planning period from 1jan2018 to 31jan2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 16JAN2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 16JAN2018 | 14:00 | 17:30 | SK  | 320    |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 17JAN2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0004 | BRU     | CPH     | 18JAN2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO6
    Scenario: FDP less than 11 for SH before LH causes the rule ind_max_sh_fdp_before_lh_CC to pass (SH-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31DEC2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0004 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "fdp.%scheduled_time%" shall be "10:20" on leg 1 on trip 1 on roster 1
    and rave "fdp.%scheduled_time%" shall be "10:20" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "fdp.%scheduled_time%" shall be "9:20" on leg 1 on trip 2 on roster 1
    and rave "fdp.%scheduled_time%" shall be "9:30" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "10:20" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "0:00" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO7
    Scenario: FDP less than 11 for SH before LH causes the rule ind_max_sh_fdp_before_lh_CC to pass (SH-SH-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 16DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 16DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0006 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH
    Given trip 3 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "fdp.%scheduled_time%" shall be "10:20" on leg 1 on trip 1 on roster 1
    and rave "fdp.%scheduled_time%" shall be "10:20" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 2 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 3 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 3 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 3 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "10:20" on leg 1 on trip 3 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "0:00" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 3 on roster 1

    ###################################################################################
    @SCENARIO8
    Scenario: FDP greater than 11 for SH before LH causes the rule ind_max_sh_fdp_before_lh_CC to fail (SH-LH)
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018


    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 16DEC2018 | 07:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 16DEC2018 | 14:00 | 18:30 | SK  | 320    |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0004 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    #and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "12:20" on leg 1 on trip 1 on roster 1
    #and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "12:20" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "12:20" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "0:00" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO9
    Scenario: Check that it is allowed to create trip combination (SH-LH) as legacy when region is not SKD
    Given Rostering_CC
    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKN       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 15JAN2018 | 0:00 | 11:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 15JAN2018 | 14:00 | 17:30 | SK  | 320    |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 17JAN2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0004 | BRU     | CPH     | 18JAN2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "crew.%is_skd%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%max_sh_days_before_lh%" shall be "1" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_duty_days_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO10
    Scenario: FDP greater than 11 for SH before LH causes the rule ind_max_sh_fdp_before_lh_CC to fail (SH-SH-LH)
    Given Rostering_CC

    Given planning period from 1jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr  | car | ac_typ |
    | leg | 0001 | CPH     | BRU     | 16DEC2018 | 02:00 | 4:30 | SK  | 320    |
    | leg | 0002 | BRU     | CPH     | 16DEC2018 | 06:00 | 8:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | BRU     | 16DEC2018 | 11:00 | 13:30 | SK  | 320    |
    | leg | 0004 | BRU     | CPH     | 16DEC2018 | 15:00 | 17:30 | SK  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | CPH     | BRU     | 17DEC2018 | 08:00 | 16:30 | SK  | 320    |
    | leg | 0006 | BRU     | CPH     | 18DEC2018 | 08:00 | 16:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH
    Given trip 3 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 1 on roster 1

    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 2 on roster 1
    and rave "crew.%is_skd%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 1 on trip 2 on roster 1
    and rave "trip.%is_standby%" shall be "False" on leg 2 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "16:20" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "0:00" on leg 2 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall pass on leg 2 on trip 2 on roster 1

    ###################################################################################
    @SCENARIO11
    Scenario: FDP greater than 11 for first LH and FDP for SH lower than 9:30 causes the rule ind_max_sh_fdp_before_lh_CC to pass (SH-LH)
    Given Rostering_CC

    Given planning period from 1oct2020 to 31oct2020

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          | SKD       |            |          |
    Given crew member 1 has contract "V200"


    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000539  | CPH     | MAN     | 06OCT2020 06:30 | 06OCT2020 08:35 | 32N     |         |
           | leg     | SK      | 000540  | MAN     | CPH     | 06OCT2020 09:15 | 06OCT2020 11:05 | 32N     |         |
           | leg     | SK      | 001217  | CPH     | AAL     | 06OCT2020 14:30 | 06OCT2020 15:15 | 32N     |         |
           | leg     | SK      | 001218  | AAL     | CPH     | 06OCT2020 15:40 | 06OCT2020 16:25 | 32N     |         |
    Given trip 1 is assigned to crew member 1 in position AH

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000935  | CPH     | SFO     | 08OCT2020 10:05 | 08OCT2020 21:20 | 33A     |         |
           | leg     | SK      | 000936  | SFO     | CPH     | 10OCT2020 23:10 | 11OCT2020 09:50 | 33A     |         |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    Then rave "crew.%is_skd%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "rules_indust_ccr.%sh_fdp_before_lh%" shall be "10:45" on leg 1 on trip 2 on roster 1
    and rave "rules_indust_ccr.%first_lh_fdp%" shall be "12:35" on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.ind_max_sh_fdp_before_lh" shall fail on leg 1 on trip 2 on roster 1
