@tracking @planning
Feature: Test max days between simulator and FAM FLT

  Background: set up
    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given table activity_set additionally contains the following
    | id  | grp | si                      | recurrent_typ |
    | C5X | ASF | Additional sim activity |               |

    Given table activity_set_period additionally contains the following
    | id  | validfrom | validto   |
    | C5X | 1JAN1986  | 31DEC2035 |

  @SCENARIO_ASF_1
  Scenario: Check that rule fails when max days between simulator and FAM FLT is exceeded
    Given Tracking

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 31DEC2035 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 11JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 11JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "True"
    and rave "training.%fam_flt_needed_start%" shall be "27APR2019 00:00"
    and rave "training.%fam_flt_needed_end%" shall be "11JUN2019 00:00"
    and rave "training.%fam_flt_needed_ac_qual%" shall be "A5"
    and rave "studio_config.%rudob_fam_flt_needed_text%" shall be "FAM FLT needed latest 10Jun2019 (A5)"


  @SCENARIO_ASF_2
  Scenario: Check that rule passes when max days between simulator and FAM FLT is on max limit
    Given Rostering_FC

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 31DEC2035 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 11JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 11JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 27APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_ASF_3
  Scenario: Check that rule passes when max days between simulator is OK and FAM FLT and ASF in roster
    Given Rostering_FC

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 31DEC2035 

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5X  | OSL     | OSL     | 05JUN2019 | 10:00 | 11:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 10JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 10JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 2 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_ASF_4
  Scenario: Check that rudob parameters are on correct dates
    Given Rostering_FC

    Given planning period from 1JUN2019 to 30JUL2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1JUN2019 to 31DEC2035 

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5X  | OSL     | OSL     | 20JUL2019 | 06:00 | 14:00 |
    
    Given trip 1 is assigned to crew member 1

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 2 has qualification "ACQUAL+A5" from 1JUN2019 to 31DEC2035 

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5X  | OSL     | OSL     | 10JUL2019 | 06:00 | 14:00 |
    
    Given trip 2 is assigned to crew member 2

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 6JUL2019  | 31JUL2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |
      | crew member 2 | 1    | 6JUL2019  | 31JUL2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then rave "training.%fam_flt_needed%" shall be "True"
    and rave "training.%fam_flt_needed_start%" shall be "21JUL2019 00:00" on leg 1 on trip 1 on roster 1
    and rave "training.%fam_flt_needed_end%" shall be "04SEP2019 00:00" on leg 1 on trip 1 on roster 1
    and rave "training.%fam_flt_needed_ac_qual%" shall be "A5" on leg 1 on trip 1 on roster 1
    and rave "studio_config.%rudob_fam_flt_needed_text%" shall be "FAM FLT needed latest 03Sep2019 (A5)" on leg 1 on trip 1 on roster 1
    and rave "training.%fam_flt_needed_start%" shall be "11JUL2019 00:00" on leg 1 on trip 1 on roster 2
    and rave "training.%fam_flt_needed_end%" shall be "25AUG2019 00:00" on leg 1 on trip 1 on roster 2
    and rave "training.%fam_flt_needed_ac_qual%" shall be "A5" on leg 1 on trip 1 on roster 2
    and rave "studio_config.%rudob_fam_flt_needed_text%" shall be "FAM FLT needed latest 24Aug2019 (A5)" on leg 1 on trip 1 on roster 2


  @SCENARIO_ASF_5
  Scenario: Check that fail text is OK for non performed FAM FLT training
    Given Tracking

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 09JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 09JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31MAY2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then rave "rules_qual_ccr.%trng_all_training_flights_performed_all_failtext%" shall be "OMA: Crew on CTR-A3A5 need FAM FLT(A5) 27Apr-10Jun2019"


  @SCENARIO_AST_1
  Scenario: Check that rule fails when max days between simulator plus AST and FAM FLT are both exceeded
    Given Rostering_FC

    Given planning period from 1MAY2019 to 31MAY2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 17MAY2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 17MAY2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 20FEB2019 12:22 |
      | crew member 1 | AST     | K5   | 25APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1FEB2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "True"
    and rave "training.%fam_flt_needed_start%" shall be "21FEB2019 00:00"
    and rave "training.%fam_flt_needed_end%" shall be "17MAY2019 00:00"
    and rave "training.%fam_flt_needed_ac_qual%" shall be "A5"


  @SCENARIO_AST_2
  Scenario: Check that rule passes when max days between simulator and FAM FLT is exceeded but ok between AST and FAM FLT
    Given Rostering_FC

    Given planning period from 1MAY2019 to 31MAY2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 17MAY2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 17MAY2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 20FEB2019 12:22 |
      | crew member 1 | AST     | K5   | 26APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1FEB2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_AST_3
  Scenario: Check that rule fails when max days are ok between AST and FAM FLT but there is no previous simulator
    Given Rostering_FC

    Given planning period from 1MAY2019 to 31MAY2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 17MAY2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 17MAY2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | AST     | K5   | 26APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1FEB2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_AST_4
  Scenario: Check that rule passes when max days between simulator and FAM FLT is exceeded but ok for AST with AST in roster
    Given Rostering_FC

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given table crew_training_log additionally contains the following
    | crew          | typ     | code | tim             |
    | crew member 1 | ASF     | C5X  | 10APR2019 12:22 |

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | K5   | OSL     | OSL     | 05JUN2019 | 10:00 | 11:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 10JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 10JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 2 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_EXTRA_ASF_1
  Scenario: Check that rule fails when max days between simulator plus extra simulator and FAM FLT are both exceeded
    Given Rostering_FC

    Given planning period from 1MAY2019 to 31MAY2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 17MAY2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 17MAY2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 20FEB2019 12:22 |
      | crew member 1 | ASF     | C5X  | 25APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1FEB2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "True"
    and rave "training.%fam_flt_needed_start%" shall be "21FEB2019 00:00"
    and rave "training.%fam_flt_needed_end%" shall be "17MAY2019 00:00"
    and rave "training.%fam_flt_needed_ac_qual%" shall be "A5"


  @SCENARIO_EXTRA_ASF_2
  Scenario: Check that rule passes when max days between initial simulator and FAM FLT is exceeded but ok between extra ASF and FAM FLT
    Given Rostering_FC

    Given planning period from 1MAY2019 to 31MAY2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 17MAY2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 17MAY2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 20FEB2019 12:22 |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1FEB2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 1 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"


  @SCENARIO_EXTRA_ASF_3
  Scenario: Check that rule passes when max days between initial simulator and FAM FLT is exceeded but ok for extra simulator with extra simulator in roster
    Given Rostering_FC

    Given planning period from 1JUN2019 to 30JUN2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035

    Given table crew_training_log additionally contains the following
    | crew          | typ     | code | tim             |
    | crew member 1 | ASF     | C5X  | 10APR2019 12:22 |

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5X  | OSL     | OSL     | 05JUN2019 | 10:00 | 11:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 10JUN2019 | 10:00 | 11:00 | SK  | 35X    |
    | leg | 0002 | LHR     | OSL     | 10JUN2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     |            |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 2 on roster 1
    and rave "training.%fam_flt_needed%" shall be "False"
