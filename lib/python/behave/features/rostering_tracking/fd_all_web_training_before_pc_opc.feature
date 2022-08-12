@FD @PC @OPC @TRAINING
Feature: Test that web trainings are scheduled correct relatively PC/OPC.

  Background:
    Given Tracking

    Given table agreement_validity additionally contains the following
      | id                    | validfrom | validto   |
      | web_training_pc_LH_17 | 1JAN2000  | 31DEC2035 |

    Given a crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 04DEC2017  | 01JAN2036 |
      | region     | SKI       | 04DEC2017  | 01JAN2036 |
      | base       | STO       | 04DEC2017  | 01JAN2036 |
      | title rank | FC        | 04DEC2017  | 01JAN2036 |
      | contract   | V131-LH   | 01APR2020  | 01JAN2021 |
      | published  | 01MAY2020 | 01JAN1986  |           |

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 04DEC2017  | 01JAN2036 |
      | region     | SKI       | 04DEC2017  | 01JAN2036 |
      | base       | STO       | 04DEC2017  | 01JAN2036 |
      | title rank | FC        | 04DEC2017  | 01JAN2036 |
      | contract   | V131-LH   | 01APR2020  | 01JAN2021 |
      | published  | 01MAY2020 | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+A3" from 30OCT2017 to 01JAN2036
    Given crew member 2 has qualification "ACQUAL+A3" from 30OCT2017 to 01JAN2036

######################################################################################################

  @SCENARIO1
  Scenario: Duplicated web trainings should be avoided - spring.
    Given planning period from 1Apr2020 to 1May2020

    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 1APR2021
    Given crew member 1 has document "REC+OPCA3" from 1APR2019 to 1MAY2020

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 20APR2020 04:00 and ends at 20APR2020 14:00
    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 24APR2020 04:00 and ends at 24APR2020 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_web_trg_not_duplicated_FC" shall fail on leg 1 on trip 2 on roster 1

######################################################################################################

  @SCENARIO2
  Scenario: Duplicated web trainings should be avoided - autumn.
    Given planning period from 01Sep2020 to 01Oct2020

    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 1NOV2020
    Given crew member 1 has document "REC+OPCA3" from 1APR2019 to 1MAY2021

    Given crew member 1 has a personal activity "WTA22" at station "ARN" that starts at 20SEP2020 04:00 and ends at 20SEP2020 14:00
    Given crew member 1 has a personal activity "WTA22" at station "ARN" that starts at 24SEP2020 04:00 and ends at 24SEP2020 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_web_trg_not_duplicated_FC" shall fail on leg 1 on trip 2 on roster 1

######################################################################################################

  @SCENARIO3
  Scenario: Web training is not required at PC or OPC SKILL TEST.
    Given planning period from 01Apr2020 to 01May2020

    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 1MAY2021
    Given crew member 1 has document "REC+OPCA3" from 1APR2019 to 1APR2021

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 01APR2020 05:45 | 01APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 01APR2020 08:30 | 01APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 01APR2020 12:30 | 01APR2020 14:30 |        | Y6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 01APR2020 19:00 | 01APR2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000003 | ARN     | CPH     | 09APR2020 05:45 | 09APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 09APR2020 08:30 | 09APR2020 10:30 |        | S6   |
      | ground |     |        | CPH     | CPH     | 09APR2020 12:30 | 09APR2020 14:30 |        | S6   |
      | dh     | SK  | 000004 | CPH     | ARN     | 09APR2020 19:00 | 09APR2020 20:15 | 73O    |      |

    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="SKILL TEST"

    Given crew member 1 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 10:00 and ends at 3MAY2020 10:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 2 on roster 1
    and the rule "rules_training_cct.trng_web_training_needed" shall pass on leg 1 on trip 3 on roster 1

######################################################################################################

  @SCENARIO4
  Scenario: Missing web training within spring eval period before PC or OPC is illegal.
    Given planning period from 01Apr2020 to 01May2020

    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1APR2019 to 1APR2021

    Given crew member 2 has qualification "ACQUAL+A4" from 30OCT2017 to 01JAN2036
    Given crew member 2 has document "REC+PCA3" from 1APR2019 to 1APR2021
    Given crew member 2 has document "REC+OPCA3" from 1APR2019 to 1MAY2021
    Given crew member 2 has document "REC+PCA4" from 1APR2019 to 1APR2021
    Given crew member 2 has document "REC+OPCA4" from 1APR2019 to 1MAY2020

    # PC
    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 16APR2020 05:45 | 16APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16APR2020 08:30 | 16APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 16APR2020 12:30 | 16APR2020 14:30 |        | Y6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 16APR2020 19:00 | 16APR2020 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000003 | ARN     | CPH     | 26APR2020 05:45 | 26APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2020 08:30 | 26APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 26APR2020 12:30 | 26APR2020 14:30 |        | Y6   |
      | dh     | SK  | 000004 | CPH     | ARN     | 26APR2020 19:00 | 26APR2020 20:15 | 73O    |      |

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 20APR2020 04:00 and ends at 20APR2020 14:00
    Given trip 1 is assigned to crew member 1 in position FP
    Given trip 2 is assigned to crew member 1 in position FP

    # OPC
    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000005 | ARN     | CPH     | 16APR2020 05:45 | 16APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16APR2020 08:30 | 16APR2020 10:30 |        | S4   |
      | ground |     |        | CPH     | CPH     | 16APR2020 12:30 | 16APR2020 14:30 |        | S4   |
      | dh     | SK  | 000006 | CPH     | ARN     | 16APR2020 19:00 | 16APR2020 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000007 | ARN     | CPH     | 26APR2020 05:45 | 26APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2020 08:30 | 26APR2020 10:30 |        | S4   |
      | ground |     |        | CPH     | CPH     | 26APR2020 12:30 | 26APR2020 14:30 |        | S4   |
      | dh     | SK  | 000008 | CPH     | ARN     | 26APR2020 19:00 | 26APR2020 20:15 | 73O    |      |

    Given crew member 2 has a personal activity "WTA21" at station "ARN" that starts at 20APR2020 04:00 and ends at 20APR2020 14:00
    Given trip 3 is assigned to crew member 2 in position FP
    Given trip 4 is assigned to crew member 2 in position FP

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 2
    and rave "training.%wt_earliest_date%" shall be "01JAN2020 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_latest_date%" shall be "01APR2020 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_earliest_date%" shall be "01FEB2020 00:00" on leg 2 on trip 1 on roster 2
    and rave "training.%wt_latest_date%" shall be "01MAY2020 00:00" on leg 2 on trip 1 on roster 2

######################################################################################################

  @SCENARIO5
  Scenario: Missing web training within autumn eval period before PC or OPC is illegal.
    Given planning period from 01SEP2020 to 01OCT2020

    Given crew member 1 has qualification "ACQUAL+A4" from 30OCT2017 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A5" from 30OCT2017 to 01JAN2036
    Given crew member 1 has document "REC+PCA3" from 01APR2018 to 01APR2021
    Given crew member 1 has document "REC+OPCA3" from 01APR2019 to 01APR2021
    Given crew member 1 has document "REC+PCA4" from 1APR2019 to 01NOV2020
    Given crew member 1 has document "REC+OPCA4" from 1APR2019 to 01APR2021
    Given crew member 1 has document "REC+PCA5" from 1APR2019 to 01APR2021
    Given crew member 1 has document "REC+OPCA5" from 1APR2019 to 01APR2021


    Given crew member 2 has document "REC+PCA3" from 01APR2019 to 01APR2021
    Given crew member 2 has document "REC+OPCA3" from 01APR2019 to 01SEP2020

    # PC
    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 16SEP2020 05:45 | 16SEP2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16SEP2020 08:30 | 16SEP2020 10:30 |        | Y4   |
      | ground |     |        | CPH     | CPH     | 16SEP2020 12:30 | 16SEP2020 14:30 |        | Y4   |
      | dh     | SK  | 000002 | CPH     | ARN     | 16SEP2020 19:00 | 16SEP2020 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000003 | ARN     | CPH     | 26SEP2020 05:45 | 26SEP2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26SEP2020 08:30 | 26SEP2020 10:30 |        | Y4   |
      | ground |     |        | CPH     | CPH     | 26SEP2020 12:30 | 26SEP2020 14:30 |        | Y4   |
      | dh     | SK  | 000004 | CPH     | ARN     | 26SEP2020 19:00 | 26SEP2020 20:15 | 73O    |      |

    Given crew member 1 has a personal activity "WTA22" at station "ARN" that starts at 20SEP2020 04:00 and ends at 20SEP2020 14:00
    Given trip 1 is assigned to crew member 1 in position FP
    Given trip 2 is assigned to crew member 1 in position FP

    # OPC
    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000005 | ARN     | CPH     | 16SEP2020 05:45 | 16SEP2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16SEP2020 08:30 | 16SEP2020 10:30 |        | S6   |
      | ground |     |        | CPH     | CPH     | 16SEP2020 12:30 | 16SEP2020 14:30 |        | S6   |
      | dh     | SK  | 000006 | CPH     | ARN     | 16SEP2020 19:00 | 16SEP2020 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000007 | ARN     | CPH     | 26SEP2020 05:45 | 26SEP2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26SEP2020 08:30 | 26SEP2020 10:30 |        | S6   |
      | ground |     |        | CPH     | CPH     | 26SEP2020 12:30 | 26SEP2020 14:30 |        | S6   |
      | dh     | SK  | 000008 | CPH     | ARN     | 26SEP2020 19:00 | 26SEP2020 20:15 | 73O    |      |

    Given crew member 2 has a personal activity "WTA22" at station "ARN" that starts at 20SEP2020 04:00 and ends at 20SEP2020 14:00
    Given trip 3 is assigned to crew member 2 in position FP
    Given trip 4 is assigned to crew member 2 in position FP

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 2
    and rave "training.%wt_earliest_date%" shall be "01AUG2020 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_latest_date%" shall be "01NOV2020 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_earliest_date%" shall be "01JUL2020 00:00" on leg 2 on trip 1 on roster 2
    and rave "training.%wt_latest_date%" shall be "01SEP2020 00:00" on leg 2 on trip 1 on roster 2

######################################################################################################

  @SCENARIO6
  Scenario: Web training needed before PC.
    Given planning period from 1Apr2020 to 1May2020

    Given crew member 1 has document "REC+PCA3" from 01JUN2019 to 01JUL2020
    Given crew member 1 has document "REC+OPCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+PCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+OPCA3" from 01OCT2019 to 01OCT2021

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 24APR2020 04:00 and ends at 24APR2020 14:00

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000419 | ARN     | CPH     | 26APR2020 05:45 | 26APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2020 08:30 | 26APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 26APR2020 12:30 | 26APR2020 14:30 |        | Y6   |
      | dh     | SK  | 001410 | CPH     | ARN     | 26APR2020 19:00 | 26APR2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

    Given crew member 1 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00
    Given crew member 2 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00

    When I show "crew" in window 1
    Then the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_training_cct.trng_web_training_needed" shall pass on leg 2 on trip 2 on roster 1
    and rave "rules_training_cct.%valid_trng_web_training_needed%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "rules_training_cct.%validity_trng_web_training_needed%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "rules_training_cct.%valid_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 2
    and rave "rules_training_cct.%validity_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 2

######################################################################################################

  @SCENARIO7
  Scenario: Web training needed before OPC.
    Given planning period from 1Apr2020 to 1May2020

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 04DEC2017  | 01JAN2036 |
      | region     | SKI       | 04DEC2017  | 01JAN2036 |
      | base       | STO       | 04DEC2017  | 01JAN2036 |
      | title rank | FC        | 04DEC2017  | 01JAN2036 |
      | contract   | V131-LH   | 01APR2020  | 01JAN2021 |
      | published  | 01MAY2020 | 01JAN1986  |           |

    Given crew member 3 has qualification "ACQUAL+A2" from 30OCT2017 to 01JAN2036
    Given crew member 3 has document "REC+PC" from 01OCT2019 to 01OCT2021
    Given crew member 3 has document "REC+OPC" from 01JUN2019 to 01JUL2020

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 24APR2020 04:00 and ends at 24APR2020 14:00

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000419 | ARN     | CPH     | 26APR2020 05:45 | 26APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2020 08:30 | 26APR2020 10:30 |        | S6   |
      | ground |     |        | CPH     | CPH     | 26APR2020 12:30 | 26APR2020 14:30 |        | S6   |
      | dh     | SK  | 001410 | CPH     | ARN     | 26APR2020 19:00 | 26APR2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

   Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000418 | ARN     | CPH     | 13APR2020 05:45 | 13APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 13APR2020 08:30 | 13APR2020 10:30 |        | S2   |
      | ground |     |        | CPH     | CPH     | 13APR2020 12:30 | 13APR2020 14:30 |        | S2   |
      | dh     | SK  | 001411 | CPH     | ARN     | 13APR2020 19:00 | 13APR2020 20:15 | 73O    |      |

    Given trip 2 is assigned to crew member 3 in position FC

    Given crew member 1 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00
    Given crew member 2 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00
    Given crew member 3 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00

    When I show "crew" in window 1
    Then the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 1 on trip 2 on roster 2
    and the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 1 on trip 1 on roster 3
    and the rule "rules_training_cct.trng_web_training_needed" shall pass on leg 1 on trip 2 on roster 1
    and rave "rules_training_cct.%valid_trng_web_training_needed%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "rules_training_cct.%valid_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 3
    and rave "rules_training_cct.%validity_trng_web_training_needed%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "rules_training_cct.%validity_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 3
    and rave "rules_training_cct.%valid_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 2
    and rave "rules_training_cct.%validity_trng_web_training_needed%" shall be "True" on leg 2 on trip 1 on roster 2

######################################################################################################

  @SCENARIO8
  Scenario: Web training in correct period - spring
    Given planning period from 1Apr2020 to 1May2020

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 24APR2020 04:00 and ends at 24APR2020 14:00
    Given crew member 2 has a personal activity "WTA22" at station "ARN" that starts at 24APR2020 04:00 and ends at 24APR2020 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall fail on leg 1 on trip 1 on roster 2
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 2

######################################################################################################

  @SCENARIO9
  Scenario: Web training in correct period - autumn
    Given planning period from 1Oct2020 to 1Nov2020

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020

    Given crew member 1 has a personal activity "WTA21" at station "ARN" that starts at 24OCT2020 04:00 and ends at 24OCT2020 14:00
    Given crew member 2 has a personal activity "WTA22" at station "ARN" that starts at 24OCT2020 04:00 and ends at 24OCT2020 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall pass on leg 1 on trip 1 on roster 2
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 2

######################################################################################################

  @SCENARIO10
  Scenario: Web training required before OPC FORCED, PC FORCED and PC RENEWAL.
    Given planning period from 1Apr2020 to 1May2020

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUN2020

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 01APR2020 05:45 | 01APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 01APR2020 08:30 | 01APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 01APR2020 12:30 | 01APR2020 14:30 |        | Y6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 01APR2020 19:00 | 01APR2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="PC FORCED"

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 05APR2020 05:45 | 05APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 05APR2020 08:30 | 05APR2020 10:30 |        | S6   |
      | ground |     |        | CPH     | CPH     | 05APR2020 12:30 | 05APR2020 14:30 |        | S6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 05APR2020 19:00 | 05APR2020 20:15 | 73O    |      |

    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="OPC FORCED"

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 10APR2020 05:45 | 10APR2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 10APR2020 08:30 | 10APR2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 10APR2020 12:30 | 10APR2020 14:30 |        | Y6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 10APR2020 19:00 | 10APR2020 20:15 | 73O    |      |

    Given trip 3 is assigned to crew member 1 in position FP with attribute TRAINING="PC RENEWAL"

    Given crew member 1 has a personal activity "BL20" at station "ARN" that starts at 1MAY2020 22:00 and ends at 3MAY2020 22:00

    When I show "crew" in window 1
    Then the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 2 on trip 2 on roster 1
    and the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 2 on trip 3 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 2 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 3 on roster 1

######################################################################################################

  @CORONA
  # Special Corona case: some crew completed the web training during spring but could not perform PC and
  # got their documents prolonged instead and the PC activity will be scheduled during the summer.
  # Web training rules are not applicable in this situation.
  Scenario: Special Corona case: crew with autumn PC and completed WTX2 course during spring is legal.
    Given planning period from 1Aug2020 to 1Sep2020

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01SEP2020
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01SEP2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01SEP2020
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01SEP2020

    Given table crew_training_log additionally contains the following
      | crew          | typ    | code | tim       | attr |
      | crew member 1 | COURSE | WTA2 | 17MAY2020 |      |

    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000419 | ARN     | CPH     | 15AUG2020 05:45 | 15AUG2020 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 15AUG2020 08:30 | 15AUG2020 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 15AUG2020 12:30 | 15AUG2020 14:30 |        | Y6   |
      | dh     | SK  | 001410 | CPH     | ARN     | 15AUG2020 19:00 | 15AUG2020 20:15 | 73O    |      |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FC

    Given crew member 1 has a personal activity "BL20" at station "ARN" that starts at 1SEP2020 22:00 and ends at 3SEP2020 22:00
    Given crew member 2 has a personal activity "BL20" at station "ARN" that starts at 1SEP2020 22:00 and ends at 3SEP2020 22:00

    When I show "crew" in window 1
    Then the rule "rules_training_cct.trng_web_training_needed" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_training_cct.trng_web_training_needed" shall pass on leg 3 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 3 on trip 1 on roster 1
    and the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_training_cct.trng_web_training_needed" shall fail on leg 3 on trip 1 on roster 2
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 3 on trip 1 on roster 2

######################################################################################################