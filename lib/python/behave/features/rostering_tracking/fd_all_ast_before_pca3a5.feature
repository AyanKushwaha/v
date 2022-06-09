@tracking @planning @A350 @AST @PC @PCA3A5 @A5
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


  @SCENARIO1
  Scenario: Check that A5 crew with PC in roster after AST in training log within grace period is legal
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PCA3A5" from 8FEB2019 to 1JUN2020

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K5   | 28APR2020 | crew member 2 |

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | S5   | ARN     | ARN     | 5MAY2020 10:00 | 5MAY2020 13:00 |

    Given trip 1 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_indust_ccr.ind_training_a5_crew_need_ast_in_pca3a5_grace_period" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO2
  Scenario: Check that A5 crew with PC in roster after AST in training log before grace period is illegal
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PCA3A5" from 8FEB2019 to 1JUN2020

    Given table crew_training_log additionally contains the following
      | crew          | typ | code | tim       | attr          |
      | crew member 1 | AST | K5   | 28FEB2020 | crew member 2 |

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | S5   | ARN     | ARN     | 5MAY2020 10:00 | 5MAY2020 13:00 |

    Given trip 1 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_indust_ccr.ind_training_a5_crew_need_ast_in_pca3a5_grace_period" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO3
  Scenario: Check that A5 crew with PC in roster after AST in roster within grace period is legal
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PCA3A5" from 8FEB2019 to 1JUN2020

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K5   | ARN     | ARN     | 2MAY2020 10:00 | 2MAY2020 11:00 |

    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | S5   | ARN     | ARN     | 5MAY2020 10:00 | 5MAY2020 13:00 |

    Given trip 2 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_indust_ccr.ind_training_a5_crew_need_ast_in_pca3a5_grace_period" shall pass on leg 1 on trip 2 on roster 1


  @SCENARIO4
  Scenario: Check that A5 crew with PC in roster before AST in roster within grace period is illegal
    Given planning period from 1MAY2020 to 31MAY2020
    
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035

    Given crew member 1 has document "REC+PCA3A5" from 8FEB2019 to 1JUN2020

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | S5   | ARN     | ARN     | 2MAY2020 10:00 | 2MAY2020 13:00 |

    Given trip 1 is assigned to crew member 1 in position FC with
      | type      | leg | name     | value      |
      | attribute | 1   | TRAINING | SKILL TEST |

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | dep            | arr            |
      | ground | K5   | ARN     | ARN     | 5MAY2020 10:00 | 5MAY2020 11:00 |

    Given trip 2 is assigned to crew member 1

    When I show "crew" in window 1
    and I load rule set "Tracking"

    Then the rule "rules_indust_ccr.ind_training_a5_crew_need_ast_in_pca3a5_grace_period" shall fail on leg 1 on trip 1 on roster 1
