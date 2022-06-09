@FC @ALL @JCRT @TRACKING @ROSTERING @A2LR
Feature: Crew need to perform ETOPS LIFUS LC sectors within 60 days of LRP2 course

##############################################################################
  Background: Setup common data
    
    Given a crew member with
    | attribute  | value |
    | crew rank  | FC    |
    | title rank | FC    |
    | region     | SKS   |
    | base       | STO   |

##############################################################################

    @SCENARIO1
    Scenario: Days passed since LRP2 training is less than max so rule shall pass
      Given planning period from 1MAR2020 to 1APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ            | code | tim             |
      | crew member 1 | COURSE         | LRP2 | 3FEB2020 08:00  |
      | crew member 1 | ETOPS LIFUS/LC | A2   | 4FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32Q    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32Q    |

      Given trip 1 is assigned to crew member 1
      Given trip 2 is assigned to crew member 1

      When I show "crew" in window 1
      and I load rule set "Tracking"

     Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 2 on roster 1

##############################################################################

    @SCENARIO2
    Scenario: Days passed since LRP2 training is more than max but LRSB is planned so rule shall pass
      Given planning period from 1MAR2020 to 1APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ            | code | tim             |
      | crew member 1 | COURSE         | LRP2 | 1DEC2019 08:00  |
      | crew member 1 | COURSE         | LRSB | 3FEB2020 08:00  |
      | crew member 1 | ETOPS LIFUS/LC | A2   | 4FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32Q    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32Q    |


      Given trip 1 is assigned to crew member 1
      Given trip 2 is assigned to crew member 1
      #Given crew member 1 has a personal activity "LRSB" at station "ARN" that starts at 3FEB2020 10:00 and ends at 3FEB2020 15:00

      When I show "crew" in window 1
      and I load rule set "Tracking"

      Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 2 on roster 1

##############################################################################

    @SCENARIO3
    Scenario: Crew member flying below rank should get qualification
      Given planning period from 1MAR2020 to 1APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ            | code | tim             |
      | crew member 1 | COURSE         | LRP2 | 1FEB2020 08:00  |
      | crew member 1 | ETOPS LIFUS/LC | A2   | 2FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32Q    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32Q    |

      Given trip 1 is assigned to crew member 1 in position FP
      Given trip 2 is assigned to crew member 1 in position FP

      When I show "crew" in window 1
      and I load rule set "Tracking"

      Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 2 on roster 1

##############################################################################

    @SCENARIO4
    Scenario: Days passed since LRP2 training is more than max so rule shall fail, no ETOPS LIFUS LC training in training log
      Given planning period from 1APR2020 to 30APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ            | code | tim             |
      | crew member 1 | COURSE         | LRP2 | 1FEB2020 08:00  |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5APR2020 02:10 | 5APR2020 13:45 | 32Q    |
      | leg | SK  | 0002 | EWR     | ARN     | 7APR2020 09:10 | 7APR2020 20:45 | 32Q    |

      Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ETOPS LIFUS/LC"
     
      When I show "crew" in window 1
      and I load rule set "Tracking"

     Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall fail on leg 1 on trip 1 on roster 1

##############################################################################

    @SCENARIO5
    Scenario: Days passed since LRP2 training is less than max (before planning period) so rule shall pass
      Given planning period from 1MAR2020 to 1APR2020
      Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2020
      Given crew member 1 has qualification "POSITION+A2LR" from 01JAN2019 to 31DEC2020

      Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | COURSE  | LRP2 | 1JAN2020 08:00  |

      Given table accumulator_int additionally contains the following
      | name                                       | acckey         | tim       | val |
      | accumulators.a2lh_flights_acc              | crew member 1  | 2JAN2020  | 0   |
      | accumulators.a2lh_flights_acc              | crew member 1  | 12JAN2020 | 1   |
      | accumulators.a2lh_flights_acc              | crew member 1  | 1MAR2020  | 1   |

      Given a trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | EWR     | 5MAR2020 02:10 | 5MAR2020 13:45 | 32Q    |

      Given another trip with the following activities
      | act | car | num  | dep stn | arr stn | dep            | arr            | ac_typ |
      | leg | SK  | 0001 | ARN     | GOT     | 6MAR2020 08:00 | 6MAR2020 09:00 | 32Q    |

      Given trip 1 is assigned to crew member 1
      Given trip 2 is assigned to crew member 1

      When I show "crew" in window 1
      and I load rule set "Tracking"

      Then the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 1 on roster 1
      and the rule "rules_training_ccr.trng_max_days_between_lrp2_and_first_lh_a2nx_flight_FC" shall pass on leg 1 on trip 2 on roster 1

##############################################################################