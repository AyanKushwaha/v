@TRACKING @PLANNING @ROSTERING
Feature: 60h rest after 3 or 4 production days.
# Developer: William Nilsson, william.nilsson@hiq.se
# Date: 2019-11
############
# SKCMS-2268
# updated 2019-12-10 by oscargr
############

  @SCENARIO_01_SKN @tracking
  Scenario: Rule shall fail if checked in studio tracking and 3 p days and break less than 60h.

    Given Tracking
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 07:00 | 11:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall fail on leg 2 on trip 3 on roster 1

###############################################################################################################################

  @SCENARIO_01_SKD @tracking
  Scenario: Rule shall pass if checked in studio tracking and 3 p days and break less than 60h.

    Given Tracking
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | CPH       |
    | title rank      | AH        |
    | region          | SKD       |
    | contract        | V300      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | CPH     | OSL     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | OSL     | CPH     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | CPH     | OSL     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | OSL     | CPH     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | CPH     | OSL     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | OSL     | CPH     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | CPH     | OSL     | 08SEP2021 | 07:00 | 11:00 | SK  |
    | leg | 0008 | OSL     | CPH     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "False" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall pass on leg 2 on trip 3 on roster 1

###############################################################################################################################

  @SCENARIO_02 @tracking
  Scenario: Rule shall pass if checked in studio tracking and 4 p days and break more than 60h.

    Given Tracking
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0009 | OSL     | CPH     | 02SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0010 | CPH     | OSL     | 02SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 06SEP2021 22:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 06SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 5 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 4 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall pass on leg 2 on trip 4 on roster 1

###############################################################################################################################

  @SCENARIO_03 @tracking
  Scenario: Rule shall fail if checked in studio tracking and 4 p days and break less than 60h.

    Given Tracking
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0009 | OSL     | CPH     | 02SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0010 | CPH     | OSL     | 02SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 06SEP2021 22:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 06SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 07:00 | 11:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 5 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 4 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall fail on leg 2 on trip 4 on roster 1

###############################################################################################################################

  @SCENARIO_04 @tracking
  Scenario: Rule shall pass if checked in studio tracking and 4 p days and break less than 60h.

    Given Tracking
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0009 | OSL     | CPH     | 02SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0010 | CPH     | OSL     | 02SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 06SEP2021 22:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 06SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 07:00 | 11:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 5 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 4 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall pass on leg 2 on trip 4 on roster 1

###############################################################################################################################

  @SCENARIO_05 @planning
  Scenario: Rule shall fail if checked in studio planning and 3 p days and break less than 60h.

    Given Rostering_CC
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 07:00 | 09:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall fail on leg 2 on trip 3 on roster 1

###############################################################################################################################

  @SCENARIO_06 @planning
  Scenario: Rule shall fail if checked in studio planning and 4 p days and break less than 60h.

    Given Rostering_CC
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0009 | OSL     | CPH     | 02SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0010 | CPH     | OSL     | 02SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00


    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 08SEP2021 | 07:00 | 09:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 08SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 5 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 4 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall fail on leg 2 on trip 4 on roster 1

###############################################################################################################################

  @SCENARIO_07 @planning
  Scenario: Rule shall pass if checked in studio planning and 3 p days and break more than 60h.

    Given Rostering_CC
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 07SEP2021 | 09:00 | 10:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 07SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 3 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall pass on leg 2 on trip 3 on roster 1

###############################################################################################################################

  @SCENARIO_08 @planning
  Scenario: Rule shall pass if checked in studio planning and 4 p days and break more than 60h.

    Given Rostering_CC
    Given planning period from 01SEP2021 to 30SEP2021

    Given a crew member with
    | attribute       | value     |
    | base            | OSL       |
    | title rank      | AH        |
    | region          | SKN       |
    | contract        | V301      |

    Given crew member 1 has qualification "ACQUAL+38" from 1FEB2021 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0009 | OSL     | CPH     | 02SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0010 | CPH     | OSL     | 02SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0001 | OSL     | CPH     | 03SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0002 | CPH     | OSL     | 03SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 2 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0003 | OSL     | CPH     | 04SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0004 | CPH     | OSL     | 04SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 3 is assigned to crew member 1 in position AH

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0005 | OSL     | CPH     | 05SEP2021 | 10:00 | 11:00 | SK  |
    | leg | 0006 | CPH     | OSL     | 05SEP2021 | 18:00 | 20:00 | SK  |
    Given trip 4 is assigned to crew member 1 in position AH

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 05SEP2021 22:00 and ends at 07SEP2021 22:00


    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car |
    | leg | 0007 | OSL     | CPH     | 07SEP2021 | 09:00 | 10:00 | SK  |
    | leg | 0008 | CPH     | OSL     | 07SEP2021 | 12:00 | 13:00 | SK  |
    Given trip 5 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then rave "rules_indust_ccr.%wop_day_limit%" shall be "True" on leg 2 on trip 4 on roster 1
    and the rule "rules_indust_ccr.ind_min_rest_after_4_or_3_prod_days" shall pass on leg 2 on trip 4 on roster 1

##################################################################################################################


