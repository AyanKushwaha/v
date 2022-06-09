@FD @PC @OPC @TRAINING
Feature: Test that web trainings are scheduled correct relatively PC/OPC.

  Background:
    Given Tracking

    Given table agreement_validity additionally contains the following
      | id                    | validfrom | validto   |
      | web_training_pc_LH_17 | 1JAN2000  | 31DEC2035 |
      | web_training_pc_22    | 1JAN2021  | 31DEC2035 |

    Given a crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 04DEC2017  | 01JAN2036 |
      | region     | SKI       | 04DEC2017  | 01JAN2036 |
      | base       | STO       | 04DEC2017  | 01JAN2036 |
      | title rank | FC        | 04DEC2017  | 01JAN2036 |
      | contract   | V131-LH   | 01APR2021  | 01JAN2022 |
      | published  | 01MAY2022 | 01JAN1986  |           |

    Given another crew member with
      | attribute  | value     | valid from | valid to  |
      | sex        | M         |            |           |
      | crew rank  | FC        | 04DEC2017  | 01JAN2036 |
      | region     | SKI       | 04DEC2017  | 01JAN2036 |
      | base       | STO       | 04DEC2017  | 01JAN2036 |
      | title rank | FC        | 04DEC2017  | 01JAN2036 |
      | contract   | V131-LH   | 01APR2021  | 01JAN2022 |
      | published  | 01MAY2022 | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+A3" from 30OCT2017 to 01JAN2036
    Given crew member 2 has qualification "ACQUAL+A3" from 30OCT2017 to 01JAN2036

######################################################################################################

  @SCENARIO1
  Scenario: Duplicated web trainings should be avoided - spring.
    Given planning period from 1Apr2022 to 1May2022

    Given crew member 1 has document "REC+PCA3" from 1APR2021 to 1APR2024
    Given crew member 1 has document "REC+OPCA3" from 1APR2021 to 1MAY2022

    Given crew member 1 has a personal activity "W21A3" at station "ARN" that starts at 20APR2022 04:00 and ends at 20APR2022 14:00
    Given crew member 1 has a personal activity "W21A3" at station "ARN" that starts at 24APR2022 04:00 and ends at 24APR2022 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_web_trg_not_duplicated_FC" shall fail on leg 1 on trip 2 on roster 1

######################################################################################################

  @SCENARIO2
  Scenario: Duplicated web trainings should be avoided - autumn.
    Given planning period from 01Sep2022 to 01Oct2022

    Given crew member 1 has document "REC+PCA3" from 1APR2020 to 1NOV2022
    Given crew member 1 has document "REC+OPCA3" from 1APR2021 to 1MAY2022

    Given crew member 1 has a personal activity "W22A3" at station "ARN" that starts at 20SEP2022 04:00 and ends at 20SEP2022 14:00
    Given crew member 1 has a personal activity "W22A3" at station "ARN" that starts at 24SEP2022 04:00 and ends at 24SEP2022 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_web_trg_not_duplicated_FC" shall fail on leg 1 on trip 2 on roster 1

######################################################################################################

  @SCENARIO3
  Scenario: Missing web training within spring eval period before PC or OPC is illegal.
    Given planning period from 01Apr2022 to 01May2022

    Given crew member 1 has document "REC+PCA3" from 1APR2020 to 1APR2022
    Given crew member 1 has document "REC+OPCA3" from 1APR2021 to 1APR2022

    Given crew member 2 has qualification "ACQUAL+A4" from 30OCT2017 to 01JAN2036
    Given crew member 2 has document "REC+PCA3" from 1APR2021 to 1APR2022
    Given crew member 2 has document "REC+OPCA3" from 1APR2021 to 1MAY2022
    Given crew member 2 has document "REC+PCA4" from 1APR2021 to 1APR2022
    Given crew member 2 has document "REC+OPCA4" from 1APR2021 to 1MAY2022

    # PC
    Given a trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000001 | ARN     | CPH     | 16APR2022 05:45 | 16APR2022 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16APR2022 08:30 | 16APR2022 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 16APR2022 12:30 | 16APR2022 14:30 |        | Y6   |
      | dh     | SK  | 000002 | CPH     | ARN     | 16APR2022 19:00 | 16APR2022 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000003 | ARN     | CPH     | 26APR2022 05:45 | 26APR2022 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2022 08:30 | 26APR2022 10:30 |        | Y6   |
      | ground |     |        | CPH     | CPH     | 26APR2022 12:30 | 26APR2022 14:30 |        | Y6   |
      | dh     | SK  | 000004 | CPH     | ARN     | 26APR2022 19:00 | 26APR2022 20:15 | 73O    |      |

    Given crew member 1 has a personal activity "W11A3" at station "ARN" that starts at 20APR2022 04:00 and ends at 20APR2022 14:00
    Given trip 1 is assigned to crew member 1 in position FP
    Given trip 2 is assigned to crew member 1 in position FP

    # OPC
    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000005 | ARN     | CPH     | 16APR2022 05:45 | 16APR2022 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 16APR2022 08:30 | 16APR2022 10:30 |        | S4   |
      | ground |     |        | CPH     | CPH     | 16APR2022 12:30 | 16APR2022 14:30 |        | S4   |
      | dh     | SK  | 000006 | CPH     | ARN     | 16APR2022 19:00 | 16APR2022 20:15 | 73O    |      |

    Given another trip with the following activities
      | act    | car | num    | dep stn | arr stn | dep             | arr             | ac_typ | code |
      | dh     | SK  | 000007 | ARN     | CPH     | 26APR2022 05:45 | 26APR2022 06:55 | 73O    |      |
      | ground |     |        | CPH     | CPH     | 26APR2022 08:30 | 26APR2022 10:30 |        | S4   |
      | ground |     |        | CPH     | CPH     | 26APR2022 12:30 | 26APR2022 14:30 |        | S4   |
      | dh     | SK  | 000008 | CPH     | ARN     | 26APR2022 19:00 | 26APR2022 20:15 | 73O    |      |

    Given crew member 2 has a personal activity "W11A3" at station "ARN" that starts at 20APR2022 04:00 and ends at 20APR2022 14:00
    Given trip 3 is assigned to crew member 2 in position FP
    Given trip 4 is assigned to crew member 2 in position FP

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 1
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall fail on leg 2 on trip 1 on roster 2
    and the rule "rules_qual_ccr.qln_min_days_btw_pc_opc_and_web_trg_FC" shall pass on leg 2 on trip 3 on roster 2
    and rave "training.%wt_earliest_date%" shall be "01JAN2022 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_latest_date%" shall be "01APR2022 00:00" on leg 2 on trip 1 on roster 1
    and rave "training.%wt_earliest_date%" shall be "01JAN2022 00:00" on leg 2 on trip 1 on roster 2
    and rave "training.%wt_latest_date%" shall be "01APR2022 00:00" on leg 2 on trip 1 on roster 2

######################################################################################################

  @SCENARIO4
  Scenario: Web training in correct period - spring
    Given planning period from 1Apr2022 to 1May2022

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020

    Given crew member 1 has a personal activity "W21A3" at station "ARN" that starts at 24APR2022 04:00 and ends at 24APR2022 14:00
    Given crew member 2 has a personal activity "W22A3" at station "ARN" that starts at 24APR2022 04:00 and ends at 24APR2022 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall fail on leg 1 on trip 1 on roster 2
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 2

######################################################################################################

  @SCENARIO5
  Scenario: Web training in correct period - autumn
    Given planning period from 1Oct2022 to 1Nov2022

    Given crew member 1 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 1 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020
    Given crew member 2 has document "REC+PCA3" from 01OCT2019 to 01OCT2021
    Given crew member 2 has document "REC+OPCA3" from 01JUN2019 to 01JUL2020

    Given crew member 1 has a personal activity "W21A3" at station "ARN" that starts at 24OCT2022 04:00 and ends at 24OCT2022 14:00
    Given crew member 2 has a personal activity "W22A3" at station "ARN" that starts at 24OCT2022 04:00 and ends at 24OCT2022 14:00

    When I show "crew" in window 1
    Then the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_correct_season_for_web_training_FC" shall pass on leg 1 on trip 1 on roster 2
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%is_spring_web_training%(task.%code%)" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "training.%is_autumn_web_training%(task.%code%)" shall be "True" on leg 1 on trip 1 on roster 2

######################################################################################################

  