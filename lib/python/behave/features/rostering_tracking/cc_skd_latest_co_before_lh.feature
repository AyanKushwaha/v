@PLANNING @ROSTERING @CC @SDK
Feature: Test rule that checks that SKD CC checkout before midnight the day before a long haul trip.
##############
# SKCMS-2516 #
##############
 Background:
 Given planning period from 1SEP2020 to 30SEP2020
 Given Rostering_CC

 Given table agreement_validity additionally contains the following
 | id                   | validfrom | validto  |
 | K20_cau_co_before_LH | 1SEP2020  | 1OCT2020 |

 Given a crew member with
 | attribute       | value     | valid from | valid to  |
 | base            | CPH       |            |           |
 | title rank      | AH        |            |           |
 | region          | SKD       |            |           |
 | contract        | F00660    | 05OCT2019  | 31DEC2035 |

######################################################################################

  @SCENARIO1
  Scenario:  Rule should fail when crew has LH trip after checkout after 00:00 same day


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 04SEP2020 00:00 | 04SEP2020 01:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################


  @SCENARIO2
  Scenario:  Rule should pass when crew has LH trip after checkout at 23:59 previous day


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 03SEP2020 20:00 | 03SEP2020 21:44 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################

   @SCENARIO3
  Scenario:  Rule should fail when crew has checkout at 00:01 same day as lh


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 03SEP2020 20:00 | 03SEP2020 21:46 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################
  @SCENARIO4
  Scenario:  Rule should fail when crew has LH trip after checkout after 00:00 same day, and trip starts previous day


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 03SEP2020 23:00 | 04SEP2020 01:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################
   @SCENARIO5
  Scenario:  Rule should pass when crew check-out on midnight before LH trip


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 03SEP2020 21:00 | 03SEP2020 21:45 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 1 on trip 2 on roster 1
 #########################################################################################
   @SCENARIO6
  Scenario:  Rule should pass when checkout is after midnight, but activity is not duty

    Given crew member 1 has a personal activity "F" at station "CPH" that starts at 03SEP2020 08:00 and ends at 04SEP2020 01:00

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 1 on trip 2 on roster 1

 ##########################################################################################
  @SCENARIO7
  Scenario:  Rule should pass when crew has LH trip with checkout after midnight


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | EWR     | 03SEP2020 12:00 | 04SEP2020 01:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 1 on trip 2 on roster 1

 ##########################################################################################
  @SCENARIO8
  Scenario:  Rule should pass when crew has LH trip with checkout after midnight and crew has activity H in between LH trips


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2020 10:00 | 03SEP2020 11:00 | SK  |
    | leg | 0002 | OSL     | EWR     | 03SEP2020 12:00 | 04SEP2020 01:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "H" at station "CPH" that starts at 04SEP2020 08:00 and ends at 04SEP2020 09:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 1 on trip 2 on roster 1

##########################################################################################
   @SCENARIO9
  Scenario:  Rule should pass when crew check-out on midnight before SH duty


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0002 | OSL     | CPH     | 03SEP2020 21:00 | 03SEP2020 21:45 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0003 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0004 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 2 on trip 2 on roster 1
 
 ##########################################################################################
  @SCENARIO10
  Scenario:  Rule should fail when crew has LH trip after checkout after 00:00 same day, and duty starts previous day


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2020 23:00 | 04SEP2020 01:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0002 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0003 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall fail on leg 1 on trip 2 on roster 1

##########################################################################################
  @SCENARIO11
  Scenario:  Rule should pass when crew check-out on midnight before LH trip


   Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2020 21:00 | 03SEP2020 21:45 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | dep             | arr             | car |
    | leg | 0002 | CPH     | EWR     | 04SEP2020 10:00 | 04SEP2020 20:00 | SK  |
    | leg | 0003 | EWR     | CPH     | 05SEP2020 22:00 | 06SEP2020 04:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_latest_checkout_before_lh_skd_cc" shall pass on leg 2 on trip 2 on roster 1
 #########################################################################################