@PLANNING @ROSTERING @SKCMS-2701 @TRACKING

Feature: A3 pilot on training to A2A5 need 50 BLH or 20 legs as single qual A2 before regaining A5 qualification.

Background: set up for tracking
        Given planning period from 01JAN2020 to 31JAN2020
        Given Tracking

        Given a crew member with
        | attribute       | value     | valid from | valid to |
        | base            | OSL       |            |          |
        | title rank      | FC        |            |          |
        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2018 to 28FEB2035
        Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2018 to 28FEB2035

        Given table crew_training_log additionally contains the following
        |crew         | typ | code | tim       | attr |
        |crew member 1| ILC | A2   | 20DEC2019 |      |

        Given crew member 1 has the following training need
        | part | course           | attribute  | valid from | valid to   | flights | max days | acqual |
        | 1    | CCQ from SH      | ILC        | 01DEC2019  | 02JAN2020  | 1       | 0        | A2     |
    
    Scenario: Insufficient block hours and legs to receive dual qualification

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 02JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0002 | LHR     | OSL     | 02JAN2020 | 12:00 | 13:00 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 2 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "False" on leg 1 on trip 2 on roster 1
    
    Scenario: Sufficient block hours to receive dual qualification
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 2 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "True" on leg 1 on trip 2 on roster 1

    Scenario: Sufficient number of legs to receive dual qualification

        Given a trip with the following activities
        | act | num   | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001  | OSL     | ARL     | 02JAN2020 | 05:00 | 06:00 | SK  | 320    |
        | leg | 0002  | ARL     | OSL     | 02JAN2020 | 06:10 | 07:00 | SK  | 320    |
        | leg | 0003  | OSL     | ARL     | 02JAN2020 | 07:10 | 08:00 | SK  | 320    |
        | leg | 0004  | ARL     | OSL     | 02JAN2020 | 08:10 | 09:00 | SK  | 320    |
        | leg | 0005  | OSL     | ARL     | 02JAN2020 | 09:10 | 10:00 | SK  | 320    |
        | leg | 0006  | ARL     | OSL     | 02JAN2020 | 10:10 | 11:00 | SK  | 320    |
        | leg | 0007  | OSL     | ARL     | 02JAN2020 | 11:10 | 12:00 | SK  | 320    |
        | leg | 0008  | ARL     | OSL     | 02JAN2020 | 12:10 | 13:00 | SK  | 320    |
        | leg | 0009  | OSL     | ARL     | 02JAN2020 | 13:10 | 14:00 | SK  | 320    |
        | leg | 0010  | ARL     | OSL     | 02JAN2020 | 14:10 | 15:00 | SK  | 320    |

        Given a trip with the following activities
        | act | num   | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0011  | OSL     | ARL     | 03JAN2020 | 05:00 | 06:00 | SK  | 320    |
        | leg | 0012  | ARL     | OSL     | 03JAN2020 | 06:10 | 07:00 | SK  | 320    |
        | leg | 0013  | OSL     | ARL     | 03JAN2020 | 07:10 | 08:00 | SK  | 320    |
        | leg | 0014  | ARL     | OSL     | 03JAN2020 | 08:10 | 09:00 | SK  | 320    |
        | leg | 0015  | OSL     | ARL     | 03JAN2020 | 09:10 | 10:00 | SK  | 320    |
        | leg | 0016  | ARL     | OSL     | 03JAN2020 | 10:10 | 11:00 | SK  | 320    |
        | leg | 0017  | OSL     | ARL     | 03JAN2020 | 11:10 | 12:00 | SK  | 320    |
        | leg | 0018  | ARL     | OSL     | 03JAN2020 | 12:10 | 13:00 | SK  | 320    |
        | leg | 0019  | OSL     | ARL     | 03JAN2020 | 13:10 | 14:00 | SK  | 320    |
        | leg | 0020  | ARL     | OSL     | 03JAN2020 | 14:10 | 15:00 | SK  | 320    |
    
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |
    
        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 3 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "True" on leg 1 on trip 3 on roster 1

    Scenario: Sufficient block hours to receive dual qualification from accumulator

        Given table accumulator_rel additionally contains the following
        | name                           | acckey         | tim       | val     |
        | accumulators.block_time_a320   | crew member 1  | 27DEC2019 | 00:00   |
        | accumulators.block_time_a320   | crew member 1  | 30DEC2019 | 50:00   |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |

        Given trip 1 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 1 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "True" on leg 1 on trip 1 on roster 1

    Scenario: Sufficient number of legs to receive dual qualification from accumulator

        Given table accumulator_int additionally contains the following
        | name                                         | acckey         | tim       | val  |
        | accumulators.a2_flights_sectors_daily_acc    | crew member 1  | 25DEC2019 | 0    |
        | accumulators.a2_flights_sectors_daily_acc    | crew member 1  | 30DEC2019 | 20   |


        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |
    
        Given trip 1 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 1 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "True" on leg 1 on trip 1 on roster 1

    Scenario: Sufficient block hours to receive dual qualification but of wrong AC type
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | SFO     | 02JAN2020 | 05:00 | 23:00 | SK  | 35A    |
        | leg | 0002 | SFO     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 35A    |
        | leg | 0003 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 35A    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 2 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "False" on leg 1 on trip 2 on roster 1
    
    Scenario: Sufficient number of legs to receive dual qualification but of wrong AC type

        Given a trip with the following activities
        | act | num   | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001  | OSL     | ARL     | 02JAN2020 | 05:00 | 06:00 | SK  | 35A    |
        | leg | 0002  | ARL     | OSL     | 02JAN2020 | 06:10 | 07:00 | SK  | 35A    |
        | leg | 0003  | OSL     | ARL     | 02JAN2020 | 07:10 | 08:00 | SK  | 35A    |
        | leg | 0004  | ARL     | OSL     | 02JAN2020 | 08:10 | 09:00 | SK  | 35A    |
        | leg | 0005  | OSL     | ARL     | 02JAN2020 | 09:10 | 10:00 | SK  | 35A    |
        | leg | 0006  | ARL     | OSL     | 02JAN2020 | 10:10 | 11:00 | SK  | 35A    |
        | leg | 0007  | OSL     | ARL     | 02JAN2020 | 11:10 | 12:00 | SK  | 35A    |
        | leg | 0008  | ARL     | OSL     | 02JAN2020 | 12:10 | 13:00 | SK  | 35A    |
        | leg | 0009  | OSL     | ARL     | 02JAN2020 | 13:10 | 14:00 | SK  | 35A    |
        | leg | 0010  | ARL     | OSL     | 02JAN2020 | 14:10 | 15:00 | SK  | 35A    |

        Given a trip with the following activities
        | act | num   | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0011  | OSL     | ARL     | 03JAN2020 | 05:00 | 06:00 | SK  | 35A    |
        | leg | 0012  | ARL     | OSL     | 03JAN2020 | 06:10 | 07:00 | SK  | 35A    |
        | leg | 0013  | OSL     | ARL     | 03JAN2020 | 07:10 | 08:00 | SK  | 35A    |
        | leg | 0014  | ARL     | OSL     | 03JAN2020 | 08:10 | 09:00 | SK  | 35A    |
        | leg | 0015  | OSL     | ARL     | 03JAN2020 | 09:10 | 10:00 | SK  | 35A    |
        | leg | 0016  | ARL     | OSL     | 03JAN2020 | 10:10 | 11:00 | SK  | 35A    |
        | leg | 0017  | OSL     | ARL     | 03JAN2020 | 11:10 | 12:00 | SK  | 35A    |
        | leg | 0018  | ARL     | OSL     | 03JAN2020 | 12:10 | 13:00 | SK  | 35A    |
        | leg | 0019  | OSL     | ARL     | 03JAN2020 | 13:10 | 14:00 | SK  | 35A    |
        | leg | 0020  | ARL     | OSL     | 03JAN2020 | 14:10 | 15:00 | SK  | 35A    |
    
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |
    
        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC
        
        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 3 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "False" on leg 1 on trip 3 on roster 1

    Scenario: Rule does not apply to flights where the pilot is flying the training AC

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 02JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0002 | LHR     | OSL     | 02JAN2020 | 12:00 | 13:00 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 320    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "False" on leg 1 on trip 2 on roster 1

    Scenario: Block hours before ILC flight

        Given table accumulator_rel additionally contains the following
        | name                           | acckey         | tim       | val     |
        | accumulators.block_time_a320   | crew member 1  | 07DEC2019 | 00:00   |
        | accumulators.block_time_a320   | crew member 1  | 10DEC2019 | 50:00   |

        # ILC takes place "here" on 25DEC2020

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | PUS     | 03JAN2020 | 05:00 | 23:00 | SK  | 320    |
        | leg | 0002 | PUS     | OSL     | 04JAN2020 | 05:00 | 23:00 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 35A    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 35A    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "rules_caa_ccr.%valid_trng_min_blk_or_legs_before_double_qual%" shall be "True" on leg 1 on trip 2 on roster 1
        Then rave "rules_caa_ccr.%crew_has_sufficient_experience_for_second_LH_qual%" shall be "False" on leg 1 on trip 2 on roster 1
