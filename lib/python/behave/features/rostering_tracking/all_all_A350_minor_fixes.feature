@TRACKING @PLANNING
Feature: Confirms the functionality of these minor A350-related changes, as well as the pre-existing functionality being intact.
# JIRA - SKCMS-2082

##############################################################################
    Background: Set up common data
        Given Tracking

        Given a crew member with
        | attribute  | value |
        | crew rank  | FC    |
        | title rank | FC    |
        | region     | SKI   |
        | base       | STO   |

        Given a crew member with
        | attribute  | value |
        | crew rank  | AH    |
        | title rank | AH    |
        | region     | SKI   |
        | base       | STO   |

        Given a crew member with
        | attribute  | value |
        | crew rank  | AH    |
        | title rank | AH    |
        | region     | SKI   |
        | base       | STO   |

        Given table ac_qual_map additionally contains the following
        | ac_type | aoc | ac_qual_fc | ac_qual_cc |
        | 35X     | SK  | A5         | AL         |

##############################################################################


        @A350_Fixes_1
        Scenario: A5 should be exempt from AST time of day rules

        Given planning period from 1JUN2019 to 1JUL2019

        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A2" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act    | code | dep stn | arr stn | dep            | arr            |
        | ground | K5   | ARN     | ARN     | 6JUN2019 04:00 | 6JUN2019 05:00 |

        Given a trip with the following activities
        | act    | code | dep stn | arr stn | dep            | arr            |
        | ground | K2   | ARN     | ARN     | 7JUN2019 04:00 | 7JUN2019 05:00 |

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1

        When I show "crew" in window 1

        # A5 AST should be allowed during night hours
        Then the rule "rules_studio_ccp.ast_allowed_time_of_day" shall pass on leg 1 on trip 1 on roster 1
        # A2 (and other non-LH quals) AST should still not be allowed during night hours
        and the rule "rules_studio_ccp.ast_allowed_time_of_day" shall fail on leg 1 on trip 2 on roster 1


        @A350_Fixes_2
        Scenario: Standby codes containing 5 should translate to AC family A350

        Given planning period from 1JUN2019 to 1JUL2019
        
        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 2 has qualification "ACQUAL+AL" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ | code |
        | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 359    | R5S  |
        | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 359    | R5S  |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 1 is assigned to crew member 2 in position AH

        When I show "crew" in window 1

        # The qualification filtering should properly handle the new code for A350, both for CC and FC
        Then rave "qualification.%trip_sim_sby_qual%" shall be "A5" on leg 1 on trip 1 on roster 1
        and rave "qualification.%trip_sim_sby_qual%" shall be "AL" on leg 1 on trip 1 on roster 2


        @A350_Fixes_3
        Scenario: Simulator activity codes containing 5 should translate to AC family A350

        Given planning period from 1JUN2019 to 1JUL2019

        When I show "crew" in window 1

        Then rave "model_training.%sim_ac_family%("K5")" shall be "A350"
        # Ensure that the first number is prioritized
        and rave "model_training.%sim_ac_family%("K45")" shall be "A340"


        @A350_Fixes_4
        Scenario: last_flown accumulator access functions should work for A350, both for A5 crew and AL crew.

        Given planning period from 1JUN2019 to 1JUL2019
        
        Given table accumulator_time additionally contains the following
        | name                         | acckey        | tim       | filt |
        | accumulators.last_flown_a350 | crew member 1 | 1APR2019  |      |
        | accumulators.last_flown_a350 | crew member 2 | 1APR2019  |      |
        | accumulators.last_flown_a320 | crew member 2 | 2APR2019  |      |
        | accumulators.last_flown_a350 | crew member 3 | 1APR2019  |      |
        | accumulators.last_flown_a340 | crew member 3 | 2APR2019  |      |

        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 2 has qualification "ACQUAL+AL" from 1FEB2019 to 31DEC2035
        Given crew member 3 has qualification "ACQUAL+AL" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 359    |
        | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 359    |

        Given trip 1 is assigned to crew member 1 in position FC
        Given trip 1 is assigned to crew member 2 in position AH
        Given trip 1 is assigned to crew member 3 in position AH

        When I show "crew" in window 1

        Then rave "recency.%last_flown_ac_qual%("A5", leg.%start_UTC%)" shall be "01APR2019 00:00" on leg 1 on trip 1 on roster 1
        # Crew 2 has a more recent A320 flown, but that shall not be counted for AL
        and rave "recency.%last_flown_ac_qual%("AL", leg.%start_UTC%)" shall be "01APR2019 00:00" on leg 1 on trip 1 on roster 2
        # Crew 3 has a more recent A340 flown, which should be the most recent date for AL
        and rave "recency.%last_flown_ac_qual%("AL", leg.%start_UTC%)" shall be "02APR2019 00:00" on leg 1 on trip 1 on roster 3


        @A350_Fixes_5
        Scenario: Longhaul definitions should support A350 as well as work as before

        Given planning period from 1JUN2019 to 1JUL2019

        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 1 has acqual qualification "ACQUAL+A5+INSTRUCTOR+SUP" from 1FEB2019 to 31DEC2035
        Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2019 to 31DEC2035
        Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SUP" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 359    |
        | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 359    |

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 7JUN2019 10:00 | 7JUN2019 11:00 | 32A    |
        | leg | SK  | 002 | HEL     | ARN     | 7JUN2019 12:00 | 7JUN2019 13:00 | 32A    |

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 2

        When I show "crew" in window 1

        # Crew 1 (Longhaul)
        Then rave "crew.%is_long_haul%(leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "crew.%is_short_haul%(leg.%start_UTC%)" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "crew.%has_qln_lh_in_pp%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "crew.%last_long_haul_qln_start%" shall be "01FEB2019 00:00" on leg 1 on trip 1 on roster 1
        and rave "crew.%has_airbus_qual_at_date%(leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "crew.%is_sup_instr_qualgroup%("A3", leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "leg.%with_long_haul_ac%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "leg.%is_long_haul_aircraft%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "leg.%code_for_areaqual%" shall be "LH" on leg 1 on trip 1 on roster 1
        # Crew 2 (Shorthaul)
        and rave "crew.%is_long_haul%(leg.%start_UTC%)" shall be "False" on leg 1 on trip 1 on roster 2
        and rave "crew.%is_short_haul%(leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 2
        and rave "crew.%has_qln_lh_in_pp%" shall be "False" on leg 1 on trip 1 on roster 2
        and rave "crew.%last_long_haul_qln_start%" shall be "01JAN1986 00:00" on leg 1 on trip 1 on roster 2
        and rave "crew.%has_airbus_qual_at_date%(leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 2
        and rave "crew.%is_sup_instr_qualgroup%("A3", leg.%start_UTC%)" shall be "True" on leg 1 on trip 1 on roster 2
        and rave "leg.%with_long_haul_ac%" shall be "False" on leg 1 on trip 1 on roster 2
        and rave "leg.%is_long_haul_aircraft%" shall be "False" on leg 1 on trip 1 on roster 2
        and rave "leg.%code_for_areaqual%" shall be "A2" on leg 1 on trip 1 on roster 2


        @A350_Fixes_6
        Scenario: The new A5 planning area defenitions should work as expected given the input from PlanningAreas.py

        Given planning period from 1JUN2019 to 1JUL2019

        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 2 has qualification "ACQUAL+A2" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 359    |
        | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 359    |

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 7JUN2019 10:00 | 7JUN2019 11:00 | 32A    |
        | leg | SK  | 002 | HEL     | ARN     | 7JUN2019 12:00 | 7JUN2019 13:00 | 32A    |

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 2

        When I show "crew" in window 1
        and I load rule set "Rostering_FC"
        and I set parameter "fundamental.%start_para%" to "1JUN2019 00:00"
        and I set parameter "fundamental.%end_para%" to "1JUL2019 00:00"
        and I set parameter "planning_area.%planning_area_crew_qualification_p%" to "planning_area.A330_340_350_QUAL"
        and I set parameter "planning_area.%planning_area_trip_ac_fam_p%" to "planning_area.A330_340_350_FAM"
        and I set parameter "planning_area.%planning_area_leg_ac_fam_p%" to "planning_area.A330_340_350_FAM"

        Then rave "planning_area.%planning_area_crew_qualification%" shall be "A3,A4,A5" on leg 1 on trip 1 on roster 1
        and rave "planning_area.%planning_area_trip_ac_fam%" shall be "A330,A340,A350" on leg 1 on trip 1 on roster 1
        and rave "planning_area.%leg_has_planning_area_ac_family%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "planning_area.%leg_has_planning_area_ac_family%" shall be "False" on leg 1 on trip 1 on roster 2


        @A350_Fixes_7
        Scenario: Check- in and out times should match other longhaul airbus flights

        Given planning period from 1JUN2019 to 1JUL2019

        Given crew member 1 has qualification "ACQUAL+A5" from 1FEB2019 to 31DEC2035
        Given crew member 1 has qualification "ACQUAL+A3" from 1FEB2019 to 31DEC2035

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep            | arr            | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 5JUN2019 10:00 | 5JUN2019 11:00 | 33A    |
        | leg | SK  | 002 | HEL     | ARN     | 5JUN2019 12:00 | 5JUN2019 13:00 | 33A    |

        Given a trip with the following activities
        | act | car | num | dep stn | arr stn | dep             | arr             | ac_typ |
        | leg | SK  | 001 | ARN     | HEL     | 10JUN2019 10:00 | 10JUN2019 11:00 | 359    |
        | leg | SK  | 002 | HEL     | ARN     | 10JUN2019 12:00 | 10JUN2019 13:00 | 359    |

        Given trip 1 is assigned to crew member 1
        Given trip 2 is assigned to crew member 1

        When I show "crew" in window 1

        # A3
        Then rave "leg.%has_check_in%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "leg.%has_check_in%" shall be "False" on leg 2 on trip 1 on roster 1
        and rave "leg.%has_check_out%" shall be "False" on leg 1 on trip 1 on roster 1
        and rave "leg.%has_check_out%" shall be "True" on leg 2 on trip 1 on roster 1
        and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 1
        and rave "leg.%check_in%" shall be "0:45" on leg 2 on trip 1 on roster 1
        and rave "leg.%check_out%" shall be "0:15" on leg 1 on trip 1 on roster 1
        and rave "leg.%check_out%" shall be "0:30" on leg 2 on trip 1 on roster 1

        # A5
        Then rave "leg.%has_check_in%" shall be "True" on leg 1 on trip 2 on roster 1
        and rave "leg.%has_check_in%" shall be "False" on leg 2 on trip 2 on roster 1
        and rave "leg.%has_check_out%" shall be "False" on leg 1 on trip 2 on roster 1
        and rave "leg.%has_check_out%" shall be "True" on leg 2 on trip 2 on roster 1
        and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 2 on roster 1
        and rave "leg.%check_in%" shall be "0:45" on leg 2 on trip 2 on roster 1
        and rave "leg.%check_out%" shall be "0:15" on leg 1 on trip 2 on roster 1
        and rave "leg.%check_out%" shall be "0:30" on leg 2 on trip 2 on roster 1