# SKCMS-2473:
# Due to Corona, some spring web trainings are postponed to autumn.
# This means that spring PC and autumn PC/OPC can be scheduled in the same season.
# This feature tests that crew with prolonged PC documents are not incorrectly assigned assist position
# and that the delayed PC activity isn't mistaken for the regular autumn PC/OPC activity.
# Only applicable for 38 crew during autumn 2020.

Feature: Test that crew with prolonged PC document are handled correctly.

  Background:
    Given Tracking

    Given a crew member with
      | attribute       | value     | valid from | valid to  |
      | employee number | 37252     |            |           |
      | sex             | M         |            |           |
      | crew rank       | FC        | 18JAN2018  | 01JAN2036 |
      | region          | SKI       | 18JAN2018  | 01JAN2036 |
      | base            | OSL       | 18JAN2018  | 01JAN2036 |
      | title rank      | FC        | 18JAN2018  | 01JAN2036 |
      | contract        | V00001-LH | 01JAN2018  | 01JAN2036 |
      | published       | 01AUG2020 | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+A3" from 10MAR2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A4" from 04DEC2017 to 01JAN2036
    Given crew member 1 has qualification "AIRPORT+LYR" from 01JAN2012 to 01JUL2021
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 11FEB2017 to 30NOV2022

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 18JAN2018  | 01JAN2036 |
      | region     | SKI       | 18JAN2018  | 01JAN2036 |
      | base       | OSL       | 18JAN2018  | 01JAN2036 |
      | title rank | FC        | 18JAN2018  | 01JAN2036 |
      | contract   | V00001-LH | 01JAN2018  | 01JAN2036 |
      | published  | 01AUG2020 | 01JAN1986  |           |

    Given crew member 2 has qualification "ACQUAL+38" from 10MAR2018 to 01JAN2036

    # Documents
    Given crew member 1 has document "REC+CRM" from 01MAY2010 to 31MAY2022
    Given crew member 1 has document "REC+PGT" from 01JAN1986 to 31DEC2020
    Given crew member 1 has document "REC+LC" from 01JAN1986 to 30JUN2021 and has qualification "A4"

    Given crew member 2 has document "REC+CRM" from 01MAY2010 to 31MAY2022
    Given crew member 2 has document "REC+PGT" from 01JAN1986 to 31DEC2020
    Given crew member 2 has document "REC+LC" from 01JAN1986 to 30JUN2021 and has qualification "38"

    Given table crew_training_log additionally contains the following
      | tim             | code | typ           | attr  | crew          |
      | 01JUN2020 05:00 | WTA2 | COURSE        |       | crew member 1 |
      | 03MAY2020 04:00 | WTB2 | COURSE        |       | crew member 2 |

######################################################################################################

  @SCENARIO1
  Scenario: Long haul crew missing PC A4 and planned PC A3 marked as FORCED should be illegal.
    Given planning period from 01Aug2020 to 01Sep2020

    # Documents
    Given crew member 1 has document "REC+PCA3" from 26JUN2019 to 30JUN2020
    Given crew member 1 has document "REC+PCA4" from 19DEC2019 to 01AUG2020
    Given crew member 1 has document "REC+OPCA3" from 19DEC2019 to 30JUN2020
    Given crew member 1 has document "REC+OPCA4" from 19DEC2019 to 30JUN2020

    # FORCED PC A3 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg     | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 73O    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S6   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S6   |
      | leg     | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="PC FORCED"

    # This trip should be illegal since OPC A4 document is not valid and no PC A4 activity planned before trip start.
    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 34B    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 13:00 | 14:00 | SK  | 34B    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 16:00 | 17:00 | SK  | 34B    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 19:00 | 20:00 | SK  | 34B    |

    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1
  and rave "rules_qual_ccr.%missed_recurrent_training_failtext%" shall be "OMA: Rec. expiry dates passed, needs: PCA4" on leg 1 on trip 2 on roster 1

######################################################################################################

  @SCENARIO2
  Scenario: Long haul crew with PC A3 (FORCED) and planned PC A4 should be legal. Crew shall be assigned in assist position on PC A4.
    Given planning period from 01Aug2020 to 01Sep2020

    # Documents, validity for PC A3, OPC A3 and OPC A4 manually extended.
    Given crew member 1 has document "REC+PCA3" from 26JUN2019 to 30JUN2021
    Given crew member 1 has document "REC+PCA4" from 19DEC2019 to 01SEP2020
    Given crew member 1 has document "REC+OPCA3" from 19DEC2019 to 30SEP2020
    Given crew member 1 has document "REC+OPCA4" from 19DEC2019 to 30SEP2020

    # FORCED PC A3 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 73O    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S6   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S6   |
      | leg    | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="PC FORCED"

    # Regular web training session for autumn
    Given crew member 1 has a personal activity "WTA22" at station "OSL" that starts at 08AUG2020 04:00 and ends at 08AUG2020 14:00

    # PC A4 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 10AUG2020 05:45 | 10AUG2020 06:55 | 73O    |      |
      | ground |     |      | CPH     | CPH     | 10AUG2020 08:30 | 10AUG2020 10:30 |        | S4   |
      | ground |     |      | CPH     | CPH     | 10AUG2020 12:30 | 10AUG2020 14:30 |        | S4   |
      | leg    | SK  | 0002 | CPH     | OSL     | 10AUG2020 19:00 | 10AUG2020 20:15 | 73O    |      |

    Given trip 2 is assigned to crew member 1 in position FR

    # This trip should be valid since crew has PC A4 activity planned before trip start.
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 34B    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 12:00 | 13:00 | SK  | 34B    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 14:00 | 15:00 | SK  | 34B    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 16:00 | 17:00 | SK  | 34B    |

    Given trip 3 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
  and rave "training_log.%leg_type%" shall be "SIM ASSIST" on leg 2 on trip 3 on roster 1
  and rave "training_log.%leg_code%" shall be "Y4" on leg 2 on trip 3 on roster 1

######################################################################################################

  @SCENARIO3
  Scenario: Short haul 38 crew missing OPC document and planned PC marked as FORCED should be illegal.
    Given planning period from 01Aug2020 to 01OCT2020

    # Documents
    Given crew member 2 has document "REC+PC" from 26JUN2019 to 01AUG2020 and has qualification "38"
    Given crew member 2 has document "REC+OPC" from 19DEC2019 to 31AUG2020 and has qualification "38"

    # FORCED PC 38 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 73K    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S3   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S3   |
      | leg    | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 73K    |      |

    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="PC FORCED"

    # This trip should still be legal since OPC 38 document is still valid at trip start.
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 73K    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 12:00 | 13:00 | SK  | 73K    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 14:00 | 15:00 | SK  | 73K    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 16:00 | 17:00 | SK  | 73K    |

    Given trip 2 is assigned to crew member 2 in position FC

    # This trip should be illegal since OPC 38 document is not valid and no OPC activity planned before trip start.
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 01SEP2020 | 10:00 | 11:00 | SK  | 73K    |
      | leg | 0002 | LHR     | OSL     | 01SEP2020 | 12:00 | 13:00 | SK  | 73K    |
      | leg | 0003 | OSL     | LHR     | 01SEP2020 | 14:00 | 15:00 | SK  | 73K    |
      | leg | 0004 | LHR     | OSL     | 01SEP2020 | 16:00 | 17:00 | SK  | 73K    |

    Given trip 3 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 2 on roster 2
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 3 on roster 2
  and rave "rules_qual_ccr.%missed_recurrent_training_failtext%" shall be "OMA: Rec. expiry dates passed, needs: OPC (38)" on leg 1 on trip 3 on roster 2

######################################################################################################

  @SCENARIO4
  Scenario: Short haul 38 crew with FORCED PC 38 and OPC 38 should be valid. Crew shall not be assigned in assist position on OPC 38.
    Given planning period from 01Aug2020 to 01Sep2020

    # Documents, validity for PC 38 manually extended.
    Given crew member 2 has document "REC+PC" from 26JUN2019 to 01JUN2021 and has qualification "38"
    Given crew member 2 has document "REC+OPC" from 19DEC2019 to 01SEP2020 and has qualification "38"

    # FORCED PC 38 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 73K    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S3   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S3   |
      | leg    | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 73K    |      |

    Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="PC FORCED"

    # Regular web training session for autumn
    Given crew member 2 has a personal activity "WTB22" at station "OSL" that starts at 08AUG2020 04:00 and ends at 08AUG2020 14:00

    # OPC 38 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 10AUG2020 05:45 | 10AUG2020 06:55 | 73K    |      |
      | ground |     |      | CPH     | CPH     | 10AUG2020 08:30 | 10AUG2020 10:30 |        | S3   |
      | ground |     |      | CPH     | CPH     | 10AUG2020 12:30 | 10AUG2020 14:30 |        | S3   |
      | leg    | SK  | 0002 | CPH     | OSL     | 10AUG2020 19:00 | 10AUG2020 20:15 | 73K    |      |

    Given trip 2 is assigned to crew member 2 in position FR

    # This trip should be valid since crew has OPC activity planned before trip start.
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 73K    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 12:00 | 13:00 | SK  | 73K    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 14:00 | 15:00 | SK  | 73K    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 16:00 | 17:00 | SK  | 73K    |

    Given trip 3 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 2
  and rave "training_log.%leg_type%" shall be "OPC" on leg 2 on trip 3 on roster 2
  and rave "training_log.%leg_code%" shall be "S3" on leg 2 on trip 3 on roster 2

######################################################################################################

  @SCENARIO5 @To_Be_Checked
  Scenario: Short haul A2 crew shall be allowed to lack OPC document.
    Given planning period from 01Aug2020 to 01OCT2020

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 18JAN2018  | 01JAN2036 |
      | region     | SKI       | 18JAN2018  | 01JAN2036 |
      | base       | OSL       | 18JAN2018  | 01JAN2036 |
      | title rank | FC        | 18JAN2018  | 01JAN2036 |
      | contract   | V00001-LH | 01JAN2018  | 01JAN2036 |
      | published  | 01AUG2020 | 01JAN1986  |           |

    Given crew member 3 has qualification "ACQUAL+A2" from 10MAR2018 to 01JAN2036
    Given crew member 3 has qualification "POSITION+A2NX" from 10MAR2018 to 01JAN2036

    # Documents
    Given crew member 3 has document "REC+PC" from 26JUN2019 to 01AUG2020 and has qualification "A2"
    Given crew member 3 has document "REC+OPC" from 19DEC2019 to 31AUG2020 and has qualification "A2"

    # FORCED PC activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 73O    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S2   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S2   |
      | leg    | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 3 in position FP with attribute TRAINING="PC FORCED"

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 32J    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 12:00 | 13:00 | SK  | 32J    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 14:00 | 15:00 | SK  | 32J    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 16:00 | 17:00 | SK  | 32J    |

    Given trip 2 is assigned to crew member 3 in position FC

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 01SEP2020 | 10:00 | 11:00 | SK  | 32J    |
      | leg | 0002 | LHR     | OSL     | 01SEP2020 | 12:00 | 13:00 | SK  | 32J    |
      | leg | 0003 | OSL     | LHR     | 01SEP2020 | 14:00 | 15:00 | SK  | 32J    |
      | leg | 0004 | LHR     | OSL     | 01SEP2020 | 16:00 | 17:00 | SK  | 32J    |

    Given trip 3 is assigned to crew member 3 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 3 on roster 3

######################################################################################################

  @SCENARIO6
  Scenario: Short haul A2 crew shall be allowed to lack OPC document and be in assist position if PC or OPC activity planned in same season.
    Given planning period from 01Aug2020 to 01Sep2020

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 18JAN2018  | 01JAN2036 |
      | region     | SKI       | 18JAN2018  | 01JAN2036 |
      | base       | OSL       | 18JAN2018  | 01JAN2036 |
      | title rank | FC        | 18JAN2018  | 01JAN2036 |
      | contract   | V00001-LH | 01JAN2018  | 01JAN2036 |
      | published  | 01AUG2020 | 01JAN1986  |           |

    Given crew member 3 has qualification "ACQUAL+A2" from 10MAR2018 to 01JAN2036
    Given crew member 3 has qualification "POSITION+A2NX" from 10MAR2018 to 01JAN2036

    # Documents, PC A2 manually extended.
    Given crew member 3 has document "REC+PC" from 26JUN2019 to 01JUL2021 and has qualification "A2"
    Given crew member 3 has document "REC+OPC" from 19DEC2019 to 01SEP2020 and has qualification "A2"

    # FORCED PC A2 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 02AUG2020 05:45 | 02AUG2020 06:55 | 32J    |      |
      | ground |     |      | CPH     | CPH     | 02AUG2020 08:30 | 02AUG2020 10:30 |        | S2   |
      | ground |     |      | CPH     | CPH     | 02AUG2020 12:30 | 02AUG2020 14:30 |        | S2   |
      | leg    | SK  | 0002 | CPH     | OSL     | 02AUG2020 19:00 | 02AUG2020 20:15 | 32J    |      |

    Given trip 1 is assigned to crew member 3 in position FP with attribute TRAINING="PC FORCED"

    # Regular web training session for autumn
    Given crew member 3 has a personal activity "WTA22" at station "OSL" that starts at 08AUG2020 04:00 and ends at 08AUG2020 14:00

    # OPC A2 activity
    Given a trip with the following activities
      | act    | car | num  | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | leg    | SK  | 0001 | OSL     | CPH     | 10AUG2020 05:45 | 10AUG2020 06:55 | 32J    |      |
      | ground |     |      | CPH     | CPH     | 10AUG2020 08:30 | 10AUG2020 10:30 |        | S2   |
      | ground |     |      | CPH     | CPH     | 10AUG2020 12:30 | 10AUG2020 14:30 |        | S2   |
      | leg    | SK  | 0002 | CPH     | OSL     | 10AUG2020 19:00 | 10AUG2020 20:15 | 32J    |      |

    Given trip 2 is assigned to crew member 3 in position FR

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | LHR     | 20AUG2020 | 10:00 | 11:00 | SK  | 32J    |
      | leg | 0002 | LHR     | OSL     | 20AUG2020 | 12:00 | 13:00 | SK  | 32J    |
      | leg | 0003 | OSL     | LHR     | 20AUG2020 | 14:00 | 15:00 | SK  | 32J    |
      | leg | 0004 | LHR     | OSL     | 20AUG2020 | 16:00 | 17:00 | SK  | 32J    |

    Given trip 3 is assigned to crew member 3 in position FC

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 3
  and rave "training_log.%leg_type%" shall be "SIM ASSIST" on leg 2 on trip 3 on roster 3
  and rave "training_log.%leg_code%" shall be "S2" on leg 2 on trip 3 on roster 3

######################################################################################################
