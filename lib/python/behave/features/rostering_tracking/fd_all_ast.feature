Feature: Check that AST recurrents work.
  Background: Set up common data
    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given table property is overridden with the following
      | id                    | validfrom | validto   | value_abs |
      | ast_period_start_38   | 1JAN1986  | 31DEC2035 | 1JAN2019  |
      | ast_period_end_38     | 1JAN1986  | 31DEC2035 | 1MAY2019  |
      | ast_period_start_A2   | 1JAN1986  | 31DEC2035 | 1MAR2019  |
      | ast_period_end_A2     | 1JAN1986  | 31DEC2035 | 1MAY2019  |
      | ast_period_start_A3A4 | 1JAN1986  | 31DEC2035 | 1APR2019  |
      | ast_period_end_A3A4   | 1JAN1986  | 31DEC2035 | 1JUL2019  |
      | ast_period_start_A5   | 1JAN1986  | 31DEC2035 | 1JAN2020  |
      | ast_period_end_A5     | 1JAN1986  | 31DEC2035 | 30JUN2020 |

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


  @SCENARIO_38_1
  Scenario: Check that 38 crew with AST in training log does not need AST
    Given planning period from 1FEB2019 to 28FEB2019
    
    Given crew member 1 has qualification "ACQUAL+38" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+38" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5FEB2019 10:00 | 5FEB2019 11:00 | 738    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5FEB2019 12:00 | 5FEB2019 13:00 | 738    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K3   | 17JAN2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A2_1
  Scenario: Check that A2 crew with AST in training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5MAY2019 11:00 | 32A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5MAY2019 13:00 | 32A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K2   | 17APR2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_1
  Scenario: Check that A3 crew with AST in training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K6   | 17MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_2
  Scenario: Check that A3 crew with AST in roster does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_3
  Scenario: Check that A3 crew with skill test in training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has the following training need
      | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
      | 1    | CONV TYPERATING | ZFTT LIFUS | 1MAY2019   | 20MAY2019  | 4       | 0        | A3     |
    
    Given table crew_training_log additionally contains the following
      | crew          | typ           | code | tim       | attr          |
      | crew member 1 | PC SKILL TEST | Z6   | 17MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_4
  Scenario: Check that A3 crew with skill test in roster does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has the following training need
      | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
      | 1    | CONV TYPERATING | ZFTT LIFUS | 1JUN2019   | 20JUN2019  | 4       | 0        | A3     |
    
    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | Y6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_5
  Scenario: Check that A3 crew with no AST or skill test in roster or training log needs AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A3_6
  Scenario: Check that A3 crew with skill test in roster and in training log warns about several ast in period.
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has the following training need
      | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
      | 1    | CONV TYPERATING | ZFTT LIFUS | 1JUN2019   | 20JUN2019  | 4       | 0        | A3     |
    
    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z6   | 02MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall fail on leg 1 on trip 2 on roster 1


  @SCENARIO_A3_7
  Scenario: Check that A3 crew with skill test in roster and in training log outside of period does not warn.
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given crew member 1 has the following training need
      | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
      | 1    | CONV TYPERATING | ZFTT LIFUS | 1JUN2019   | 20JUN2019  | 4       | 0        | A3     |
    
    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z6   | 02MAR2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall pass on leg 1 on trip 2 on roster 1

    
  @SCENARIO_A4_1
  Scenario: Check that A4 crew with AST in training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019
    
    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 34A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 34A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K4   | 17MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1 
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A5_1
  Scenario: Check that A5 crew with no CTR-A3A5 course and AST in training log does not need AST
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5MAY2020 10:00 | 5MAY2020 11:00 | 35X    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5MAY2020 12:00 | 5MAY2020 13:00 | 35X    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K5   | 28APR2020 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A5_2
  Scenario: Check that A5 crew with CTR-A3A5 course ending 26APR2020 and AST in training log does not need AST
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5MAY2020 10:00 | 5MAY2020 11:00 | 35X    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5MAY2020 12:00 | 5MAY2020 13:00 | 35X    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            | attr          |
      | crew member 1 | AST     | K5   | 28APR2020      | crew member 2 |

    Given table crew_training_need additionally contains the following
      | crew            | part | course   | validfrom | validto   | completion |
      | crew member 1   | 1    | CTR-A3A5 | 1APR2020  | 26APR2020 | 26APR2020  |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A5_3
  Scenario: Check that A5 crew with CTR-A3A5 course ending 26APR2020 and AST in roster does not need AST
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5MAY2020 10:00 | 5MAY2020 11:00 | 35X    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5MAY2020 12:00 | 5MAY2020 13:00 | 35X    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K5   | ARN     | ARN     | 6MAY2020 10:00 | 6MAY2020 11:00 |

    Given trip 2 is assigned to crew member 1

    Given table crew_training_need additionally contains the following
      | crew            | part | course   | validfrom | validto   | completion |
      | crew member 1   | 1    | CTR-A3A5 | 1APR2020  | 26APR2020 | 26APR2020  |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A5_4
  Scenario: Check that A5 crew with CTR-A3A5 course ending 26APR2020 and no AST in roster or training log needs AST
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5MAY2020 10:00 | 5MAY2020 11:00 | 35X    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5MAY2020 12:00 | 5MAY2020 13:00 | 35X    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            | attr          |
      | crew member 1 | FAM FLT | A5   | 4APR2020 12:22 |               |
      | crew member 1 | FAM FLT | A5   | 6APR2020 12:22 |               |

    Given table crew_training_need additionally contains the following
      | crew            | part | course   | validfrom | validto   | completion |
      | crew member 1   | 1    | CTR-A3A5 | 1APR2020  | 26APR2020 | 26APR2020  |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_A5_5
  Scenario: Check that A5 crew with CTR-A3A5 course ending 27APR2020 and AST in A3A4 period does not need AST
    Given planning period from 1MAY2020 to 31MAY2020

    Given crew member 1 has qualification "ACQUAL+A2" from 1APR2016 to 31DEC2035    
    Given crew member 1 has qualification "ACQUAL+A3" from 1APR2016 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A4" from 1APR2016 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5MAY2020 10:00 | 5MAY2020 11:00 | 35X    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5MAY2020 12:00 | 5MAY2020 13:00 | 35X    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            | attr          |
      | crew member 1 | FAM FLT | A5   | 4APR2020 12:22 |               |
      | crew member 1 | FAM FLT | A5   | 6APR2020 12:22 |               |
      | crew member 1 | AST     | K4   | 5MAY2019       | crew member 2 |


    Given table crew_training_need additionally contains the following
      | crew            | part | course   | validfrom | validto   | completion |
      | crew member 1   | 1    | CTR-A3A5 | 1APR2020  | 27APR2020 | 27APR2020  |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1

  @SCENARIO_A5_6
  Scenario: Check that A5 crew with CTR-A3A5 course ending 26APR2020 in the future and no AST in roster or training log needs AST
    Given planning period from 1JAN2020 to 31JAN2020
    
    Given crew member 1 has qualification "ACQUAL+A3" from 1APR2017 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JAN2020 10:00 | 5JAN2020 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JAN2020 12:00 | 5JAN2020 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim            | attr          |
      | crew member 1 | FAM FLT | A5   | 4APR2020 12:22 |               |
      | crew member 1 | FAM FLT | A5   | 6APR2020 12:22 |               |

    Given table crew_training_need additionally contains the following
      | crew            | part | course   | validfrom | validto   | completion |
      | crew member 1   | 1    | CTR-A3A5 | 1APR2020  | 26APR2020 |            |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1


  @SCENARIO_INSTRUCTOR_1
  Scenario: Check that instructor can be assigned as acting instructor to an AST of a different qualification group then their own
    Given planning period from 1FEB2019 to 28FEB2019

    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+SFE" from 1FEB2018 to 28FEB2019
    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+SFE" from 1FEB2018 to 28FEB2019
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6FEB2019 10:00 | 6FEB2019 12:00 |

    Given trip 1 is assigned to crew member 1 in position TR with attribute INSTRUCTOR="SIM INSTR SUPERVIS"


    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_soft_ccr_cct.sft_activity_not_allowed_on_day_all" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO_INSTRUCTOR_2
  Scenario: Check that instructor cannot be assigned as student to an AST of a different qualification group than their own
    Given planning period from 1FEB2019 to 28FEB2019

    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+SFE" from 1FEB2018 to 28FEB2019
    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 1FEB2018 to 28FEB2019
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+SFE" from 1FEB2018 to 28FEB2019
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6FEB2019 10:00 | 6FEB2019 12:00 |

    Given trip 1 is assigned to crew member 1 in position TL


    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_soft_ccr_cct.sft_activity_not_allowed_on_day_all" shall fail on leg 1 on trip 1 on roster 1

  @SCENARIO_A2A3_1
  Scenario: Check that A2A3 crew with no AST or skill test in roster or training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1

  @SCENARIO_A2A3_2
  Scenario: Check that A2A3 crew with A3 skill test in roster gets a warning - as there is no need
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z6   | 02MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.no_ast_for_a2a3_fc" shall fail on leg 1 on trip 2 on roster 1

  @SCENARIO_A2A3_3
  Scenario: Check that A2A3 crew with A3 skill test in roster gets a warning - as there is no need
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K2   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z2   | 02MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.no_ast_for_a2a3_fc" shall fail on leg 1 on trip 2 on roster 1

    @SCENARIO_A2A5_1
  Scenario: Check that A2A5 crew with no AST or skill test in roster or training log does not need AST
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 35A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 35A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A5%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%too_many_ast_in_ast_period%" shall be "False" on leg 1 on trip 1 on roster 1

    @SCENARIO_A2A5_2
  Scenario: Check that A2A5 crew with A5 skill test in roster gets a warning - as there is no need
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 35A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 35A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K6   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z6   | 02MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.no_ast_for_a2a5_fc" shall fail on leg 1 on trip 2 on roster 1

    @SCENARIO_A2A5_3
  Scenario: Check that A2A5 crew with A5 skill test in roster gets a warning - as there is no need
    Given planning period from 1JUN2019 to 30JUN2019

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given a trip with the following activities
      | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 35A    |      |
      | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 35A    |      |

    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K2   | ARN     | ARN     | 6JUN2019 10:00 | 6JUN2019 11:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | Z2   | 02MAY2019 | crew member 2 |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then rave "training.%needs_ast%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_38%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A2%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "training.%needs_ast_for_qual_group_A3A4%" shall be "False" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ast_required_once_per_period_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.no_ast_for_a2a5_fc" shall fail on leg 1 on trip 2 on roster 1




