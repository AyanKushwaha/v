Feature: Check that LPC/OPC documents work.
  Background: Set up common data
    Given planning period from 1FEB2019 to 28FEB2019

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1JAN2020
    Given crew member 1 has document "REC+LC" from 1JAN2018 to 1JAN2020 and has qualification "A3"
    Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1JAN2020
    Given crew member 1 has document "REC+PGT" from 1JAN2018 to 1JAN2020

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5FEB2019 10:00 | 5FEB2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5FEB2019 12:00 | 5FEB2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC


  @SCENARIO_A3A4_1 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_2 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that LPCA3 document is expired for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1FEB2019
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " LPC: Jan19 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_3 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that LPCA4 document is expired for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1FEB2019
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Mar20 (A3), Jan19 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_4 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA3 document is expired for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1FEB2019
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Jan19 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_5 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA4 document is expired for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1FEB2019

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Jan19 (A4)"


  @SCENARIO_A3A4_6 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that LPCA3 document is missing for A3A4 crew

    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: - (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_7 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA3 document is missing for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: - (A3), Oct20 (A4)"


  @SCENARIO_A3A4_8 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that PCA4 document is missing for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), - (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A3A4_9 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA4 document is missing for A3A4 crew

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), - (A4)"


  @SCENARIO_A5_1 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A5 crew when FAM FLTs have not been completed

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A5_2 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A5 crew when FAM FLTs are in training log

    Given crew member 1 has document "REC+LPCA3" from 1JUN2018 to 7JAN2019
    Given crew member 1 has document "REC+OPCA3" from 1JUL2018 to 7JAN2019
    Given crew member 1 has document "REC+LPCA3A5" from 7JAN2019 to 1JUN2020
    Given crew member 1 has document "REC+OPCA3A5" from 7JAN2019 to 1JUL2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            |
      | crew member 1 | FAM FLT | A5   | 4JAN2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 6JAN2019 12:22 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20 (A3/A5), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Jun20 (A3/A5), Oct20 (A4)"


  @SCENARIO_A5_3 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A5 crew when FAM FLTs are in roster for OPCA3 and LPCA3

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
    | leg | 0001 | ARN     | LHR     | 7FEB2019 10:00 | 7FEB2019 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | ARN     | 7FEB2019 12:00 | 7FEB2019 13:00 | SK  | 35X    |

    Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Mar20 (A3), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Apr20 (A3), Oct20 (A4)"


  @SCENARIO_A5_4 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A5 crew when FAM FLTs are in roster for OPCA3A5 and LPCA3A5

    Given crew member 1 has document "REC+LPCA3" from 1JUN2018 to 8FEB2019
    Given crew member 1 has document "REC+OPCA3" from 1JUL2018 to 8FEB2019
    Given crew member 1 has document "REC+LPCA3A5" from 8FEB2019 to 1JUN2020
    Given crew member 1 has document "REC+OPCA3A5" from 8FEB2019 to 1JUL2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
    | leg | 0001 | ARN     | LHR     | 7FEB2019 10:00 | 7FEB2019 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | ARN     | 7FEB2019 12:00 | 7FEB2019 13:00 | SK  | 35X    |

    Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20 (A3/A5), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Jun20 (A3/A5), Oct20 (A4)"


  @SCENARIO_A5_5 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that LPCA3A5 document is not registered for A5 crew when FAM FLTs are in roster for OPCA3A5 and LPCA3A5

    Given crew member 1 has document "REC+OPCA3" from 1JUL2018 to 8FEB2019
    Given crew member 1 has document "REC+OPCA3A5" from 8FEB2019 to 1JUL2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
    | leg | 0001 | ARN     | LHR     | 7FEB2019 10:00 | 7FEB2019 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | ARN     | 7FEB2019 12:00 | 7FEB2019 13:00 | SK  | 35X    |

    Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: - (A3/A5), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: Jun20 (A3/A5), Oct20 (A4)"


  @SCENARIO_A5_6 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA3A5 document is not registered for A5 crew when FAM FLTs are in roster for OPCA3A5 and LPCA3A5

    Given crew member 1 has document "REC+LPCA3" from 1JUN2018 to 8FEB2019
    Given crew member 1 has document "REC+LPCA3A5" from 8FEB2019 to 1JUN2020
    Given crew member 1 has document "REC+LPCA4" from 1OCT2018 to 1OCT2020
    Given crew member 1 has document "REC+OPCA4" from 1NOV2018 to 1NOV2020

    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
    | leg | 0001 | ARN     | LHR     | 7FEB2019 10:00 | 7FEB2019 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | ARN     | 7FEB2019 12:00 | 7FEB2019 13:00 | SK  | 35X    |

    Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="FAM FLT"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20 (A3/A5), Sep20 (A4)"
    and rave "crg_info.%opc_str%" shall be "OPC: - (A3/A5), Oct20 (A4)"
    