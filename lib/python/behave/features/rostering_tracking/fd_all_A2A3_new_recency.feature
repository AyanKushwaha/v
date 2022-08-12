@TRACKING @PLANNING @FC @SKCMS-2328

Feature: A2A3 MFF recency rules
    Background: set up
        Given Rostering_FC
        Given planning period from 01MAR2020 to 30APR2020
        Given a crew member with
            | attribute  | value   | valid from  | valid to  |
            | base       | OSL     |             |           |
            | title rank | FC      |             |           |

        Given crew member 1 has qualification "ACQUAL+A2" from 01OCT2019 to 01DEC2020
        Given crew member 1 has qualification "ACQUAL+A3" from 01OCT2019 to 01DEC2020

        # The second crew member is created to take the landings of the two flights
        # in April. Setting nr_landings 0 does not stop the pilot from getting landings.
        # FC gets odd legs and FP gets even legs.

        Given a crew member with
            | attribute  | value   | valid from  | valid to  |
            | base       | OSL     |             |           |
            | title rank | FC      |             |           |

        Given crew member 2 has qualification "ACQUAL+A2" from 01OCT2019 to 01MAY2020
        Given crew member 2 has qualification "ACQUAL+A3" from 01OCT2019 to 01MAY2020

        Given a crew member with
            | attribute  | value   | valid from  | valid to  |
            | base       | OSL     |             |           |
            | title rank | FC      |             |           |

        Given crew member 3 has qualification "ACQUAL+A5" from 01OCT2019 to 01MAY2020
        

        

        Given table agreement_validity additionally contains the following
       | id                       | validfrom | validto   | si |
       | 2_landings_every_45_days | 18APR2020 | 31Dec2035 |    |


    Scenario: A2A3 qualified pilot with correct flights to remain recent
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 15MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0004 | ARN     | OSL     | 15MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL    | 1           | True  |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC




        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 3 on roster 1
        #Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 4 on roster 1

    Scenario: A2A3 qualified pilot with one landing inside validity

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 02MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 02MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 28APR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0004 | ARN     | OSL     | 28APR2020 | 07:55 | 09:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL    | 1           | True  |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 3 on roster 1
    @S00
    Scenario: A2A3 qualified pilot with correct flights to remain recent within validity

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 18APR2020 | 10:25 | 21:45 | SK  |  333   |
    | leg | 0002 | ARN     | OSL     | 19APR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | OSL     | ARN     | 21APR2020 | 10:25 | 21:45 | SK  |  320   |
    | leg | 0004 | ARN     | OSL     | 22APR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 2 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | OSL     | ARN     | 27APR2020 | 10:25 | 21:45 | SK  |  333   |
    | leg | 0006 | ARN     | OSL     | 28APR2020 | 00:35 | 11:15 | SK  |  333   |
    Given trip 3 is assigned to crew member 1

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 18APR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 19APR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 21APR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 22APR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 27APR2020 | "SK 000005 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 28APR2020 | "SK 000006 "  | ARN         | crew member 1    | OSL     | 1           | True  |


    When I show "crew" in window 1
    Then the rule "rules_training_ccr.qln_recency_ok_ALL" shall pass on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_is_recent%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_has_at_least_two_landings_of_leg_qual_for_recency%" shall be "True" on leg 2 on trip 3 on roster 1

    Scenario: A2A3 qualified pilot with only no landing in 45 days within validity

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 01MAR2020 | 10:25 | 21:45 | SK  |  333   |
    | leg | 0002 | ARN     | OSL     | 02MAR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | OSL     | ARN     | 03MAR2020 | 10:25 | 21:45 | SK  |  320   |
    | leg | 0004 | ARN     | OSL     | 04MAR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 2 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | OSL     | ARN     | 27APR2020 | 10:25 | 21:45 | SK  |  333   |
    | leg | 0006 | ARN     | OSL     | 28APR2020 | 00:35 | 11:15 | SK  |  333   |
    Given trip 3 is assigned to crew member 1

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 01MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 02MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 03MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 04MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 27APR2020 | "SK 000005 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 28APR2020 | "SK 000006 "  | ARN         | crew member 1    | OSL     | 1           | True  |


    When I show "crew" in window 1
    
    Then rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_is_recent%" shall be "False" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_has_at_least_two_landings_of_leg_qual_for_recency%" shall be "False" on leg 2 on trip 3 on roster 1

Scenario: A2A3 qualified pilot with only two landings in 90 days within validity


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 19APR2020 | 10:25 | 21:45 | SK  |  320   |
    | leg | 0002 | ARN     | OSL     | 20APR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | OSL     | ARN     | 27APR2020 | 10:25 | 21:45 | SK  |  320   |
    | leg | 0004 | ARN     | OSL     | 28APR2020 | 00:35 | 11:15 | SK  |  320   |
    Given trip 2 is assigned to crew member 1


    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 19APR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 20APR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 27APR2020 | "SK 000005 "  | OSL         | crew member 1    | ARN     | 1           | True  |
    | 28APR2020 | "SK 000006 "  | ARN         | crew member 1    | OSL     | 1           | True  |


    When I show "crew" in window 1
    
    Then rave "recency.%leg_is_recent%" shall be "False" on leg 2 on trip 2 on roster 1
    
    @S01
    Scenario: A5 qualified pilot with correct flights to remain recent
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 35A    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 35A    |
 
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 35A    |
        | leg | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 35A    |
 
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 14MAR2020 | 06:00 | 07:10 | SK  | 35A    |
        | leg | 0004 | ARN     | OSL     | 14MAR2020 | 07:55 | 09:10 | SK  | 35A    |
 
    Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 15MAR2020 | 06:00 | 07:10 | SK  | 35A    |
        | leg | 0004 | ARN     | OSL     | 15MAR2020 | 07:55 | 09:10 | SK  | 35A    |
 
    Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 3    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 3    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 3    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 3    | OSL    | 1           | True  |
        | 14MAR2020 | "SK 000003 "  | OSL         | crew member 3    | ARN    | 1           | True  |
        | 14MAR2020 | "SK 000004 "  | ARN         | crew member 3    | OSL    | 1           | True  |
 
    Given trip 1 is assigned to crew member 3 in position FC
    Given trip 2 is assigned to crew member 3 in position FC
    Given trip 3 is assigned to crew member 3 in position FC
    Given trip 4 is assigned to crew member 3 in position FC

 
    When I show "crew" in window 1
    Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 4 on roster 3




    
    





    

    
