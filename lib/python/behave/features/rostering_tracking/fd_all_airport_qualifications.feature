Feature: Check that airport qualifications are handled correctly
    Background: Set up common data
        Given planning period from 1MAR2020 to 31MAR2020
        # One crew member for each AC qual A2-A5
        Given a crew member with
            | attribute  | value |
            | crew rank  | FC    |
            | title rank | FC    |
            | region     | SKI   |
            | base       | STO   |
        Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
        
        Given a crew member with
            | attribute  | value |
            | crew rank  | FC    |
            | title rank | FC    |
            | region     | SKI   |
            | base       | STO   |
        Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2018 to 31DEC2035
        
        Given a crew member with
            | attribute  | value |
            | crew rank  | FC    |
            | title rank | FC    |
            | region     | SKI   |
            | base       | STO   |
        Given crew member 3 has qualification "ACQUAL+A4" from 1JAN2018 to 31DEC2035
        
        Given a crew member with
            | attribute  | value |
            | crew rank  | FC    |
            | title rank | FC    |
            | region     | SKI   |
            | base       | STO   |
        Given crew member 4 has qualification "ACQUAL+A5" from 1JAN2018 to 31DEC2035


    @SCENARIO1
    Scenario: INN requires the qualification to be of a specific AC qual
        Given table crew_qual_acqual additionally contains the following
            | crew         | qual_typ | qual_subtype | acqqual_typ | acqqual_subtype | validfrom | validto   |
            | crew member 1| ACQUAL   | A2           | AIRPORT     | INN             | 01JAN2020 | 01OCT2020 |
            | crew member 2| ACQUAL   | A2           | AIRPORT     | INN             | 01JAN2020 | 01OCT2020 |
        

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0001 | ARN     | INN     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 320    |
        | leg | 0002 | INN     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 320    |

        Given trip 1 is assigned to crew member 1 in position FC

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0003 | ARN     | INN     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 333    |
        | leg | 0004 | INN     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 333    |
    
        Given trip 2 is assigned to crew member 2 in position FC
        
        When I show "crew" in window 1 
        and I load rule set "Tracking"

        Then rave "qualification.%airport_is_valid_for_crew_restriction%("INN")" shall be "True" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%leg_extends_airport_qual%" shall be "INN" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%leg_extends_airport_qual_extension%" shall be "31MAR2021 00:00" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%airport_qual_ac_qual_code%" shall be "A2" on leg 1 on trip 1 on roster 1

        Then rave "qualification.%airport_is_valid_for_crew_restriction%("INN")" shall be "False" on leg 1 on trip 1 on roster 2


    @SCENARIO2
    Scenario: For US airports AC qual AWD is used for A2,A3,A4,A5

        Given table crew_qual_acqual additionally contains the following
            | crew         | qual_typ | qual_subtype | acqqual_typ | acqqual_subtype | validfrom | validto   |
            | crew member 1| ACQUAL   | AWB          | AIRPORT     | US              | 01JAN2020 | 01OCT2020 |
            | crew member 2| ACQUAL   | AWB          | AIRPORT     | US              | 01JAN2020 | 01OCT2020 |
            | crew member 3| ACQUAL   | AWB          | AIRPORT     | US              | 01JAN2020 | 01OCT2020 |
            | crew member 4| ACQUAL   | AWB          | AIRPORT     | US              | 01JAN2020 | 01OCT2020 |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0001 | ARN     | ORD     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 320    |
        | leg | 0002 | ORD     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 320    |

        Given trip 1 is assigned to crew member 1 in position FC

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0003 | ARN     | ORD     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 333    |
        | leg | 0004 | ORD     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 333    |
    
        Given trip 2 is assigned to crew member 2 in position FC

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0005 | ARN     | ORD     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 340    |
        | leg | 0006 | ORD     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 340    |

        Given trip 3 is assigned to crew member 3 in position FC

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0007 | ARN     | ORD     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 350    |
        | leg | 0008 | ORD     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 350    |
    
        Given trip 4 is assigned to crew member 4 in position FC

        When I show "crew" in window 1 
        and I load rule set "Tracking"

        Then rave "qualification.%airport_is_valid_for_crew_restriction%(leg.%end_station%)" shall be "True" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%leg_extends_airport_qual%" shall be "US" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%leg_extends_airport_qual_extension%" shall be "31MAR2021 00:00" on leg 1 on trip 1 on roster 1
        Then rave "training_log.%airport_qual_ac_qual_code%" shall be "AWB" on leg 1 on trip 1 on roster 1

        Then rave "qualification.%airport_is_valid_for_crew_restriction%(leg.%end_station%)" shall be "True" on leg 1 on trip 1 on roster 2
        Then rave "training_log.%leg_extends_airport_qual%" shall be "US" on leg 1 on trip 1 on roster 2
        Then rave "training_log.%leg_extends_airport_qual_extension%" shall be "31MAR2021 00:00" on leg 1 on trip 1 on roster 2
        Then rave "training_log.%airport_qual_ac_qual_code%" shall be "AWB" on leg 1 on trip 1 on roster 2

        Then rave "qualification.%airport_is_valid_for_crew_restriction%(leg.%end_station%)" shall be "True" on leg 1 on trip 1 on roster 3
        Then rave "training_log.%leg_extends_airport_qual%" shall be "US" on leg 1 on trip 1 on roster 3
        Then rave "training_log.%leg_extends_airport_qual_extension%" shall be "31MAR2021 00:00" on leg 1 on trip 1 on roster 3
        Then rave "training_log.%airport_qual_ac_qual_code%" shall be "AWB" on leg 1 on trip 1 on roster 3

        Then rave "qualification.%airport_is_valid_for_crew_restriction%(leg.%end_station%)" shall be "True" on leg 1 on trip 1 on roster 4
        Then rave "training_log.%leg_extends_airport_qual%" shall be "US" on leg 1 on trip 1 on roster 4
        Then rave "training_log.%leg_extends_airport_qual_extension%" shall be "31MAR2021 00:00" on leg 1 on trip 1 on roster 4
        Then rave "training_log.%airport_qual_ac_qual_code%" shall be "AWB" on leg 1 on trip 1 on roster 4


    @SCENARIO3
    Scenario: Any A2NX US leg with FC not qualified for US airport should create AIRPORT+US qualification

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ |
        | leg | 0001 | ARN     | ORD     | 7MAR2020 10:00 | 7MAR2020 11:00 | SK  | 320    |
        | leg | 0002 | ORD     | ARN     | 7MAR2020 12:00 | 7MAR2020 13:00 | SK  | 320    |

        Given trip 1 is assigned to crew member 1 in position FP
        
        When I show "crew" in window 1
        and I load rule set "Tracking"
        Then rave "training_log.%training_leg_should_create_apt_qual%" shall be "True" on leg 1 on trip 1 on roster 1
