Feature: Check that PC/OPC documents work.
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
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1JAN2020
    Given crew member 1 has document "REC+LC" from 1JAN2018 to 1JAN2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1JAN2018 to 1JAN2020 and has qualification "A5"
    Given crew member 1 has document "REC+PGT" from 1JAN2018 to 1JAN2020

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5FEB2019 10:00 | 5FEB2019 11:00 | 35A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5FEB2019 12:00 | 5FEB2019 13:00 | 35A    |      |

    Given trip 1 is assigned to crew member 1 in position FC


  @SCENARIO_A2A5_1 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that all documents are registered for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Apr20 (A5)"

    @SCENARIO_A2A5_2 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that PCA5 document is expired for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1FEB2019
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Jan19 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Apr20 (A5)"


  @SCENARIO_A2A5_3 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that PC (A2) document is expired for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1FEB2019 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 6FEB2019 10:00 | 6FEB2019 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 6FEB2019 12:00 | 6FEB2019 13:00 | 320    |      |

    Given trip 2 is assigned to crew member 1 in position FC


    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 2 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Jan19 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Apr20 (A5)"

    @SCENARIO_A2A5_4 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA5 document is expired for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1FEB2019
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Jan19 (A5)"


  @SCENARIO_A2A5_5 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPC (A2) document is expired for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1FEB2019 and has qualification "A2"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 6FEB2019 10:00 | 6FEB2019 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 6FEB2019 12:00 | 6FEB2019 13:00 | 320    |      |

    Given trip 2 is assigned to crew member 1 in position FC


    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall fail on leg 1 on trip 2 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Jan19 (A2), Apr20 (A5)"


  @SCENARIO_A2A5_6 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that PCA5 document is missing for A2A5 crew

    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), - (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Apr20 (A5)"


  @SCENARIO_A2A5_7 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPCA3 document is missing for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), - (A5)"


  @SCENARIO_A2A5_8 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that PC (A2) document is missing for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+OPC" from 1NOV2018 to 1NOV2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: - (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: Oct20 (A2), Apr20 (A5)"


  @SCENARIO_A2A5_9 @PC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that OPC (A2) document is missing for A2A5 crew

    Given crew member 1 has document "REC+PCA5" from 1APR2018 to 1APR2020
    Given crew member 1 has document "REC+OPCA5" from 1MAY2018 to 1MAY2020
    Given crew member 1 has document "REC+PC" from 1OCT2018 to 1OCT2020 and has qualification "A2"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 6FEB2019 10:00 | 6FEB2019 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 6FEB2019 12:00 | 6FEB2019 13:00 | 320    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%pc_str%" shall be " PC: Sep20 (A2), Mar20 (A5)"
    and rave "crg_info.%opc_str%" shall be "OPC: - (A2), Apr20 (A5)"




