@TRACKING @PLANNING @FD
# SKCMS-2052 and SKCMS-2074

Feature: Test standard connection times before and after flight training duty.

##############################################################################
  Background: Setup common data

    Given Tracking

    Given planning period from 1MAR2020 to 1APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FP    |
      | title rank | FP    |
      | region     | SKS   |
      | base       | STO   |

  Given table cnx_time_training is overridden with the following
      | cnx_type           | leg_end_station | ac_type | min_training_cnx_time | validfrom | validto   |
      | PASSTOSIM          | CPH             | N/A     | 00:45                 | 01JAN2020 | 31DEC2035 |
      | PASSTOSIM          | CPH             | N/A     | 00:45                 | 01JAN1986 | 31DEC2019 |
      | PASSTOSIM          | -               | N/A     | 02:00                 | 01JAN1986 | 31DEC2035 |
      | SIMTOPASS          | -               | N/A     | 00:45                 | 01JAN1986 | 31DEC2035 |
      | PASSTOLIFUS        | N/A             | -       | 01:00                 | 01JAN1986 | 31DEC2035 |
      | PASSTOLIFUS        | N/A             | A3      | 01:30                 | 01JAN1986 | 31DEC2035 |
      | LIFUSTOPASS        | N/A             | -       | 01:00                 | 01JAN1986 | 31DEC2035 |
      | LIFUSTOPASS        | N/A             | A3      | 01:30                 | 01JAN1986 | 31DEC2035 |
      | LCTOILC            | N/A             | -       | 02:45                 | 01JAN1986 | 31DEC2035 |
      | ILCTOLC            | N/A             | -       | 02:45                 | 01JAN1986 | 31DEC2035 |
      | LCTOILC            | N/A             | A3      | 01:45                 | 01JAN1986 | 31DEC2035 |
      | ILCTOLC            | N/A             | A3      | 01:45                 | 01JAN1986 | 31DEC2035 |
      | LCTOACT            | N/A             | -       | 01:00                 | 01JAN1986 | 31DEC2035 |
      | LCTOACT            | N/A             | A2      | 01:30                 | 01JAN1986 | 31DEC2035 |
      | TOLC               | N/A             | -       | 01:15                 | 01JAN1986 | 31DEC2035 |
      | TOLC               | N/A             | A2      | 00:45                 | 01JAN1986 | 31DEC2035 |
      | PASSTOSCHOOLFLIGHT | N/A             | -       | 01:20                 | 01JAN1986 | 31DEC2035 |
      | SCHOOLFLIGHTTOPASS | N/A             | -       | 01:20                 | 01JAN1986 | 31DEC2035 |
      | PASSTOZFTTX        | N/A             | A3      | 01:20                 | 01JAN1986 | 31DEC2035 |
      | PASSTOZFTTX        | N/A             | A4      | 01:20                 | 01JAN1986 | 31DEC2035 |
      | PASSTOZFTTX        | N/A             | -       | 01:20                 | 01JAN1986 | 31DEC2035 |
      | LCTOLC             | N/A             | -       | 02:10                 | 01JAN1986 | 31DEC2035 |
      | LCTOILC            | N/A             | -       | 02:45                 | 01JAN1986 | 31DEC2035 |
      | ILCTOILC           | N/A             | -       | 02:45                 | 01JAN1986 | 31DEC2035 |
      | ILCTOLC            | N/A             | -       | 02:45                 | 01JAN1986 | 31DEC2035 |
      | LCTOPASS           | N/A             | -       | 01:30                 | 01JAN1986 | 31DEC2035 |
      | TOILC              | N/A             | -       | 01:15                 | 01JAN1986 | 31DEC2035 |
      | ILCTOPASS          | N/A             | -       | 01:30                 | 01JAN1986 | 31DEC2035 |
      | ILCTOACT           | N/A             | -       | 01:45                 | 01JAN1986 | 31DEC2035 |
      | SUPERNUMTOPASS     | N/A             | -       | 01:15                 | 01JAN1986 | 31DEC2035 |
      | PASSTOSUPERNUM     | N/A             | -       | 01:20                 | 01JAN1986 | 31DEC2035 |
      | FAMFLTTOPASS       | N/A             | -       | 01:15                 | 01JAN1986 | 31DEC2035 |
      | PASSTOFAMFLT       | N/A             | -       | 01:20                 | 01JAN1986 | 31DEC2035 |

##############################################################################

  @SCENARIO1
  Scenario: Test PASSTOSIM and SIMTOPASS connections. Uses the airport specific row (CPH) and ignores default rows and
  invalid rows (validto is before duty start) in table.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020


    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | title rank | FC    |            |          |
      | region     | SKS   |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | date      | dep   | arr   | num  | car |
      | dh     | FLT  | ARN     | CPH     | 10MAR2020 | 06:00 | 07:00 | 0001 | SK  |
      | ground | S2   | CPH     | CPH     | 10MAR2020 | 11:00 | 13:00 | 0002 | SK  |
      | ground | S2   | CPH     | CPH     | 10MAR2020 | 15:00 | 17:00 | 0003 | SK  |
      | dh     | FLT  | CPH     | ARN     | 10MAR2020 | 17:30 | 18:30 | 0004 | SK  |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | date      | dep   | arr   | num  | car |
      | dh     | FLT  | ARN     | CPH     | 15MAR2020 | 09:30 | 10:30 | 0001 | SK  |
      | ground | S2   | CPH     | CPH     | 15MAR2020 | 11:00 | 13:00 | 0002 | SK  |
      | ground | S2   | CPH     | CPH     | 15MAR2020 | 15:00 | 17:00 | 0003 | SK  |
      | dh     | FLT  | CPH     | ARN     | 15MAR2020 | 21:00 | 22:00 | 0004 | SK  |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1
    Given trip 1 is assigned to crew member 2 in position 10
    Given trip 2 is assigned to crew member 2 in position 10

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSIM" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSIM" on leg 1 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SIMTOPASS" on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SIMTOPASS" on leg 3 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSIM" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSIM" on leg 1 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "SIMTOPASS" on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "SIMTOPASS" on leg 3 on trip 2 on roster 2

##############################################################################

  @SCENARIO2
  Scenario: Test PASSTOLIFUS and LIFUSTOPASS connections. Uses the default aircraft row (-) in table and ignore aircraft specific rows.
  Connection times should be applied both to trainee and instructor.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | title rank | FC    |            |          |
      | region     | SKS   |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2018 to 31JUL2020
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 10MAR2020 | 18:15 | 20:15 | SK  | 320    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 15MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 15MAR2020 | 17:45 | 19:45 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 2 on roster 2

##############################################################################

  @SCENARIO3
  Scenario: Test TOLC and LCTOACT connections. Uses the aircraft specific row (A2) in table.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | OSL   |            |          |
      | region     | SKN   |            |          |
      | title rank | FC    |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | ARN     | CPH     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | CPH     | OSL     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | OSL     | CPH     | 10MAR2020 | 15:00 | 17:00 | SK  | 320    |
      | leg | 0004 | CPH     | ARN     | 10MAR2020 | 18:15 | 20:15 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FP with
      | type      | leg | name     | value |
      | attribute | 2-3 | TRAINING | LC    |

    Given trip 1 is assigned to crew member 2 in position FC with
      | type      | leg | name       | value |
      | attribute | 2-3 | INSTRUCTOR | LC    |

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "TOLC" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "LCTOACT" on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "TOLC" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "LCTOACT" on leg 3 on trip 1 on roster 2

##############################################################################


  @SCENARIO4
  Scenario: Test calculation of SIM connection types.
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a trip with the following activities
      | act    | num  | code | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh     | 0001 | FLT  | ARN     | CPH     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | ground | 0002 | S2   | CPH     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | ground | 0003 | S2   | CPH     | CPH     | 10MAR2020 | 15:00 | 17:00 | SK  | 320    |
      | dh     | 0004 | FLT  | CPH     | ARN     | 10MAR2020 | 18:15 | 20:15 | SK  | 320    |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    Then rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSIM" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SIMTOPASS" on leg 3 on trip 1 on roster 1

##############################################################################

  @SCENARIO5
  Scenario: Test calculation of school flight connection types.
    Given a crew member with
      | attribute  | value     | valid from | valid to |
      | base       | STO       |            |          |
      | title rank | FC        |            |          |
      | region     | SKS       |            |          |
      | published  | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JAN2019 to 31DEC2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | OSL     | 10MAR2020 | 08:00 | 09:00 | SK  | 320    |
      | leg | 9160 | OSL     | LHR     | 10MAR2020 | 10:00 | 11:00 | SK  | 320    |
      | leg | 9161 | LHR     | OSL     | 10MAR2020 | 12:00 | 13:00 | SK  | 320    |
      | dh  | 0004 | OSL     | ARN     | 10MAR2020 | 14:30 | 15:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 2 in position FC
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSCHOOLFLIGHT" on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SCHOOLFLIGHTTOPASS" on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSCHOOLFLIGHT" on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SCHOOLFLIGHTTOPASS" on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2

############################################################################## ,

  @SCENARIO6
  Scenario: Test TOILC and ILCTOACT connections. Uses the aircraft specific row (A2) in table.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | OSL   |            |          |
      | region     | SKN   |            |          |
      | title rank | FC    |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | ARN     | CPH     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | CPH     | OSL     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | OSL     | CPH     | 10MAR2020 | 15:00 | 17:00 | SK  | 320    |
      | leg | 0004 | CPH     | ARN     | 10MAR2020 | 18:45 | 20:15 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FP with
      | type      | leg | name     | value |
      | attribute | 2-3 | TRAINING | ILC   |

    Given trip 1 is assigned to crew member 2 in position FC with
      | type      | leg | name       | value |
      | attribute | 2-3 | INSTRUCTOR | ILC   |

    When I show "crew" in window 1
   Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "TOILC" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOACT" on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "TOILC" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOACT" on leg 3 on trip 1 on roster 2


##############################################################################

  @SCENARIO7
  Scenario: Test PASSTOZFTTX connections
  Connection times should be applied both to trainee and instructor.

    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | region     | SKS   |            |          |
      | title rank | FC    |            |          |

    Given crew member 2 has qualification "ACQUAL+A3" from 1JUL2018 to 31JUL2020
    Given crew member 2 has acqual qualification "ACQUAL+A3+INSTRUCTOR+LIFUS" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:30 | 11:00 | SK  | 320    |


    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT X"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ZFTT X"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT X"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ZFTT X"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 2 on roster 2


##############################################################################

 @SCENARIO8
 Scenario: Test combinations of ILC and LC

     Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

     Given another crew member with
       | attribute  | value | valid from | valid to |
       | base       | OSL   |            |          |
       | title rank | FC    |            |          |
       | region     | SKN   |            |          |

     Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

     Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | ARN     | CPH     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | CPH     | OSL     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | OSL     | CPH     | 10MAR2020 | 12:00 | 13:00 | SK  | 320    |
      | leg | 0004 | CPH     | ARN     | 10MAR2020 | 14:15 | 15:15 | SK  | 320    |
      | leg | 0005 | ARN     | OSL     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |

       Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | ARN     | CPH     | 12MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | CPH     | OSL     | 12MAR2020 | 11:00 | 12:00 | SK  | 320    |
      | leg | 0003 | OSL     | CPH     | 12MAR2020 | 15:00 | 16:00 | SK  | 320    |
      | leg | 0004 | CPH     | ARN     | 12MAR2020 | 19:15 | 20:15 | SK  | 320    |
      | leg | 0005 | ARN     | OSL     | 12MAR2020 | 23:00 | 23:45 | SK  | 320    |

     Given trip 1 is assigned to crew member 1 in position FP with
      | type      | leg | name     | value |
      | attribute | 1-2 | TRAINING | LC    |
      | attribute | 3-4 | TRAINING | ILC   |
      | attribute | 5   | TRAINING | LC    |

     Given trip 1 is assigned to crew member 2 in position FC with
      | type      | leg | name       | value |
      | attribute | 1-2 | INSTRUCTOR | LC    |
      | attribute | 3-4 | INSTRUCTOR | ILC   |
      | attribute | 5   | INSTRUCTOR | LC    |


    Given trip 2 is assigned to crew member 1 in position FP with
      | type      | leg | name     | value |
      | attribute | 1-2 | TRAINING | LC    |
      | attribute | 3-4 | TRAINING | ILC   |
      | attribute | 5   | TRAINING | LC    |

    Given trip 2 is assigned to crew member 2 in position FC with
      | type      | leg | name       | value |
      | attribute | 1-2 | INSTRUCTOR | LC    |
      | attribute | 3-4 | INSTRUCTOR | ILC   |
      | attribute | 5   | INSTRUCTOR | LC    |

     When I show "crew" in window 1
     Then rave "rules_indust_ccp.%connection_type%" shall be "LCTOLC" on leg 1 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOILC" on leg 2 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOILC" on leg 3 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOLC" on leg 4 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOLC" on leg 1 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOILC" on leg 2 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOILC" on leg 3 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOLC" on leg 4 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 2 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 2

 ##############################################################################

  @SCENARIO9
  Scenario: Test LCTOACT, TOLC, LCTOPASS

  Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

  Given a crew member with
    | attribute  | value | valid from | valid to |
    | base       | OSL   |            |          |
    | title rank | FC    |            |          |
    | region     | SKN   |            |          |

  Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

  Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | CPH     | 10MAR2020 | 06:15 | 08:30 | SK  | 320    |
    | leg | 0002 | CPH     | OSL     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
    | leg | 0003 | OSL     | CPH     | 10MAR2020 | 12:00 | 13:00 | SK  | 320    |
    | leg | 0004 | CPH     | ARN     | 10MAR2020 | 14:15 | 15:15 | SK  | 320    |
    | dh  | 0005 | ARN     | OSL     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |

  Given trip 1 is assigned to crew member 1 in position FP with
    | type      | leg | name     | value |
    | attribute | 2   | TRAINING | LC    |
    | attribute | 4   | TRAINING | LC    |


  Given trip 1 is assigned to crew member 2 in position FC with
    | type      | leg | name       | value |
    | attribute | 2   | INSTRUCTOR | LC    |
    | attribute | 4   | INSTRUCTOR | LC    |

  Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | CPH     | 20MAR2020 | 06:15 | 08:15 | SK  | 320    |
    | leg | 0002 | CPH     | OSL     | 20MAR2020 | 11:00 | 12:00 | SK  | 320    |
    | leg | 0003 | OSL     | CPH     | 20MAR2020 | 15:00 | 16:00 | SK  | 320    |
    | leg | 0004 | CPH     | ARN     | 20MAR2020 | 19:15 | 20:15 | SK  | 320    |
    | dh  | 0005 | ARN     | OSL     | 20MAR2020 | 23:00 | 23:45 | SK  | 320    |

  Given trip 2 is assigned to crew member 1 in position FP with
    | type      | leg | name     | value |
    | attribute | 2   | TRAINING | LC    |
    | attribute | 4   | TRAINING | LC    |

  Given trip 2 is assigned to crew member 2 in position FC with
    | type      | leg | name       | value |
    | attribute | 2   | INSTRUCTOR | LC    |
    | attribute | 4   | INSTRUCTOR | LC    |


     When I show "crew" in window 1
     Then rave "rules_indust_ccp.%connection_type%" shall be "TOLC" on leg 1 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOACT" on leg 2 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOPASS" on leg 4 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "TOLC" on leg 1 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOACT" on leg 2 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "LCTOPASS" on leg 4 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 2


##############################################################################

 @SCENARIO10
 Scenario: Test ILCTOACT, ITOLC, ILCTOPASS

 Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020
 
 Given a crew member with
  | attribute  | value | valid from | valid to |
  | base       | OSL   |            |          |
  | title rank | FC    |            |          |
  | region     | SKN   |            |          |

 Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

 Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | CPH     | 10MAR2020 | 06:15 | 08:30 | SK  | 320    |
   | leg | 0002 | CPH     | OSL     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
   | leg | 0003 | OSL     | CPH     | 10MAR2020 | 12:00 | 13:00 | SK  | 320    |
   | leg | 0004 | CPH     | ARN     | 10MAR2020 | 14:15 | 15:15 | SK  | 320    |
   | dh  | 0005 | ARN     | OSL     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |

 Given trip 1 is assigned to crew member 1 in position FP with
   | type      | leg | name     | value |
   | attribute | 2   | TRAINING | ILC   |
   | attribute | 4   | TRAINING | ILC   |


 Given trip 1 is assigned to crew member 2 in position FC with
   | type      | leg | name       | value |
   | attribute | 2   | INSTRUCTOR | ILC   |
   | attribute | 4   | INSTRUCTOR | ILC   |

 Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | CPH     | 20MAR2020 | 06:15 | 08:15 | SK  | 320    |
   | leg | 0002 | CPH     | OSL     | 20MAR2020 | 11:00 | 12:00 | SK  | 320    |
   | leg | 0003 | OSL     | CPH     | 20MAR2020 | 15:00 | 16:00 | SK  | 320    |
   | leg | 0004 | CPH     | ARN     | 20MAR2020 | 19:15 | 20:15 | SK  | 320    |
   | dh  | 0005 | ARN     | OSL     | 20MAR2020 | 23:00 | 23:45 | SK  | 320    |

 Given trip 2 is assigned to crew member 1 in position FP with
   | type      | leg | name     | value |
   | attribute | 2   | TRAINING | ILC   |
   | attribute | 4   | TRAINING | ILC   |


 Given trip 2 is assigned to crew member 2 in position FC with
   | type      | leg | name       | value |
   | attribute | 2   | INSTRUCTOR | ILC   |
   | attribute | 4   | INSTRUCTOR | ILC   |


    When I show "crew" in window 1
    Then rave "rules_indust_ccp.%connection_type%" shall be "TOILC" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOACT" on leg 2 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOPASS" on leg 4 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "TOILC" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOACT" on leg 2 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "ILCTOPASS" on leg 4 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 2 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 4 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 2 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 4 on trip 2 on roster 2


##############################################################################
  @SCENARIO11
  Scenario: Test PASSTOSUPERNUM and SUPERNUMTOPASS connections.
  Connection times should be applied both to trainee and instructor.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | title rank | FC    |            |          |
      | region     | SKS   |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 10MAR2020 | 18:20 | 20:15 | SK  | 320    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:20 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 15MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 15MAR2020 | 17:45 | 19:45 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position 4 with attribute TRAINING="X SUPERNUM"
    Given trip 1 is assigned to crew member 2 in position 4 with attribute INSTRUCTOR="X SUPERNUM"
    Given trip 2 is assigned to crew member 1 in position 4 with attribute TRAINING="X SUPERNUM"
    Given trip 2 is assigned to crew member 2 in position 4 with attribute INSTRUCTOR="X SUPERNUM"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSUPERNUM" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSUPERNUM" on leg 1 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SUPERNUMTOPASS" on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "SUPERNUMTOPASS" on leg 3 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSUPERNUM" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOSUPERNUM" on leg 1 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "SUPERNUMTOPASS" on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "SUPERNUMTOPASS" on leg 3 on trip 2 on roster 2

##############################################################################
  @SCENARIO12
  Scenario: Test PASSTOFAMFLT and FAMFLTTOPASS connections.
  Connection times should be applied both to trainee and instructor.

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | title rank | FC    |            |          |
      | region     | SKS   |            |          |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 10MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 10MAR2020 | 18:20 | 20:15 | SK  | 320    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 320    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:20 | 11:00 | SK  | 320    |
      | leg | 0003 | CPH     | LHR     | 15MAR2020 | 16:00 | 17:00 | SK  | 320    |
      | dh  | 0004 | LHR     | ARN     | 15MAR2020 | 17:45 | 19:45 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="FAM FLT"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOFAMFLT" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOFAMFLT" on leg 1 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "FAMFLTTOPASS" on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "FAMFLTTOPASS" on leg 3 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOFAMFLT" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOFAMFLT" on leg 1 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "FAMFLTTOPASS" on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "FAMFLTTOPASS" on leg 3 on trip 2 on roster 2

##############################################################################

  @SCENARIO13
  Scenario: Test PASSTOLIFUS and LIFUSTOPASS connections.

    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | title rank | FC    |            |          |
      | region     | SKS   |            |          |

    Given crew member 2 has qualification "ACQUAL+A3" from 1JUL2018 to 31JUL2020
    Given crew member 2 has acqual qualification "ACQUAL+A3+INSTRUCTOR+LIFUS" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 333    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 333    |
      | leg | 0003 | CPH     | LHR     | 10MAR2020 | 16:00 | 17:00 | SK  | 333    |
      | dh  | 0004 | LHR     | ARN     | 10MAR2020 | 18:30 | 20:15 | SK  | 333    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 333    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:30 | 11:00 | SK  | 333    |
      | leg | 0003 | CPH     | LHR     | 15MAR2020 | 16:00 | 17:00 | SK  | 333    |
      | dh  | 0004 | LHR     | ARN     | 15MAR2020 | 17:45 | 19:45 | SK  | 333    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 2 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 1 on roster 1
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 2 on roster 1
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 3 on trip 1 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
  and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 3 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOLIFUS" on leg 1 on trip 2 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 1 on roster 2
  and rave "rules_indust_ccp.%connection_type%" shall be "LIFUSTOPASS" on leg 3 on trip 2 on roster 2

##############################################################################

  @SCENARIO14
  Scenario: Test PASSTOZFTTX connections using specific aircraft row (A4)
  Connection times should be applied both to trainee and instructor.

    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2019 to 31DEC2020

    Given a crew member with
      | attribute  | value | valid from | valid to |
      | base       | STO   |            |          |
      | region     | SKS   |            |          |
      | title rank | FC    |            |          |

    Given crew member 2 has qualification "ACQUAL+A4" from 1JUL2018 to 31JUL2020
    Given crew member 2 has acqual qualification "ACQUAL+A4+INSTRUCTOR+LIFUS" from 1JUL2018 to 31JUL2020

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 10MAR2020 | 06:15 | 08:15 | SK  | 340    |
      | leg | 0002 | LHR     | CPH     | 10MAR2020 | 09:00 | 11:00 | SK  | 340    |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 0001 | ARN     | LHR     | 15MAR2020 | 06:00 | 08:00 | SK  | 340    |
      | leg | 0002 | LHR     | CPH     | 15MAR2020 | 09:30 | 11:00 | SK  | 340    |


    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT X"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ZFTT X"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT X"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ZFTT X"

    When I show "crew" in window 1
    Then the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 1 on roster 1
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 2 on roster 1
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall fail on leg 1 on trip 1 on roster 2
   and the rule "rules_indust_ccp.ind_min_training_connection_ALL" shall pass on leg 1 on trip 2 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 1 on roster 2
   and rave "rules_indust_ccp.%connection_type%" shall be "PASSTOZFTTX" on leg 1 on trip 2 on roster 2

