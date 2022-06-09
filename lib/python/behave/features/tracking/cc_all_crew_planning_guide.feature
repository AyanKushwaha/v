@TRACKING @SBY @ALL @CC @PLANNING_GUIDE @LH
Feature: Testing Crew planning guide rules

    Background: Setup for tracking
        Given Tracking
        Given planning period from 1FEB2019 to 1APR2019

        Given a crew member with
        | attribute | value |
        | base      | OSL   |
        | title rank| AH    |
        | region    | SKS   |

        Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2019 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 01JAN2019 to 31DEC2035
    @SCENARIO1
    Scenario: DH should not trigger longhaul warning after sby at airport.
        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
         | DH | 0001 | OSL     | LHR     | 24FEB2019 | 17:00 | 18:00 | SK  | 320    |
         | DH | 0002 | LHR     | OSL     | 24FEB2019 | 19:00 | 20:00 | SK  | 320    |
     
        Given table crew_publish_info additionally contains the following
         | crew          | start_date | end_date  | flags |
         | crew member 1 | 24FEB2019  | 25FEB2019 | :hsa  |

        Given trip 1 is assigned to crew member 1 in position AH
        
        Given crew member 1 has a personal activity "RL" at station "OSL" that starts at 24FEB2019 10:00 and ends at 24FEB2019 14:00

        Given the roster is published

        When I show "crew" in window 1
        Then the rule "rules_crew_planning_guide_cct.cpg_longhaul_after_airport_sby_CC" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO2
    Scenario: Standby should not trigger longhaul_after_airport_sby
        
        Given table crew_publish_info additionally contains the following
         | crew          | start_date | end_date  | flags |
         | crew member 1 | 24FEB2019  | 25FEB2019 | :hsa  |

        Given crew member 1 has a personal activity "RC" at station "OSL" that starts at 24FEB2019 10:00 and ends at 24FEB2019 14:00
        Given crew member 1 has a personal activity "AC" at station "OSL" that starts at 24FEB2019 16:00 and ends at 24FEB2019 20:00

        Given the roster is published

        When I show "crew" in window 1
        Then the rule "rules_crew_planning_guide_cct.cpg_longhaul_after_airport_sby_CC" shall pass on leg 1 on trip 1 on roster 1

    @SCENARIO3
    Scenario: Freeday should not trigger longhaul_after_airport_sby
        
        Given table crew_publish_info additionally contains the following
         | crew          | start_date | end_date  | flags |
         | crew member 1 | 24FEB2019  | 25FEB2019 | :hsa  |

        Given crew member 1 has a personal activity "RL" at station "OSL" that starts at 24FEB2019 10:00 and ends at 24FEB2019 14:00
        Given crew member 1 has a personal activity "F" at station "OSL" that starts at 25FEB2019 00:00 and ends at 25FEB2019 23:59

        Given the roster is published

        When I show "crew" in window 1
        Then the rule "rules_crew_planning_guide_cct.cpg_longhaul_after_airport_sby_CC" shall pass on leg 1 on trip 1 on roster 1
