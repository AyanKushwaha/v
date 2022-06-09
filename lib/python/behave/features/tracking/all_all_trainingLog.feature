Feature: Training log entries

   Background:
     Given Tracking
     Given planning period from 1DEC2018 to 31DEC2018

   # FBF LCP does not work, but there is no FBF in roster whatsoever, so leaving this out for now.
   # #################
   # # JIRA - SKAM-816
   # #################
   # @TRACKING @SCENARIO1 @FBF_LCP @TRAINING_LOG
   # Scenario: Check training log entry FBF LCP


   #  Given a crew member with
   #  | attribute       | value     | valid from | valid to |
   #  | base            | STO       |            |          |
   #  | crew rank       | FC        |            |          |
   #  | title rank      | FC        |            |          |

   # Given a trip with the following activities
   # | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   # | leg | 0001 | ARN     | LHR     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   # | leg | 0002 | LHR     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   # Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FBF"

   # When I show "crew" in window 1

   # Then rave "training_log.%active_flight_log_type%" shall be "FBF LCP" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO2 @FBF @TRAINING_LOG
   Scenario: Check training log entry FBF


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FP        |            |          |
    | title rank      | FP        |            |          |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FBF"

   When I show "crew" in window 1

   Then rave "training_log.%active_flight_log_type%" shall be "FBF" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO3 @FLIGHT_AIRPORT @TRAINING_LOG
   Scenario: Check training log entry FLIGHT AIRPORT


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |

   Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
   Given crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+GZP" from 1DEC2018 to 1FEB2019 

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | GZP     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | GZP     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1 in position FC

   When I show "crew" in window 1

   Then rave "training_log.%active_flight_log_type%" shall be "FLIGHT AIRPORT" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO3_1 @FLIGHT_AIRPORT @TRAINING_LOG
   Scenario: Check training log entry FLIGHT AIRPORT for virtual qualification


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |

   Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
   Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+GZP" from 1DEC2018 to 1FEB2019 

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | GZP     | 26DEC2018 | 10:00 | 11:00 | SK  | 33A    |
   | leg | 0002 | GZP     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 33A    |

   Given trip 1 is assigned to crew member 1 in position FC

   When I show "crew" in window 1

   Then rave "training_log.%active_flight_log_type%" shall be "FLIGHT AIRPORT" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO4 @NEW @TRAINING_LOG
   Scenario: Check training log entry NEW


    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | AH        |            |          |
    | title rank      | AH        |            |          |

   Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 1DEC2018 to 1FEB2019

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | GZP     | 26DEC2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | GZP     | ARN     | 26DEC2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1 in position AH

   When I show "crew" in window 1

   Then rave "training_log.%active_flight_log_type%" shall be "NEW" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO5 @LIFUS_INSTR @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO5_1 @LIFUS_INSTR @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR for virtual qualification
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @ROSTERING @SCENARIO5_2 @LIFUS_INSTR @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR for virtual qualification
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LIFUS"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO6 @LCP_SUPERNUM @TRAINING_LOG
   Scenario: Check training log entry LCP SUPERNUM
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "POSITION+LCP" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FU with attribute INSTRUCTOR="LC"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LCP SUPERNUM" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO7 @LCP @TRAINING_LOG
   Scenario: Check training log entry LCP
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "POSITION+LCP" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ILC"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="ILC"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LCP" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO8 @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry FLIGHT INSTR
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="CNF"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="CNF"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "FLIGHT INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO9 @SCHOOLFLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry SCHOOLFLIGHT INSTR
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 9160 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 9161 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "SCHOOLFLIGHT INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO9_1 @SCHOOLFLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry SCHOOLFLIGHT INSTR for virtual qualification
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 9160 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 9161 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "SCHOOLFLIGHT INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @TRACKING @SCENARIO10 @SCHOOLFLIGHT @TRAINING_LOG
   Scenario: Check training log entry SCHOOLFLIGHT
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 9160 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 9161 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "SCHOOLFLIGHT" on leg 1 on trip 1 on roster 2


   #################
   # JIRA - SKAM-816
   #################
   @ROSTERING @SCENARIO11 @LIFUS_INSTR @ZFTT_LIFUS @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR for ZFTT LIFUS instructor
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT LIFUS"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @ROSTERING @SCENARIO12 @LIFUS_INSTR @X_LIFUS @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR for X LIFUS instructor
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="X LIFUS"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="X LIFUS"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   #################
   # JIRA - SKAM-816
   #################
   @ROSTERING @SCENARIO13 @LIFUS_INSTR @ZFTT_X @TRAINING_LOG
   Scenario: Check training log entry LIFUS INSTR for ZFTT X instructor
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="ZFTT X"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="ZFTT X"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "LIFUS INSTR" on leg 1 on trip 1 on roster 1


   ###################
   # JIRA - SKCMS-2067
   ###################
   @ROSTERING @SCENARIO14 @FAM_FLT @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry FLIGHT INSTR for FAM FLT instructor, FC, pos 1, and entry FAM FLT for FAM FLT trainee, FP, pos 2
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" values shall be
       | leg | trip | roster | value        |
       | 1   | 1    | 1      | FLIGHT INSTR |
       | 1   | 1    | 2      | FAM FLT      |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      | C     |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | C     |
       | 1   | 1    | 2      | ""    |


   ###################
   # JIRA - SKCMS-2067
   ###################
   @ROSTERING @SCENARIO15 @FAM_FLT @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry FLIGHT INSTR for FAM FLT instructor, FC, pos 1, and entry FAM FLT for FAM FLT trainee, FC, pos 2
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 05DEC2018 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | LHR     | OSL     | 05DEC2018 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" values shall be
       | leg | trip | roster | value        |
       | 1   | 1    | 1      | FLIGHT INSTR |
       | 1   | 1    | 2      | FAM FLT      |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      | CL    |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | C     |
       | 1   | 1    | 2      | ""    |


   ###################
   # JIRA - SKCMS-2072
   ###################
   @ROSTERING @SCENARIO17 @FAM_FLT @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry for C5* activity, flight deck trainee

    Given table activity_set additionally contains the following
    | id  | grp | si                      | recurrent_typ |
    | C5X | ASF | Additional sim activity |               |

    Given table activity_set_period additionally contains the following
    | id  | validfrom | validto   |
    | C5X | 1JAN1986  | 31DEC2035 |

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1DEC2018 to 1FEB2019


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5X  | OSL     | OSL     | 05DEC2018 | 10:00 | 11:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ASF   |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | C5X   |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |


   ###################
   # JIRA - SKCMS-2078
   ###################
   @SCENARIO18 @FMST @TRAINING_LOG
   Scenario: Check training log entry for FMST activity

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1DEC2018 to 1FEB2019

    Given crew member 1 has a personal activity "FMST" at station "OSL" that starts at 05DEC2018 10:00 and ends at 05DEC2018 11:00

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | FMST   |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | FMST  |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |


   ###################
   # JIRA - SKCMS-2383
   ###################
   @SCENARIO19 @LRP2 @TRAINING_LOG
   Scenario: Check training log entry for FMST activity

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given crew member 1 has a personal activity "LRP2" at station "OSL" that starts at 05DEC2018 10:00 and ends at 05DEC2018 11:00

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | COURSE |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | LRP2  |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |


   ###################
   # JIRA - SKCMS-2383
   ###################
   @SCENARIO20 @LRSB @TRAINING_LOG
   Scenario: Check training log entry for FMST activity

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 05DEC2018 10:00 and ends at 05DEC2018 11:00

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | COURSE |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | LRSB  |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |


   ###################
   # JIRA - SKCMS-2383
   ###################
   @SCENARIO21 @LR_REFRESH @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry FLIGHT INSTR for LR REFRESH instructor, FC, pos 1, and entry LR REFRESH for LR REFRESH trainee, FP, pos 2
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | JFK     | 05DEC2018 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | JFK     | OSL     | 06DEC2018 | 12:00 | 13:00 | SK  | 32J    |

    Given trip 1 is assigned to crew member 1 in position FC with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value  |
       | 1   | 1    | 1      | FLIGHT INSTR |
       | 1   | 1    | 2      | LR REFRESH   |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | A2    |
       | 1   | 1    | 2      | A2    |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      | C     |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | C     |
       | 1   | 1    | 2      | ""    |


   ###################
   # JIRA - SKCMS-2383
   ###################
   @SCENARIO22 @LR_REFRESH @FLIGHT_INSTR @TRAINING_LOG
   Scenario: Check training log entry FLIGHT INSTR for LR REFRESH instructor, FC, pos 2, and entry LR REFRESH for LR REFRESH trainee, FC, pos 1
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1DEC2018 to 1FEB2019
    Given crew member 1 has qualification "INSTRUCTOR+TRI" from 1DEC2018 to 1FEB2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |
    | published       | 31Dec2035 |            |          |
    Given crew member 2 has qualification "ACQUAL+A3" from 1DEC2018 to 1FEB2019

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | JFK     | 05DEC2018 | 10:00 | 11:00 | SK  | 32J    |
    | leg | 0002 | JFK     | OSL     | 06DEC2018 | 12:00 | 13:00 | SK  | 32J    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute INSTRUCTOR="LR REFRESH"
    Given trip 1 is assigned to crew member 2 in position FC with attribute TRAINING="LR REFRESH"

    When I show "crew" in window 1

    Then rave "training_log.%leg_type%" values shall be
       | leg | trip | roster | value        |
       | 1   | 1    | 1      | FLIGHT INSTR |
       | 1   | 1    | 2      | LR REFRESH   |
    and rave "training_log.%leg_type2%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      |       |
    and rave "training_log.%leg_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | A2    |
       | 1   | 1    | 2      | A2    |
    and rave "training_log.%leg_attr%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | ""    |
       | 1   | 1    | 2      | ""    |
    and rave "training.%leg_trainee_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      |       |
       | 1   | 1    | 2      | C     |
    and rave "training.%leg_instructor_duty_code%" values shall be
       | leg | trip | roster | value |
       | 1   | 1    | 1      | CL    |
       | 1   | 1    | 2      | ""    |

    ###################
    # JIRA - SKCMS-2171
    ###################
    @SCENARIO23 @TRAINING_LOG @FC
    Scenario: Extend airport qualifications for lifus airport when flying below rank and
    qual ends earlier than extension period
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 21DEC2017  | 13DEC2018 |
           | region          | SKN        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | V00008     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 11DEC2018 to 19FEB2019
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | LYR     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | LYR     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    Given trip 1 is assigned to crew member 1 in position FP with
           | type      | leg             | name            | value           |
           | attribute | 2,3             | TRAINING        | X LIFUS         |

    When I show "crew" in window 1
    Then rave "training_log.%leg_extends_airport_qual%" shall be "LYR" on leg 2 on trip 1 on roster 1

    ###################
    # JIRA - SKCMS-2171
    ###################
    @SCENARIO24 @TRAINING_LOG @FC
    Scenario: Extend airport qualifications for lifus airport when flying in title rank and
    qual ends earlier than extension period
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 21DEC2017  | 13DEC2018 |
           | region          | SKN        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | V00008     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 11DEC2018 to 19FEB2019
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | LYR     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | LYR     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    Given trip 1 is assigned to crew member 1 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 2,3             | TRAINING        | X LIFUS         |

    When I show "crew" in window 1
    Then rave "training_log.%leg_extends_airport_qual%" shall be "LYR" on leg 2 on trip 1 on roster 1
    
    ###################
    # JIRA - SKCMS-2518
    ###################
    @SCENARIO21 @TRAINING_LOG @FC
    Scenario: Don't extend airport qualifications for lifus airport ALF when flying below rank and
    qual ends earlier than extension period if crew is other than SKN.
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 21DEC2017  | 13DEC2018 |
           | region          | SKD        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | QAF018     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 11DEC2018 to 19FEB2019
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | ALF     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | ALF     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    
    Given trip 1 is assigned to crew member 1 in position FP 
    When I show "crew" in window 1

    Then rave "crew_pos.%lower_rank%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "training_log.%fc_lower_exception%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "crew.%is_SKN%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "fundamental.%flight_crew%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "leg.%arrival_airport_name%" shall be "ALF" on leg 2 on trip 1 on roster 1    
    and rave "crew_pos.%current_pos%" shall be "1" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%assigned_pos%" shall be "2" on leg 2 on trip 1 on roster 1
    and rave "training_log.%leg_extends_airport_qual%" shall be "" on leg 2 on trip 1 on roster 1
   
    
    ###################
    # JIRA - SKCMS-2518
    ###################
    @SCENARIO22 @TRAINING_LOG @FC
    Scenario: Extend airport qualifications for lifus airport ALF when flying below rank and
    qual ends earlier than extension period only if crew is SKN.
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 21DEC2017  | 13DEC2018 |
           | region          | SKN        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | V00008     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 11DEC2018 to 19FEB2019
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | ALF     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | ALF     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    
    Given trip 1 is assigned to crew member 1 in position FP 
    When I show "crew" in window 1

    Then rave "crew_pos.%lower_rank%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "training_log.%fc_lower_exception%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "crew.%is_SKN%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "fundamental.%flight_crew%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "leg.%arrival_airport_name%" shall be "ALF" on leg 2 on trip 1 on roster 1    
    and rave "crew_pos.%current_pos%" shall be "1" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%assigned_pos%" shall be "2" on leg 2 on trip 1 on roster 1
    and rave "training_log.%leg_extends_airport_qual%" shall be "ALF" on leg 2 on trip 1 on roster 1    


    ###################
    # JIRA - SKCMS-2518
    ###################
    @SCENARIO23 @TRAINING_LOG @FC
    Scenario: Don't create airport qualifications for lifus airport ALF when flying below rank and
    qual ends earlier than extension period if crew is not SKN.
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 21DEC2017  | 13DEC2018 |
           | region          | SKD        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | QAF018     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | ALF     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | ALF     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    
    Given trip 1 is assigned to crew member 1 in position FP 
    When I show "crew" in window 1

    Then rave "crew_pos.%lower_rank%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "training_log.%fc_lower_exception%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "crew.%is_SKD%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%current_pos%" shall be "1" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%assigned_pos%" shall be "2" on leg 2 on trip 1 on roster 1
    and rave "training_log.%training_leg_should_create_apt_qual%" shall be "False" on leg 2 on trip 1 on roster 1
    

    ###################
    # JIRA - SKCMS-2518
    ###################
    @SCENARIO24 @TRAINING_LOG @FC
    Scenario: Create airport qualifications for lifus airport ALF when flying below rank and
    qual ends earlier than extension period only if crew is SKN.
    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 21DEC2017  | 13DEC2018 |
           | region          | SKN        | 21DEC2017  | 13DEC2018 |
           | base            | TRD        | 21DEC2017  | 13DEC2018 |
           | title rank      | FC         | 21DEC2017  | 13DEC2018 |
           | contract        | V00008     | 29NOV2017  | 01MAR2019 |
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
    Given crew member 1 has restriction "TRAINING+CAPT" from 30DEC2017 to 13DEC2018

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 000345  | TRD     | OSL     | 11DEC2018 07:25 | 11DEC2018 08:25 | 73T     |         |
           | leg     | SK      | 004490  | OSL     | ALF     | 11DEC2018 10:15 | 11DEC2018 13:10 | 73J     |         |
           | leg     | SK      | 004491  | ALF     | OSL     | 11DEC2018 13:55 | 11DEC2018 16:50 | 73J     |         |
           | dh      | SK      | 000368  | OSL     | TRD     | 11DEC2018 17:35 | 11DEC2018 18:30 | 73T     |         |
    
    Given trip 1 is assigned to crew member 1 in position FP 
    When I show "crew" in window 1

    Then rave "crew_pos.%lower_rank%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "training_log.%fc_lower_exception%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "crew.%is_SKN%" shall be "True" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%current_pos%" shall be "1" on leg 2 on trip 1 on roster 1
    and rave "crew_pos.%assigned_pos%" shall be "2" on leg 2 on trip 1 on roster 1
    and rave "training_log.%training_leg_should_create_apt_qual%" shall be "True" on leg 2 on trip 1 on roster 1

    ###################
    # JIRA - SKCMS-2545
    ###################
    @SCENARIO25 @TRAINING_LOG @FC @ETOPS
    Scenario: Check that trainee and instructor get correct log type for LC instructor
    Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2018

    Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2020
    Given crew member 2 has qualification "POSITION+LCP" from 1JAN2018 to 31DEC2018
    Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2018 to 31DEC2018

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12DEC2018 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12DEC2018 | 13:00 | 20:00 | SK  | 321    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

    When I show "crew" in window 1
    Then rave "training_log.%active_flight_log_type%" shall be "ETOPS LIFUS/LC" on leg 1 on trip 1 on roster 1
     and rave "training_log.%active_flight_log_type%" shall be "FLIGHT INSTR" on leg 1 on trip 1 on roster 2


    ###################
    # JIRA - SKCMS-2545
    ###################
    @SCENARIO26 @TRAINING_LOG @FC @ETOPS
    Scenario: Check that trainee and instructor get correct log type for LIFUS instructor
    Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FP    |            |          |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2018

    Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2018
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2018 to 31DEC2018
    Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2018 to 31DEC2018

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12DEC2018 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12DEC2018 | 13:00 | 20:00 | SK  | 321    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

    When I show "crew" in window 1

    Then rave "training_log.%active_flight_log_type%" shall be "ETOPS LIFUS/LC" on leg 1 on trip 1 on roster 1
     and rave "training_log.%active_flight_log_type%" shall be "FLIGHT INSTR" on leg 1 on trip 1 on roster 2


    ###################
    # JIRA - SKCMS-2545
    ###################
    @SCENARIO27 @TRAINING_LOG @FC @ETOPS
    Scenario: Check that trainee and instructor get correct log type for LIFUS instructor
    Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2018

    Given another crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2018
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 01JAN2018 to 31DEC2018
    Given crew member 2 has qualification "POSITION+A2NX" from 1JAN2018 to 31DEC2018

    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | EWR     | 12DEC2018 | 08:00 | 12:00 | SK  | 321    |
        | leg | 0002 | EWR     | OSL     | 12DEC2018 | 13:00 | 20:00 | SK  | 321    |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ETOPS LIFUS/LC"
    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="ETOPS LIFUS/LC"

    When I show "crew" in window 1
    Then rave "training_log.%active_flight_log_type%" shall be "ETOPS LIFUS/LC" on leg 1 on trip 1 on roster 1
     and rave "training_log.%active_flight_log_type%" shall be "FLIGHT INSTR" on leg 1 on trip 1 on roster 2
