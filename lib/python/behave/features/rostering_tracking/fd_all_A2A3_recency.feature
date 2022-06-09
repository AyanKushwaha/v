@TRACKING @PLANNING @FC @SKCMS-2328

Feature: A2A3 MFF recency rules
    Background: set up
        Given Rostering_FC
        Given planning period from 01MAR2020 to 30APR2020
        Given a crew member with
            | attribute  | value   | valid from  | valid to  |
            | base       | OSL     |             |           |
            | title rank | FC      |             |           |

        Given crew member 1 has qualification "ACQUAL+A2" from 01OCT2019 to 01MAY2020
        Given crew member 1 has qualification "ACQUAL+A3" from 01OCT2019 to 01MAY2020

        # The second crew member is created to take the landings of the two flights
        # in April. Setting nr_landings 0 does not stop the pilot from getting landings.
        # FC gets odd legs and FP gets even legs.

        Given a crew member with
            | attribute  | value   | valid from  | valid to  |
            | base       | OSL     |             |           |
            | title rank | FC      |             |           |

        Given crew member 2 has qualification "ACQUAL+A2" from 01OCT2019 to 01MAY2020
        Given crew member 2 has qualification "ACQUAL+A3" from 01OCT2019 to 01MAY2020

        # The DH trips are created to ensure no landings for crew 1 during this period
        Given a trip with the following activities
            | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
            | leg | 0011 | OSL     | ARN     | 25APR2020 | 06:00 | 07:10 | SK  | 320    |
            | dh  | 0012 | ARN     | OSL     | 25APR2020 | 07:55 | 09:10 | SK  | 320    |
            | leg | 0013 | OSL     | ARN     | 26APR2020 | 06:00 | 07:10 | SK  | 333    |
            | dh  | 0014 | ARN     | OSL     | 26APR2020 | 07:55 | 09:10 | SK  | 333    |

        Given trip 1 is assigned to crew member 1 in position FP
        Given trip 1 is assigned to crew member 2 in position FC


    Scenario: A2A3 qualified pilot with correct flights to remain recent
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 3 on roster 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 4 on roster 1

    Scenario: Too few A3 landings (4x A2 landings) A3 too long ago
        
        Given table accumulator_time additionally contains the following
        | name                           | acckey        | tim       | filt |
        | accumulators.last_landing_a320 | crew member 1 | 05MAR2020 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 3 on roster 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 4 on roster 1

    Scenario: Too few total landings (1x A2, 1x A3)
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | dh  | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | dh  | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 3 on roster 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 4 on roster 1

    Scenario: Correct number of landings, one outside PP

        Given table accumulator_time additionally contains the following
        | name                           | acckey        | tim       | filt |
        | accumulators.last_landing_a320 | crew member 1 | 26FEB2020 |      |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | dh  | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | dh  | 0004 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 3 on roster 1
        Then rave "recency.%leg_is_recent%" shall be "True" on leg 1 on trip 4 on roster 1

    Scenario: Correct number of landings but too long ago
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 02MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | CPH     | 02MAR2020 | 07:55 | 09:10 | SK  | 320    |
        | leg | 0003 | CPH     | OSL     | 02MAR2020 | 10:55 | 12:10 | SK  | 320    |


        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0004 | OSL     | ARN     | 03MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0005 | ARN     | CPH     | 03MAR2020 | 07:55 | 09:10 | SK  | 333    |
        | leg | 0006 | CPH     | OSL     | 03MAR2020 | 10:55 | 12:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 02MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 02MAR2020 | "SK 000002 "  | ARN         | crew member 1    | CPH    | 1           | True  |
        | 02MAR2020 | "SK 000003 "  | CPH         | crew member 1    | OSL    | 1           | True  |
        | 03MAR2020 | "SK 000004 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 03MAR2020 | "SK 000005 "  | ARN         | crew member 1    | CPH    | 1           | True  |
        | 03MAR2020 | "SK 000006 "  | CPH         | crew member 1    | OSL    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 3 on roster 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 4 on roster 1

    Scenario: Expirary warning when nearing unrecent for A3
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0002 | ARN     | OSL     | 12MAR2020 | 07:55 | 09:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |
        | leg | 0003 | ARN     | OSL     | 13MAR2020 | 07:55 | 09:10 | SK  | 333    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 23APR2020 | 06:00 | 07:10 | SK  | 320    |
        | leg | 0003 | ARN     | OSL     | 23APR2020 | 07:55 | 09:10 | SK  | 320    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 12MAR2020 | "SK 000002 "  | ARN         | crew member 1    | OSL    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000004 "  | ARN         | crew member 1    | OSL    | 1           | True  |

        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC

        When I show "crew" in window 1
        Then rave "roster_cost.%first_expiry_date_distance_to_leg%" shall be "0" on leg 1 on trip 3 on roster 1


    Scenario: A2A3 qualified pilot with correct flights to remain recent
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | ARN     | 12MAR2020 | 06:00 | 07:10 | SK  | 320    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0003 | OSL     | ARN     | 13MAR2020 | 06:00 | 07:10 | SK  | 333    |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0005 | OSL     | ARN     | 10APR2020 | 06:00 | 07:10 | SK  | 333    |

        Given table crew_landing additionally contains the following
        | leg_udor  | leg_fd        | leg_adep    | crew             | airport| nr_landings | activ |
        | 12MAR2020 | "SK 000001 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000002 "  | OSL         | crew member 1    | ARN    | 1           | True  |
        | 13MAR2020 | "SK 000003 "  | OSL         | crew member 1    | ARN    | 1           | True  |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 2 is assigned to crew member 1 in position FC
        Given trip 3 is assigned to crew member 1 in position FC


        When I show "crew" in window 1
        Then rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 2 on roster 1
