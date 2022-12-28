Feature: Check that LC/LPC/OPC documents planned too early legality work
  Background: Set up common data

    Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1JAN2021
    Given crew member 1 has document "REC+PGT" from 1JAN2018 to 1JAN2021



  @SCENARIO1 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A3 FD gets illegality when assigned PC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    
    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: OPCA3 too early [1Jul-29Sep 2020]" on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "S6" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Jul20"
    and rave "crg_info.%opc_str%" shall be "OPC: Sep20"


  @SCENARIO1_A2A3 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD gets illegality when assigned A3 LPC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1"

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: OPCA3 too early [1Jul-29Sep 2020]" on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "S6" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20 (A2), Jul20 (A3)"
    and rave "crg_info.%opc_str%" shall be "OPC: Nov20 (A2), Sep20 (A3)"


  @SCENARIO2 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD is legal when assigned LPC within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "Y2" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20"
    and rave "crg_info.%opc_str%" shall be "OPC: Nov20"


  @SCENARIO2_A2A3 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is legal when assigned LPC A2 within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "Y2" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20 (A2), Jul20 (A3)"
    and rave "crg_info.%opc_str%" shall be "OPC: Nov20 (A2), Sep20 (A3)"


  @SCENARIO3 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD is illegal when assigned LC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A2"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 320    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: LC too early [1May-30Jul 2020]" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: Jul20 "


  @SCENARIO3_A2A3 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is illegal when assigned LC A2 too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 320    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: LC too early [1May-30Jul 2020]" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: Jul20 (A2), May20 (A3)"


  @SCENARIO4 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A3 FD is legal when assigned LC within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: May20 "


  @SCENARIO4_A2A3 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is legal when assigned LC A3 within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30NOV2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31JUL2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30SEP2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: Jul20 (A2), May20 (A3)"


  @SCENARIO5 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD gets illegality when assigned LPC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: OPC too early [1Jul-29Sep 2020]" on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "S2" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Jul20"
    and rave "crg_info.%opc_str%" shall be "OPC: Sep20"


  @SCENARIO5_A2A3 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD gets illegality when assigned A2 PC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: OPC too early [1Jul-29Sep 2020]" on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "S2" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Jul20 (A2), May20 (A3)"
    and rave "crg_info.%opc_str%" shall be "OPC: Sep20 (A2), Nov20 (A3)"


  @SCENARIO6 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A3 FD is legal when assigned LPC within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "Y6" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20"
    and rave "crg_info.%opc_str%" shall be "OPC: Nov20"


  @SCENARIO6_A2A3 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is legal when assigned LPC A3 within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%leg_code%" shall be "Y6" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: Jul20 (A2), May20 (A3)"
    and rave "crg_info.%opc_str%" shall be "OPC: Sep20 (A2), Nov20 (A3)"


  @SCENARIO7 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A3 FD is illegal when assigned LC too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: LC too early [1May-30Jul 2020]" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: Jul20 "


  @SCENARIO7_A2A3 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is illegal when assigned LC A3 too early
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%rec_planned_too_early_failtext%" shall be "OMA: LC too early [1May-30Jul 2020]" on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: May20 (A2), Jul20 (A3)"


  @SCENARIO8 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD is legal when assigned LC within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A2"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 320    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: May20 "


  @SCENARIO8_A2A3 @LC @DOCUMENT @RECURRENT
  Scenario: Check that A2A3 FD is legal when assigned LC A2 within grace period
    Given Tracking
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+LPCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31MAY2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1APR2018 to 31JUL2020 and has qualification "A3"

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5APR2020 10:00 | 5APR2020 11:00 | 320    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5APR2020 12:00 | 5APR2020 13:00 | 320    |      |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.lc_must_not_be_planned_too_early_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lc_str%" shall be " LC: May20 (A2), Jul20 (A3)"


  @SCENARIO9 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD is illegal when assigned two OPC within grace period
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14SEP2020 8:00 | 14SEP2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 24SEP2020 8:00 | 24SEP2020 12:00 |

    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 2 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20"
    and rave "crg_info.%opc_str%" shall be "OPC: -"


  @SCENARIO10 @LPC @OPC @DOCUMENT @RECURRENT
  Scenario: Check that A2 FD is illegal when assigned two OPC within grace period and the first is in training log
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035

    Given crew member 1 has document "REC+LPC" from 1APR2018 to 31MAY2020 and has qualification "A2"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            | attr   |
      | crew member 1 | OPC     | S2   | 4AUG2020 12:22 | 31337  |

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S2   | ARN     | ARN     | 14SEP2020 8:00 | 14SEP2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.qln_recurrent_training_must_not_be_planned_too_early_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_all_required_recurrent_dates_registered_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_recurrent_training_performed_all" shall pass on leg 1 on trip 1 on roster 1
    and rave "crg_info.%lpc_str%" shall be " LPC: May20"
    and rave "crg_info.%opc_str%" shall be "OPC: -"


  @SCENARIO11
  Scenario: Test that must and may have opc is false for A2 crew with expired OPC document but OPC session in training log
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |
    Given crew member 1 has qualification "ACQUAL+A2" from 20JAN2020 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 26MAY2020 to 01OCT2020

    Given table crew_document additionally contains the following
           | doc_typ  | validto         | crew          | si    | doc_subtype | docno               | maindocno | ac_qual | validfrom       | issuer |
           | REC      | 01OCT2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | 38      | 02OCT2019 00:00 |        |
           | REC      | 01SEP2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | A2      | 28FEB2020 00:00 |        |
           | REC      | 01APR2020 00:00 | crew member 1 |       | LPC         |                     |           | 38      | 26MAR2016 00:00 |        |
           | REC      | 01MAR2021 00:00 | crew member 1 | TPMSn | LPC         |                     |           | A2      | 28FEB2020 00:00 |        |


    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 11SEP2020 22:00 and ends at 12SEP2020 22:00

    Given table crew_training_log additionally contains the following
           | tim             | code  | typ           | attr  | crew          |
           | 20AUG2020 09:00 | S2    | OPC           | 17880 | crew member 1 |

    When I show "crew" in window 1
    and I set parameter "fundamental.%use_now_debug%" to "TRUE"
    and I set parameter "fundamental.%now_debug%" to "10AUG2020"

    Then rave "training.%must_have_opc_any%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_opc_any%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO12
  Scenario: Test that must and may have opc is false for A2 crew with expired OPC document but OPC session on roster
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |
    Given crew member 1 has qualification "ACQUAL+A2" from 20JAN2020 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 26MAY2020 to 01OCT2020

    Given table crew_document additionally contains the following
           | doc_typ  | validto         | crew          | si    | doc_subtype | docno               | maindocno | ac_qual | validfrom       | issuer |
           | REC      | 01OCT2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | 38      | 02OCT2019 00:00 |        |
           | REC      | 01SEP2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | A2      | 28FEB2020 00:00 |        |
           | REC      | 01APR2020 00:00 | crew member 1 |       | LPC         |                     |           | 38      | 26MAR2016 00:00 |        |
           | REC      | 01MAR2021 00:00 | crew member 1 | TPMSn | LPC         |                     |           | A2      | 28FEB2020 00:00 |        |


    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep           | arr             |
     | ground | S2   | ARN     | ARN     | 5SEP2020 8:00 | 5SEP2020 12:00 |
    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 11SEP2020 22:00 and ends at 12SEP2020 22:00


    When I show "crew" in window 1
    and I set parameter "fundamental.%use_now_debug%" to "TRUE"
    and I set parameter "fundamental.%now_debug%" to "10AUG2020"

    Then rave "training.%must_have_opc_any%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_opc_any%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO13
  Scenario: Test that must and may have opc is true for A2 crew with expired OPC document and no OPC session planned
    Given Tracking
    Given planning period from 1SEP2020 to 30SEP2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |
    Given crew member 1 has qualification "ACQUAL+A2" from 20JAN2020 to 01JAN2036
    Given crew member 1 has acqual restriction "ACQUAL+A2+NEW+ACTYPE" from 26MAY2020 to 01OCT2020

    Given table crew_document additionally contains the following
           | doc_typ  | validto         | crew          | si    | doc_subtype | docno               | maindocno | ac_qual | validfrom       | issuer |
           | REC      | 01OCT2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | 38      | 02OCT2019 00:00 |        |
           | REC      | 01SEP2020 00:00 | crew member 1 | TPMSn | OPC         |                     |           | A2      | 28FEB2020 00:00 |        |
           | REC      | 01APR2020 00:00 | crew member 1 |       | LPC         |                     |           | 38      | 26MAR2016 00:00 |        |
           | REC      | 01MAR2021 00:00 | crew member 1 | TPMSn | LPC         |                     |           | A2      | 28FEB2020 00:00 |        |


    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 11SEP2020 22:00 and ends at 12SEP2020 22:00

    When I show "crew" in window 1
    and I set parameter "fundamental.%use_now_debug%" to "TRUE"
    and I set parameter "fundamental.%now_debug%" to "10AUG2020"

    Then rave "training.%must_have_opc_any%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%may_have_opc_any%" shall be "True" on leg 1 on trip 1 on roster 1
