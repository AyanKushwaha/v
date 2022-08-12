@JCRT @TRAINING @ALL @FD @SKCMS-2875
Feature: Rule that controls that crew needing PC is not assigned to same sim slot as crew needing OPC (OTS)

  Background:
    Given planning period from 1JAN2022 to 31JAN2022
  @SCENARIO1
  Scenario: Check that rule fails when PC and OTS in same sim slot
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+PC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+PCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "True" on leg 1 on trip 1 on roster 1

@SCENARIO2
  Scenario: Check that rule passes when both sim slots have PC required crew
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SIM ASSIST"
    Given trip 1 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "False" on leg 1 on trip 1 on roster 1

@SCENARIO3
  Scenario: Check that rule passes in case of SIM ASSIST crew
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+PC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+PCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SIM ASSIST"
    Given trip 1 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "False" on leg 1 on trip 1 on roster 1

@SCENARIO4
  Scenario: Check that rule passes in case of SIM INSTR crew
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+PC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+PCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SIM INSTR"
    Given trip 1 is assigned to crew member 2 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "False" on leg 1 on trip 1 on roster 1

@SCENARIO5
  Scenario: Check that rule passes in case of SIM INSTR crew and fails for other crew with mismatch
    Given planning period from 1APR2020 to 30APR2020

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |
    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKI   |
      | base       | STO   |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 1 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 1 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has document "REC+OPC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 2 has document "REC+PC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 2 has document "REC+OPCA3" from 1APR2018 to 31MAY2020
    Given crew member 2 has document "REC+PCA3" from 1MAY2018 to 30NOV2020
  
    Given crew member 3 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 3 has document "REC+PC" from 1APR2018 to 31JUL2020 and has qualification "A2"
    Given crew member 3 has document "REC+OPC" from 1MAY2018 to 30SEP2020 and has qualification "A2"
    Given crew member 3 has document "REC+PCA3" from 1APR2018 to 31MAY2020
    Given crew member 3 has document "REC+OPCA3" from 1MAY2018 to 30NOV2020

    Given a trip with the following activities
     | act    | code | dep stn | arr stn | dep            | arr             |
     | ground | S6   | ARN     | ARN     | 14APR2020 8:00 | 14APR2020 12:00 |

    Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="SIM INSTR"
    Given trip 1 is assigned to crew member 2 in position FC
    Given trip 1 is assigned to crew member 3 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall pass on leg 1 on trip 1 on roster 1
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.comp_mixed_pc_ots_not_allowed_in_sim" shall fail on leg 1 on trip 1 on roster 2
    and rave "rules_training_ccr.%has_pc_opc_mismatch%" shall be "True" on leg 1 on trip 1 on roster 2