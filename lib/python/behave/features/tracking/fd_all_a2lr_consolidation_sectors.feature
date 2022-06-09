@tracking @planning @LRP2 @MIN_SECTORS @A2LR
Feature: Test min number of sectors after LRP2

  Background: Set up A2LR qualified FP

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | OSL       |            |          |
      | title rank      | FP        |            |          |
    Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2020 to 31DEC2035 
    Given crew member 1 has qualification "POSITION+A2LR" from 1FEB2020 to 31DEC2035 


  @SCENARIO1
  Scenario: Check that rule passes when crew has 8 A2LH sectors within 180 days of LRP2

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 11AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 12AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 13AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 14AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 15AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 16AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 17AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 18AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    # This is the first "normal" A2LH trip, more than 180 days after LRP2
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 21AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 22AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-5  | 1-2 | pass  |

  @SCENARIO2
  Scenario: Check that rule fails when crew has 6 active A2LH sectors within 180 days of LRP2 and no LRSB

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ    | code | tim             |
      | crew member 1 | COURSE | LRP2 | 22FEB2020 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 11AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 12AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 13AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 14AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 15AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 16AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    # This is the first "normal" A2LH trip, more than 180 days after LRP2
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 21AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 22AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-3  | 1-2 | pass  |
      | 1      | 4    | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_etops_training_failtext%(7, 8)" values shall be
      | roster | trip | leg | value                                                                                        |
      | 1      | 4    | 1-2 | OMA: Min A2 LH sectors within 180 days after LRP2 needs LRSB followed by last sectors: 7[8] |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-4  | 1-2 | pass  |

  @SCENARIO3
  Scenario: Check that rule fails when crew has 6 A2LH sectors within 180 days after LRP2 followed by LRSB and then 1 extra sectors directly after

    Given Tracking

    Given planning period from 1AUG2020 to 31OCT2020

    Given table crew_training_log additionally contains the following
      | crew          | typ    | code | tim             |
      | crew member 1 | COURSE | LRP2 | 22FEB2020 12:22 |
      | crew member 1 | COURSE | LRSB | 18AUG2020 11:00 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 11AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 12AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 13AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 14AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 15AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 16AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 3 is assigned to crew member 1 in position FP


    # This is the first "normal" A2LH trip, more than 180 days after LRP2
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 17SEP2020 | 10:00 | 11:00 | SK  | 32Q    |


    Given trip 4 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip | leg | value |
      | 1      | 4    | 1 | fail  |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 4    | 1 | pass  |

  @SCENARIO4
  Scenario: Check that rule passes when crew has 6 A2LH sectors within 180 days after LRP2 followed by LRSB and then 1 extra sectors directly after

    Given Tracking

    Given planning period from 1AUG2020 to 31OCT2020

    Given table crew_training_log additionally contains the following
      | crew          | typ    | code | tim             |
      | crew member 1 | COURSE | LRP2 | 22FEB2020 12:22 |
      | crew member 1 | COURSE | LRSB | 18AUG2020 11:00 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 11AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 12AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 13AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 14AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 15AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 16AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 3 is assigned to crew member 1 in position FP

    # This is the first "normal" A2LH trip, more than 180 days after LRP2
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 17SEP2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 18SEP2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |


  @SCENARIO6
  Scenario: Check that the LRSB followed by consolidation sector rule fails when there is an activity in between

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00
    Given crew member 1 has a personal activity "R" at station "OSL" that starts at 21AUG2020 22:00 and ends at 24AUG2020 22:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32J    |
      | leg | 0002 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32J    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | fail  |
      | 1      | 2    | 1   | pass  |
      | 1      | 3    | 2   | pass  |

    and rave "rules_training_ccr.%trng_lrsb_followed_by_active_sectors_failtext%(2, 0)" values shall be
      | roster | trip | leg | value                                      |
      | 1      | 1    | 1   | OMA: LRSB followed by active sectors: 2[0] |


  @SCENARIO7
  Scenario: Check that the LRSB followed by consolidation sector rule passes when there is no activity in between

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | pass  |
      | 1      | 2    | 1-2 | pass  |

  @SCENARIO8
  Scenario: Check that the LRSB followed by consolidation sector rule fails when there is only one active A2LH leg after

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | dh  | 0002 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | fail  |
      | 1      | 2    | 2   | pass  |
    and rave "rules_training_ccr.%trng_lrsb_followed_by_active_sectors_failtext%(2, 1)" values shall be
      | roster | trip | leg | value                                      |
      | 1      | 1    | 1   | OMA: LRSB followed by active sectors: 2[1] |


  @SCENARIO9
  Scenario: Check that rule fails when crew has 4 A2LH sectors within 180 days of LRP2

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 12AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 13AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 14AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 15AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    # This is the first "normal" A2 LH trip, more than 180 days after LRP2
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 21AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 22AUG2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-2  | 1-2 | pass  |
      | 1      | 3    | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_etops_training_failtext%(9, 10)" values shall be
      | roster | trip | leg | value                                                                                                                              |
      | 1      | 3    | 1-2 | OMA: Min A2 LH sectors within 180 days after LRP2 training needs LR REFRESH flight followed by last sectors within 30 days: 9[10] |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1-3  | 1-2 | pass  |


  @SCENARIO10
  Scenario: Check that rule fails when crew has 5 A2 LH sectors within 180 days after LRP2 followed by 2 LR REFRESH sectors

    Given Tracking

    Given planning period from 1OCT2020 to 31OCT2020

    Given table crew_training_log additionally contains the following
      | crew          | typ        | code | tim             |
      | crew member 1 | COURSE     | LRP2 | 22FEB2020 12:22 |
      | crew member 1 | LR REFRESH | A2   | 18SEP2020 12:22 |
      | crew member 1 | LR REFRESH | A2   | 19SEP2020 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a2lh_flights_acc              | crew member 1  | 15AUG2020 | 5   |


    # This is the first "normal" A2 LH trip, more than 30 days after LR REFRESH
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 19OCT2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 20OCT2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | fail  |

    and rave "rules_training_ccr.%trng_min_active_sectors_after_etops_training_failtext%(9, 10)" values shall be
      | roster | trip | leg | value                                                                                        |
      | 1      | 1    | 1-2 | OMA: Min A2 LH sectors within 180 days after LRP2 training needs LR REFRESH flight followed by last sectors within 30 days: 9[10] |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |


  @SCENARIO11
  Scenario: Check that rule passes when crew has 5 A2 LH sectors within 180 days after LRP2 followed by 2 LR REFRESH sectors and another A2LH sector within 30 days

    Given Tracking

    Given planning period from 1OCT2020 to 31OCT2020

    Given table crew_training_log additionally contains the following
      | crew          | typ        | code | tim             |
      | crew member 1 | COURSE     | LRP2 | 22FEB2020 12:22 |
      | crew member 1 | LR REFRESH | A2   | 18SEP2020 12:22 |
      | crew member 1 | LR REFRESH | A2   | 19SEP2020 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                       | acckey         | tim       | val |
    | accumulators.a2lh_flights_acc              | crew member 1  | 16SEP2020 | 5   |

    # This is the first "normal" A2LH trip, more than 30 days after LR REFRESH
    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 10OCT2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 11OCT2020 | 12:00 | 13:00 | SK  | 32Q    |
    
    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_min_active_sectors_after_etops_training" legality shall be
      | roster | trip  | leg | value |
      | 1      | 1     | 1-2 | pass  |

    and the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |


  @SCENARIO12
  Scenario: Check that the LRSB followed by consolidation sector rule fails when there is a deadhead flight directly after LRSB and then only one A2LH sector

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 003  | STO     | OSL     | 25Aug2020 | 08:00 | 09:00 | SK  | 32Q    |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | fail  |
      | 1      | 2    | 1-2 | pass  |

    and rave "rules_training_ccr.%trng_lrsb_followed_by_active_sectors_failtext%(2, 1)" values shall be
      | roster | trip | leg | value                                      |
      | 1      | 1    | 1   | OMA: LRSB followed by active sectors: 2[1] |


  @SCENARIO13
  Scenario: Check that the LRSB followed by consolidation sector rule fails when there is a deadhead followed by a trip before A2LH sectors

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |


    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00

    Given a trip with the following activities
      | act | num | dep stn | arr stn | date       | dep   | arr   | car | ac_typ |
      | dh  | 001 | OSL     | STO     | 24AUG2020  | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 002 | STO     | OSL     | 24AUG2020  | 13:00 | 14:00 | SK  | 32Q    |
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 2 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | fail  |
      | 1      | 2    | 1-2 | pass  |
      | 1      | 3    | 1-2 | pass  |

    and rave "rules_training_ccr.%trng_lrsb_followed_by_active_sectors_failtext%(2, 1)" values shall be
      | roster | trip | leg | value                                      |
      | 1      | 1    | 1   | OMA: LRSB followed by active sectors: 2[1] |


  @SCENARIO14
  Scenario: Check that the LRSB followed by consolidation sector rule passes when there is a deadhead flight directly after LRSB and then two consecutive A2LH sectors

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |

    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | dh  | 003  | STO     | OSL     | 25Aug2020 | 08:00 | 09:00 | SK  | 32Q    |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0001 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | pass  |
      | 1      | 2    | 1-3 | pass  |


  @SCENARIO15
  Scenario: Check that the LRSB followed by consolidation sector rule passes when there is an activity in between but crew is off-duty

    Given Tracking

    Given planning period from 1AUG2020 to 31AUG2020

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 22FEB2020 12:22 |


    Given crew member 1 has a personal activity "LRSB" at station "OSL" that starts at 21AUG2020 10:00 and ends at 21AUG2020 11:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 21AUG2020 22:00 and ends at 24AUG2020 22:00

    Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | JFK     | 25AUG2020 | 10:00 | 11:00 | SK  | 32Q    |
      | leg | 0002 | JFK     | OSL     | 25AUG2020 | 12:00 | 13:00 | SK  | 32Q    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.trng_lrsb_followed_by_active_sectors" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1   | pass  |
      | 1      | 2    | 1   | pass  |
      | 1      | 3    | 1-2 | pass  |




