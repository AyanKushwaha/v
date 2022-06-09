@tracking @planning @FAM_FLT @MIN_SECTORS @A5 @A350
Feature: Test min number of sectors after FAM FLT

  Background: Set up A5 qualified FP with FAM FLT and 3 A5 trips (6 sectors)

    Given table agreement_validity additionally contains the following
      | id                                  | validfrom | validto   |
      | A5_sectors_btw_ctr_con_flt        | 1JAN2019  | 31DEC2035 |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35A     | SK  | A5         | AL         |

    Given table activity_set additionally contains the following
      | id  | grp | si                      | recurrent_typ |
      | C5X | ASF | Additional sim activity |               |

    Given table activity_set_period additionally contains the following
      | id  | validfrom | validto   |
      | C5X | 1JAN1986  | 31DEC2035 |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | region          | SKN       | 28SEP2011  | 09DEC2022 |
      | base            | OSL       |            |          |
      | title rank      | FP        |            |          |
      | contract        | V131-LH     | 28SEP2011  | 08JAN2022 |
    Given crew member 1 has qualification "ACQUAL+A5" from 1APR2019 to 31DEC2035 
    Given crew member 1 has qualification "ACQUAL+A3" from 1APR2019 to 31DEC2035 

    Given table crew_training_need additionally contains the following
      | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
      | crew member 1 | 1    | 5Sep2019  | 15SEP2019 | CTR-A3A5 | FAM FLT   | 2       | 0       | A5     | 15SEP2019  |
    
    Given Tracking

    Given planning period from 1OCT2019 to 31OCT2019
 
@SCENARIO01
  Scenario: Check that rule passes when crew has completed 4 consecutive A5 sectors after CTR course including FAM FLT



    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 20SEP2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 21SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                                     | acckey         | tim       | val |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 25SEP2019 | 0   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 25SEP2019 | 0   |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 28SEP2019 | 2   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 28SEP2019 | 2   |


     Given table accumulator_time additionally contains the following
    | name                                        | acckey         | tim       | 
    | accumulators.last_flown_a350                | crew member 1  | 25SEP2019 10:00 | 
    | accumulators.last_flown_a350                | crew member 1  | 27SEP2019 10:00 | 

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 01OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 03OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 03OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 08OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 08OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 12OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "01OCT2019 13:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    | 1-2 | pass  |

  @SCENARIO02
  Scenario: Check that rule fails when crew has not flown 4 consecutive A5 sectors after CTR course including FAM FLT

    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 20SEP2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 21SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                                     | acckey         | tim       | val |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 25SEP2019 | 0   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 25SEP2019 | 0   |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 28SEP2019 | 1   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 28SEP2019 | 1   |


     Given table accumulator_time additionally contains the following
    | name                                        | acckey         | tim       | 
    | accumulators.last_flown_a350                | crew member 1  | 25SEP2019 10:00 | 

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 01OCT2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 02OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 02OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 2 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 03OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 03OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 08OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 08OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 12OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 5 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "03OCT2019 11:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    |   1 | fail  |

    
    @SCENARIO03
  Scenario: Check that rule passes when crew has only flown less than 4 A5 consolidation sectors after CTR course including FAM FLT and have not flown any other aircraft type

    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 20SEP2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 21SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                                     | acckey         | tim       | val |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 25SEP2019 | 0   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 25SEP2019 | 0   |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 28SEP2019 | 1   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 28SEP2019 | 1   |


     Given table accumulator_time additionally contains the following
    | name                                        | acckey         | tim       | 
    | accumulators.last_flown_a350                | crew member 1  | 25SEP2019 10:00 | 

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 01OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 1 is assigned to crew member 1 in position FP
   
    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "01OCT2019 13:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      |  1   | 1-2 | pass  |

  @SCENARIO04
  Scenario: Check that rule fails when crew has only flown less than 4 A5 consolidation sectors after CTR course including FAM FLT and have also flown any other aircraft type

    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 20SEP2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 21SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                                     | acckey         | tim       | val |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 25SEP2019 | 0   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 25SEP2019 | 0   |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 28SEP2019 | 1   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 28SEP2019 | 1   |


     Given table accumulator_time additionally contains the following
    | name                                        | acckey         | tim       | 
    | accumulators.last_flown_a350                | crew member 1  | 25SEP2019 10:00 |  

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 01OCT2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 03OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 04OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 2 is assigned to crew member 1 in position FP
   
    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "04OCT2019 13:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      |  1   | 1-2 | fail  |

   @SCENARIO05
  Scenario: Check that rule fails when crew has flown a non A5 sectors after CTR course and before FAM FLT

    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 03OCT2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 04OCT2019 12:22 |

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 02OCT2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FP

      Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 03OCT2019 | 10:22 | 11:22 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 04OCT2019 | 12:22 | 13:22 | SK  | 35A    |

    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

      Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 06OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 06OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 3 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 07OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 07OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 4 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 08OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 08OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 5 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 12OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 6 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 17OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 17OCT2019 | 12:00 | 13:00 | SK  | 35A    |
    
    Given trip 7 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "07OCT2019 13:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 1    |   2 | fail  |
  
    @SCENARIO06
  Scenario: Check that rule fails when crew has flown 3 consecutive A5 consolidation sectors after CTR course and 4th sector is A3

        Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 20SEP2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 21SEP2019 12:22 |

    Given table accumulator_int additionally contains the following
    | name                                                     | acckey         | tim       | val |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 25SEP2019 | 0   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 25SEP2019 | 0   |
    | accumulators.a5_flights_sectors_daily_acc                | crew member 1  | 28SEP2019 | 1   |
    | accumulators.all_flights_sectors_daily_acc               | crew member 1  | 28SEP2019 | 1   |


     Given table accumulator_time additionally contains the following
    | name                                        | acckey         | tim       | 
    | accumulators.last_flown_a350                | crew member 1  | 25SEP2019 10:00 | 

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 01OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 02OCT2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 02OCT2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 2 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "training.%date_of_four_or_less_consolidation_sector%" shall be "01OCT2019 13:00" on leg 1 on trip 1 on roster 1 
    and the rule "rules_training_ccr.trng_only_A5_sectors_allowed_btw_fam_and_con_flt" legality shall be
      | roster | trip | leg | value |
      | 1      | 2    | 1 | fail  |

    @SCENARIO07
  Scenario: Check that rule is not valid on leg performed before CTR training

    Given planning period from 1SEP2019 to 31OCT2019

    Given table crew_training_log additionally contains the following
      | crew          | typ      | code | tim             |
      | crew member 1 | FAM FLT  | A5   | 03OCT2019 10:22 |
      | crew member 1 | FAM FLT  | A5   | 04OCT2019 12:22 |
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01SEP2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 02SEP2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 1 is assigned to crew member 1 in position FP

     Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 01OCT2019 | 10:00 | 11:00 | SK  | 33A    |
    | leg | 0002 | AMS     | OSL     | 02OCT2019 | 12:00 | 13:00 | SK  | 33A    |

    Given trip 2 is assigned to crew member 1 in position FP

      Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 03OCT2019 | 10:22 | 11:22 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 04OCT2019 | 12:22 | 13:22 | SK  | 35A    |

    Given trip 3 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

      Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 06OCT2019 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | AMS     | OSL     | 06OCT2019 | 12:00 | 13:00 | SK  | 35A    |

    Given trip 4 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "training.%is_less_than_fourth_consolidation_sector%" shall be "False" on leg 1 on trip 1 on roster 1 
    and rave "rules_training_ccr.%valid_trng_only_A5_sectors_allowed_btw_fam_and_con_flt%" shall be "False" on leg 1 on trip 1 on roster 1