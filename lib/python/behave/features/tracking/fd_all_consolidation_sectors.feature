@tracking @planning @FAM_FLT @MIN_SECTORS @A5 @A350
Feature: Test min number of sectors after FAM FLT

  Background: Set up A5 qualified FP with FAM FLT and 3 A5 trips (6 sectors)

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given table activity_set additionally contains the following
      | id  | grp | si                      | recurrent_typ |
      | C5X | ASF | Additional sim activity |               |

    Given table activity_set_period additionally contains the following
      | id  | validfrom | validto   |
      | C5X | 1JAN1986  | 31DEC2035 |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | OSL       |            |          |
      | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035 

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 1APR2019  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     | 30APR2019  |


  @SCENARIO1
  Scenario: Check that rule passes when crew has 10 A5 sectors within 90 days of FAM FLT

    Given Tracking

    Given planning period from 1AUG2019 to 31AUG2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 12AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 12AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 13AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 13AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 14AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 14AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 15AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 15AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 16AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 16AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    # This is the first "normal" A5 trip, more than 90 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 18AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 18AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-6  | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-6  | 1-2 | pass  |

  @SCENARIO2
  Scenario: Check that rule fails when crew has 9 active A5 sectors within 90 days of FAM FLT

    Given Tracking

    Given planning period from 1AUG2019 to 31AUG2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 12AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 12AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 13AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 13AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 14AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 14AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 15AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 15AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 16AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | dh  | 0002 | AMS     | OSL     | 16AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    # This is the first "normal" A5 trip, more than 90 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 18AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 18AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |
      | 1      | 6    | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value                                                                           |
      | 1      | 6    | 1-2 | OMA: Min A5 sectors within 90 days after FAM flight needs FMST 17Aug2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-6  | 1-2 | pass  |

  @SCENARIO3
  Scenario: Check that rule passes when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then 2 extra sectors within 120 days after FAM FLT

    Given Tracking

    Given planning period from 1SEP2019 to 30SEP2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 10  |

    # This is the first "normal" A5 trip, more than 120 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17SEP2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17SEP2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO4
  Scenario: Check that rule fails when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then 1 extra sector within 120 days after FAM FLT

    Given Tracking

    Given planning period from 1SEP2019 to 30SEP2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 9   |

    # This is the first "normal" A5 trip, more than 120 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17SEP2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17SEP2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | FMST and remaining A5 sectors within 120 days after FAM flight 16Sep2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO5
  Scenario: Check that rule passes when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then 1 extra sector within 120 days after FAM FLT followed by ASF and then 1 extra sector within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |
      | crew member 1 | ASF     | C5X  | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 9   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 10  |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO6
  Scenario: Check that rule passes when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then 1 extra sector within 120 days after FAM FLT followed by PC and then 1 extra sector within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |
      | crew member 1 | PC      | Y5   | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 9   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 10  |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO7
  Scenario: (SKCMS-2395) Check that rule passes when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then 1 extra sector within 120 days after FAM FLT followed by AST and then 1 extra sector within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |
      | crew member 1 | AST     | K5   | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 9   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 10  |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO8
  Scenario: Check that rule fails when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then no extra sector within 120 days after FAM FLT followed by AST and then 1 extra sector within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |
      | crew member 1 | AST     | K5   | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 9   |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | ASF, AST or PC/OPC and remaining A5 sectors within 150 days after FAM flight 16Oct2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO9
  Scenario: Check that rule fails when crew has 8 A5 sectors within 90 days after FAM FLT followed by FMST and then no extra sector within 120 days after FAM FLT followed by ASF and then 1 extra sector within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | FMST    | FMST | 21AUG2019 11:00 |
      | crew member 1 | ASF     | C5X  | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 8   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 9   |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | ASF, AST or PC/OPC and remaining A5 sectors within 150 days after FAM flight 16Oct2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO10
  Scenario: Check that the FMST to consolidation distance rule fails when distance is long

    Given Tracking

    Given planning period from 1AUG2019 to 31AUG2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 12AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 12AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 13AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 13AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 14AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 14AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 15AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 15AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 16AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | dh  | 0002 | AMS     | OSL     | 16AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    Given crew member 1 has a personal activity "FMST" at station "OSL" that starts at 21AUG2019 10:00 and ends at 21AUG2019 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 25AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 25AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |
      | 1      | 6    | 1   | pass  |
      | 1      | 7    | 1   | fail  |
      | 1      | 7    | 2   | pass  |

# FIXME: Needs to patch behave/gherkin to handle abstime parameters
#    and rave "rules_training_ccr.%trng_max_days_between_fmst_and_cons_flt_failtext%(24AUG1029, 25AUG 12:00)" values shall be
#      | roster | trip | leg | value |
#      | 1      | 7    | 1   | OMA: Distance too large between FMST and next consolidation flight 24Aug 00:00[25Aug 12:00] |


  @SCENARIO11
  Scenario: Check that the FMST to consolidation distance rule fails when distance three days

    Given Tracking

    Given planning period from 1AUG2019 to 31AUG2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 12AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 12AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 13AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 13AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 14AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 14AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 15AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 15AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 16AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | dh  | 0002 | AMS     | OSL     | 16AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    Given crew member 1 has a personal activity "FMST" at station "OSL" that starts at 21AUG2019 10:00 and ends at 21AUG2019 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 24AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 24AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |
      | 1      | 6    | 1   | pass  |
      | 1      | 7    | 1-2 | pass  |


  @SCENARIO12
  Scenario: Check that rule fails when crew has 7 A5 sectors within 90 days of FAM FLT

    Given Tracking

    Given planning period from 1AUG2019 to 31AUG2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 12AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 12AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 13AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 13AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 14AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 14AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 15AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | dh  | 0002 | AMS     | OSL     | 15AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    # This is the first "normal" A5 trip, more than 90 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 18AUG2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 18AUG2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-4  | 1-2 | pass  |
      | 1      | 5    | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 5    | 1-2 | OMA: Min A5 sectors within 90 days after FAM flight needs ASF, PC or OPC 17Aug2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |


  @SCENARIO13
  Scenario: Check that rule fails when crew has 7 A5 sectors within 90 days after FAM FLT followed by ASF and then 2 extra sectors within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | ASF     | C5X  | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 9   |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | ASF, AST or PC/OPC and remaining A5 sectors within 150 days after FAM flight 16Oct2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO14
  Scenario: (SKCMS-2395) Check that rule fails when crew has 7 A5 sectors within 90 days after FAM FLT followed by AST and then 2 extra sectors within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | AST     | K5   | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | AST     | K5  | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 9   |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_ctr_flight_failtext%(9, 10)" values shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | ASF, AST or PC/OPC and remaining A5 sectors within 150 days after FAM flight 16Oct2019: 9[10] |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO15
  Scenario: Check that rule passes when crew has 7 A5 sectors within 90 days after FAM FLT followed by ASF and then 3 extra sectors within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | ASF     | C5X  | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | ASF     | C5X  | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 10  |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO16
  Scenario: Check that rule passes when crew has 7 A5 sectors within 90 days after FAM FLT followed by ASF and then 3 extra sectors within 150 days

    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | AST     | K5   | 26APR2019 12:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 10:22 |
      | crew member 1 | FAM FLT | A5   | 19MAY2019 12:22 |
      | crew member 1 | AST     | K5   | 18SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a5_flights_acc                | crew member 1  | 12AUG2019 | 0   |
    | accumulators.a5_flights_acc                | crew member 1  | 13AUG2019 | 2   |
    | accumulators.a5_flights_acc                | crew member 1  | 14AUG2019 | 4   |
    | accumulators.a5_flights_acc                | crew member 1  | 15AUG2019 | 6   |
    | accumulators.a5_flights_acc                | crew member 1  | 16AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 22AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 23AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 24AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 25AUG2019 | 7   |
    | accumulators.a5_flights_acc                | crew member 1  | 18SEP2019 | 10  |

    # This is the first "normal" A5 trip, more than 150 days after FAM FLT
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35X    |
      | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35X    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_ctr_flight" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_max_days_between_fmst_and_cons_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |
