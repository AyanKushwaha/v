@CC @TRAINING @CRMC
Feature: Check if CRMC is valid for CC.

  @SCENARIO_01
  Scenario: CC has no CRMC document and employment date is before 01jan2020
    Given planning period from 01NOV2021 to 31Dec2021
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05Dec2021 10:00 | 05DEC2021 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05Dec2021 13:00 | 05DEC2021 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_02
  Scenario: CC has no CRMC document and employment date is before 01jan2020 illegal after 31dec2022
    Given planning period from 01JAN2023 to 31JAN2023
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05JAN2023 10:00 | 05JAN2023 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05JAN2023 13:00 | 05JAN2023 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%qln_all_required_dates_registered_ALL_failtext%" shall be "OMA: Recurrent dates not registered CRMC, CRMC"
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "True" on leg 1 on trip 1 on roster 1


  @SCENARIO_03
  Scenario: CC has no CRMC and no REC document and employment date is before 01jan2020
    Given planning period from 01NOV2021 to 31Dec2021
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2018  |          |
      | contract   | V00863 | 01FEB2018  |          |
      | employment |        | 01FEB2018  |          |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05Dec2021 10:00 | 05DEC2021 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05Dec2021 13:00 | 05DEC2021 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%qln_all_required_dates_registered_ALL_failtext%" shall be "OMA: Recurrent dates not registered REC"
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_04
  Scenario: CC has no CRMC document and employment date is after 01jan02020
    Given planning period from 01NOV2021 to 31DEC2021
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01FEB2021  |          |
      | contract   | V00863 | 01FEB2021  |          |
      | employment |        | 01FEB2021  |          |


    Given crew member 1 has document "REC+REC" from 01JAN2021 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05DEC2021 10:00 | 05DEC2021 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05DEC2021 13:00 | 05DEC2021 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%qln_all_required_dates_registered_ALL_failtext%" shall be "OMA: Recurrent dates not registered CRMC, CRMC"
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "True" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_05
  Scenario: Check CC with employment start date 01Jan2020 or later and holds a CRMC document.
    Given planning period from 01JAN2020 to 30JAN2020
    Given another crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 01JAN2020 | 31DEC2020 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | REC         | 01JAN2020 | 31DEC2020 | ""    | ""        | ""     | "" | ""      |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 10JAN2020 10:00 | 10JAN2020 12:00 | 219    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 10JAN2020 13:00 | 10JAN2020 15:00 | 219    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_06
  Scenario: From 01Jan2023 the CC should have a valid CRMC document for active flight (Contract before 1Jan2020)
    Given planning period from 01NOV2024 to 30NOV2024
    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2019  |          |
      | contract   | V00863 | 01JAN2019  |          |
      | employment |        | 01JAN2019  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | REC         | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05NOV2024 10:00 | 05NOV2024 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05NOV2024 13:00 | 05NOV2024 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_07
  Scenario: From 01Jan2023 the CC should have a valid CRMC document for active flight (Contract after 1Jan2020)

    Given planning period from 01DEC2024 to 31DEC2024

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | REC         | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05DEC2024 10:00 | 05DEC2024 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05DEC2024 13:00 | 05DEC2024 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "True" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_08
  Scenario: The CC is hired after 31.Dec.2022

    Given planning period from 01Sep2024 to 30Sep2024

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2023  |          |
      | contract   | V00863 | 01JAN2023  |          |
      | employment |        | 01JAN2023  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | REC         | 01Jan2024 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05SEP2024 10:00 | 05SEP2024 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05SEP2024 13:00 | 05SEP2024 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_09
  Scenario: Scenario: The CC is hired 01.Jan.2018

    Given planning period from 01Sep2024 to 30Sep2024

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2018  |          |
      | contract   | V00863 | 01JAN2018  |          |
      | employment |        | 01JAN2018  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 01Jan2020 | 31Dec2022 | ""    | ""        | ""     | "" | ""      |
      | crew member 1 | REC     | REC         | 01Jan2020 | 31Dec2024 | ""    | ""        | ""     | "" | ""      |

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05SEP2024 10:00 | 05SEP2024 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05SEP2024 13:00 | 05SEP2024 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%missed_recurrent_training_failtext%" shall be "OMA: Rec. expiry dates passed, needs: CRMC, CRMC"
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "True" on leg 1 on trip 1 on roster 1


#############################################################################################################################
############ rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all ########################################
#############################################################################################################################

  @SCENARIO_10
  Scenario: CRMC planned correctly for crew employed 1JAN2020

    Given planning period from 01dec2020 to 30dec2020

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 12Jan2020 | 31DEC2020 | ""    | ""        | ""     | "" | ""      |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1dec2020 10:00 | 1dec2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_11
  Scenario: CRMC planned correctly for crew employed 1JAN2020 but just one session
    Given Tracking
    Given planning period from 01dec2020 to 30dec2020

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 12Jan2020 | 31DEC2020 | ""    | ""        | ""     | "" | ""      |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep             | arr             | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1dec2020 10:00  | 1dec2020 17:00  |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep             | arr             | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 11dec2020 10:00 | 11dec2020 17:00 |        | SK  |     |      |

    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall fail on leg 1 on trip 2 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_12
  Scenario: CRMC planned too early for crew employed 1JAN2020

    Given planning period from 01sep2020 to 30sep2020

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2020  |          |
      | contract   | V00863 | 01JAN2020  |          |
      | employment |        | 01JAN2020  |          |

    Given table crew_document additionally contains the following
      | crew          | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer | si | ac_qual |
      | crew member 1 | REC     | CRMC        | 12Jan2020 | 31DEC2020 | ""    | ""        | ""     | "" | ""      |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1sep2020 10:00 | 1sep2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: CRMC too early [1Oct-30Dec 2020]" on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_13
  Scenario: CRMC can be planned in full period 1JAN2020 - 31DEC2022 for CC who is employed before 2020

    Given planning period from 01dec2020 to 31dec2020

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2018  |          |
      | contract   | V00863 | 01JAN2018  |          |
      | employment |        | 01JAN2018  |          |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 1dec2020 10:00 | 1dec2020 17:00 |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position AH

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 05Dec2020 10:00 | 05DEC2020 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 05Dec2020 13:00 | 05DEC2020 15:00 | 319     | SK  |      |      |

    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_14
  Scenario: CRMC can be planned in full period 1JAN2020 - 31DEC2022 for CC who is employed before 2020 but just one session

    Given planning period from 1FEB2020 to 31MAY2020

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2018  |          |
      | contract   | V00863 | 01JAN2018  |          |
      | employment |        | 01JAN2018  |          |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep             | arr             | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 23FEB2020 10:00  | 23FEB2020 17:00  |        | SK  |     |      |

    Given trip 1 is assigned to crew member 1 in position AH

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | dep             | arr             | ac_typ | car | num | date |
      | ground | CRMC | ARN     | ARN     | 20MAY2020 10:00 | 20MAY2020 17:00 |        | SK  |     |      |

    Given trip 2 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_All" shall fail on leg 1 on trip 2 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


####################################################################################################################
############ rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL ########################################
####################################################################################################################
  @SCENARIO_15
  Scenario: Verify that the CRMC document fits for REC+CRMC for CC after 2022

    Given planning period from 01SEP2022 to 30SEP2022

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2022  |          |
      | contract   | V00863 | 01JAN2022  |          |
      | employment |        | 01JAN2022  |          |


    Given crew member 1 has document "REC+CRMC" from 01JAN2022 to 31Dec2022
    Given crew member 1 has document "REC+REC" from 01JAN2022 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 12SEP2022 10:00 | 12SEP2022 12:00 | 319     | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 12SEP2022 13:00 | 12SEP2022 15:00 | 319     | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_16
  Scenario: Verify that the CRMC document fits for REC+CRMC for CC before 2022

    Given planning period from 01SEP2022 to 30SEP2022

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2018  |          |
      | contract   | V00863 | 01JAN2018  |          |
      | employment |        | 01JAN2018  |          |

    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 31Dec2022
    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 12SEP2022 10:00 | 12SEP2022 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 12SEP2022 13:00 | 12SEP2022 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_crmc%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "False" on leg 1 on trip 1 on roster 1


##################################################################
##################################################################
##################################################################
  @SCENARIO_17
  Scenario: Verify rule failures when CRMC document expired before flight

    Given planning period from 01Dec2023 to 30Dec2023

    Given a crew member with
      | attribute  | value  | valid from | valid to |
      | crew rank  | AH     |            |          |
      | title rank | AH     |            |          |
      | region     | SKS    |            |          |
      | base       | STO    | 01JAN2019  |          |
      | contract   | V00863 | 01JAN2019  |          |
      | employment |        | 01JAN2019  |          |

    Given crew member 1 has document "REC+CRMC" from 01JAN2020 to 31Dec2022
    Given crew member 1 has document "REC+REC" from 01JAN2020 to 31Dec2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ | car | code | date |
      | leg | SK  | 001 | ARN     | HEL     | 12DEC2023 10:00 | 12DEC2023 12:00 | 319    | SK  |      |      |
      | leg | SK  | 002 | HEL     | ARN     | 12DEC2023 13:00 | 12DEC2023 15:00 | 319    | SK  |      |      |

    Given trip 1 is assigned to crew member 1 in position AH

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%missed_recurrent_training_failtext%" shall be "OMA: Rec. expiry dates passed, needs: CRMC, CRMC"
    and rave "training.%may_have_crmc%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%must_have_in_pp%(\"CRMC\")" shall be "True" on leg 1 on trip 1 on roster 1
