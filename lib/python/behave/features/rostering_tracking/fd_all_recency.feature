########################
# JIRA - SKCMS-2075
########################
@planning @tracking
Feature: Recency requirements for crew with three qualifications to handle the A5 and triple qualification.

    Background: Setup common data

    Given table aircraft_type additionally contains the following
      | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc |
      | 35X | A350     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |

    Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 1 | FAM FLT | A5   | 01Oct2018 10:22 |
      | crew member 1 | FAM FLT | A5   | 01Oct2018 12:22 |

    Given table crew_training_need additionally contains the following
    | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
    | crew member 1 | 1    | 1FEB2018  | 31AUG2019 | CTR-A3A5 | FAM FLT   | 2       | 21       | A5     |            |


    @SCENARIO1
    Scenario: Rule passes if FC have 3 total landings within 90 days.

    Given Tracking
    Given planning period from 1Nov2018 to 01Jan2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 16Nov2018 | 10:25 | 21:45 | SK  |  35X   |
    | leg | 0002 | SFO     | CPH     | 18Nov2018 | 00:35 | 11:15 | SK  |  34A   |
    Given trip 1 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | SFO     | 16Dec2018 | 10:25 | 21:45 | SK  |  33A   |
    | leg | 0004 | SFO     | CPH     | 18Dec2018 | 00:35 | 11:15 | SK  |  33A   |
    Given trip 2 is assigned to crew member 1

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | CPH     | SFO     | 27Dec2018 | 10:25 | 21:45 | SK  |  35X   |
    | leg | 0006 | SFO     | CPH     | 28Dec2018 | 00:35 | 11:15 | SK  |  35X   |
    Given trip 3 is assigned to crew member 1

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 16Nov2018 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 18Nov2018 | "SK 000002 "  | SFO         | crew member 1    | CPH     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 16Dec2018 | "SK 000003 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 18Dec2018 | "SK 000004 "  | SFO         | crew member 1    | CPH     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 27Dec2018 | "SK 000005 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 28Dec2018 | "SK 000006 "  | SFO         | crew member 1    | CPH     | 1           | True  |


    When I show "crew" in window 1
    Then the rule "rules_training_ccr.qln_recency_ok_ALL" shall pass on leg 2 on trip 3 on roster 1
    and the rule "rules_training_ccr.trng_max_days_between_sim_and_fam_flt_fc" shall pass on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_is_recent%" shall be "True" on leg 2 on trip 3 on roster 1
    and rave "recency.%leg_has_at_least_one_landing_of_leg_qual_for_recency%" shall be "True" on leg 2 on trip 3 on roster 1


    @SCENARIO2
    Scenario: Rule fail if FC have less than 3 total landings within 90 days.

    Given Tracking
    Given planning period from 1Sep2018 to 30Apr2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |



    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 16Oct2018 | 10:25 | 21:45 | SK  |  34A   |
    | leg | 0002 | SFO     | CPH     | 18Oct2018 | 00:35 | 11:15 | SK  |  34A   |
    Given trip 1 is assigned to crew member 1


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | SFO     | 27Mar2019 | 10:25 | 21:45 | SK  |  35X   |
    | leg | 0004 | SFO     | CPH     | 28Mar2019 | 00:35 | 11:15 | SK  |  35X   |
    Given trip 2 is assigned to crew member 1


    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 16Oct2018 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 27Mar2019 | "SK 000003 "  | CPH         | crew member 1    | SFO     | 1           | True  |


    When I show "crew" in window 1
    Then the rule "rules_training_ccr.qln_recency_ok_ALL" shall fail on leg 1 on trip 1 on roster 1
    and rave "recency.%leg_is_recent%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "recency.%leg_is_recent%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "recency.%leg_has_at_least_one_landing_of_leg_qual_for_recency%" shall be "True" on leg 2 on trip 2 on roster 1


    @SCENARIO3
    Scenario: Rule fail if FC have less than 1 landings with A5 within 45 days.

    Given Tracking
    Given planning period from 1Nov2018 to 30Apr2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |

    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | CPH     | SFO     | 27Apr2019 | 10:25 | 21:45 | SK  |  34A   |
    | leg | 0006 | SFO     | CPH     | 28Apr2019 | 00:35 | 11:15 | SK  |  34A   |
    Given trip 1 is assigned to crew member 1

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 16Nov2018 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |


    When I show "crew" in window 1
    Then rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "recency.%leg_is_recent%" shall be "False" on leg 2 on trip 1 on roster 1
    and rave "recency.%leg_has_at_least_one_landing_of_leg_qual_for_recency%" shall be "False" on leg 2 on trip 1 on roster 1

    @SCENARIO4
    Scenario: Rule passes if FC have a minimum of 1 landing A5 with FAM FLT within 45 days.

    Given Tracking
    Given planning period from 1Mar2019 to 30May2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |


    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 15May2019 | 10:25 | 21:45 | SK  |  35X   |
    | leg | 0002 | SFO     | CPH     | 17May2019 | 00:35 | 11:15 | SK  |  35X   |
    Given trip 1 is assigned to crew member 1 in position FC with
    | type      | leg | name     | value   |
	| attribute | 1-2 | TRAINING | FAM FLT |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | SFO     | 25May2019 | 10:25 | 21:45 | SK  |  35X   |
    | leg | 0004 | SFO     | CPH     | 27May2019 | 00:35 | 11:15 | SK  |  35X   |
    Given trip 2 is assigned to crew member 1 in position FC

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 15May2019 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 17May2019 | "SK 000002 "  | SFO         | crew member 1    | CPH     | 1           | True  |



    When I show "crew" in window 1
    Then rave "recency.%leg_has_at_least_one_landing_of_leg_qual_for_recency%" shall be "True" on leg 2 on trip 2 on roster 1
    and rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "False" on leg 2 on trip 2 on roster 1

    @SCENARIO5
    Scenario: Rule passes if FC have a minimum of 1 landing A5 with FAM FLT within 45 days.

    Given Tracking
    Given planning period from 1Mar2019 to 30May2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |


    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022


       Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 15May2019 | 10:25 | 21:45 | SK  |  33A   |
    | leg | 0002 | SFO     | CPH     | 17May2019 | 00:35 | 11:15 | SK  |  35X   |
     Given trip 1 is assigned to crew member 1 in position FC with
    | type      | leg | name     | value   |
    | attribute | 1-2 | TRAINING | FAM FLT |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 20May2019 | 10:25 | 21:45 | SK  |  33A   |
    | leg | 0002 | SFO     | CPH     | 22May2019 | 00:35 | 11:15 | SK  |  35X   |

    Given trip 2 is assigned to crew member 1 in position FC

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 15May2019 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 17May2019 | "SK 000002 "  | SFO         | crew member 1    | CPH     | 1           | True  |
    | 20May2019 | "SK 000003 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 22May2019 | "SK 000004 "  | SFO         | crew member 1    | SFO     | 1           | True  |

    When I load ruleset "Rostering_FC"
    When I show "crew" in window 1
    Then the rule "rules_training_ccr.qln_recency_ok_ALL" shall pass on leg 2 on trip 1 on roster 1
    and rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "False" on leg 2 on trip 1 on roster 1


    @SCENARIO6
    Scenario: Rule fail if FC have a minimum of 1 landing A5 with FAM FLT outside of 45 days.

    Given Tracking
    Given planning period from 1Mar2019 to 30May2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |

    Given table ac_qual_map additionally contains the following
      | ac_type | aoc | ac_qual_fc | ac_qual_cc |
      | 35X     | SK  | A5         | AL         |


    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 15May2019 | 10:25 | 21:45 | SK  |  33A   |
    | leg | 0002 | SFO     | CPH     | 17May2019 | 00:35 | 11:15 | SK  |  35X   |
    Given trip 1 is assigned to crew member 1 in position FC

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 16Mar2019 | 10:25 | 21:45 | SK  |  33A   |
    | leg | 0002 | SFO     | CPH     | 17Mar2019 | 00:35 | 11:15 | SK  |  35X   |

    Given trip 2 is assigned to crew member 1 in position FC

    Given table crew_landing additionally contains the following
    | leg_udor  | leg_fd        | leg_adep    | crew             | airport | nr_landings | activ |
    | 15May2019 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |
    | 17Mar2019 | "SK 000002 "  | SFO         | crew member 1    | CPH     | 1           | True  |
    | 16Mar2019 | "SK 000001 "  | CPH         | crew member 1    | SFO     | 1           | True  |

    When I show "crew" in window 1
    Then the rule "rules_training_ccr.qln_recency_ok_ALL" shall fail on leg 2 on trip 2 on roster 1
    and rave "recency.%leg_has_enough_total_landings_for_recency%" shall be "False" on leg 2 on trip 1 on roster 1


    # The simulator types K* correspond to the following AC types:
    # K2 - A2
    # K3 - 38
    # K4 - A4
    # K5 - A5
    # K6 - A3

    @SCENARIO7 @CORONA
    Scenario: AST doesn't give full recency to the relevant ac qual due to corona (A3A4A5 pilot)

    Given Tracking
    Given planning period from 1Mar2020 to 30May2020

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |


    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A4" from 1Oct2018 to 01JAN2022
    
    # K4/K6 both give recency to A3A4 
    Given crew member 1 has a personal activity "K4" at station "OSL" that starts at 01MAR2020 08:00 and ends at 01MAR2020 18:30
    Given crew member 1 has a personal activity "K5" at station "OSL" that starts at 02MAR2020 08:00 and ends at 02MAR2020 18:30

    When I show "crew" in window 1
    Then rave "recency.%expiry_date%(20MAR2020, "A5")" shall be "14FEB1986 23:59" on leg 1 on trip 1 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "A3")" shall be "31MAR1986 23:59" on leg 1 on trip 1 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "A4")" shall be "31MAR1986 23:59" on leg 1 on trip 1 on roster 1

    @SCENARIO8 @CORONA
    Scenario: AST doesn't give full recency to all ac quals due to corona (A2A3 pilot)

    Given Tracking
    Given planning period from 1Mar2020 to 30May2020

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |


    Given crew member 1 has qualification "ACQUAL+A2" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022

    
    Given crew member 1 has a personal activity "K2" at station "OSL" that starts at 01MAR2020 08:00 and ends at 01MAR2020 18:30
    Given crew member 1 has a personal activity "K6" at station "OSL" that starts at 02MAR2020 08:00 and ends at 02MAR2020 18:30

    When I show "crew" in window 1
    Then rave "recency.%expiry_date%(20MAR2020, "A2")" shall be "31MAR1986 23:59" on leg 2 on trip 1 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "A3")" shall be "14FEB1986 23:59" on leg 2 on trip 1 on roster 1
    
    @SCENARIO9 @CORONA
    Scenario: AST doesn't give full recency to all ac quals due to corona (A2 38 pilot)

    Given Tracking
    Given planning period from 1Mar2020 to 30May2020

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |


    Given crew member 1 has qualification "ACQUAL+A2" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+38" from 1Oct2018 to 01JAN2022

    
    Given crew member 1 has a personal activity "K2" at station "OSL" that starts at 01MAR2020 08:00 and ends at 01MAR2020 18:30
    Given crew member 1 has a personal activity "K3" at station "OSL" that starts at 02MAR2020 08:00 and ends at 02MAR2020 18:30

    When I show "crew" in window 1
    Then rave "recency.%expiry_date%(20MAR2020, "A2")" shall be "31MAR1986 23:59" on leg 2 on trip 1 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "38")" shall be "31MAR1986 23:59" on leg 2 on trip 1 on roster 1


 @SCENARI10 @CORONA
    Scenario: SIM ASSIST LANDINGs gives full recency to all ac quals due to corona (A2 38 pilot)

    Given Rostering_FC
    Given planning period from 1Mar2020 to 30May2020

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |


    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022

     Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | S5   | OSL     | OSL     | 2Mar2020  | 13:00 | 17:00 |
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="SIM ASSIST LANDINGS"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 10Mar2020 | 10:25 | 21:45 | SK  |  35A   |
    | leg | 0002 | SFO     | CPH     | 12Mar2020 | 00:35 | 11:15 | SK  |  35A   |
    Given trip 2 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "recency.%expiry_date%(20MAR2020, "A5")" shall be "15APR2020 23:59" on leg 2 on trip 2 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "A3")" shall be "31MAR1986 23:59" on leg 2 on trip 2 on roster 1


 @SCENARIO11 
    Scenario: ASF gives full recency to all ac quals due to corona (A2 38 pilot)

    Given Rostering_FC
    Given planning period from 1Mar2020 to 30May2020

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FC      |             |           |
    | region     | SKN     |             |           |


    Given crew member 1 has qualification "ACQUAL+A5" from 1Oct2018 to 01JAN2022
    Given crew member 1 has qualification "ACQUAL+A3" from 1Oct2018 to 01JAN2022

      Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | C5RF1| OSL     | OSL     | 10Mar2020 | 10:00 | 11:00 |
    Given trip 1 is assigned to crew member 1
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 12Mar2020 | 10:00 | 11:00 | SK  | 35A    |
    | leg | 0002 | LHR     | OSL     | 14Mar2020 | 12:00 | 13:00 | SK  | 35A    |
    Given trip 2 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then rave "recency.%expiry_date%(20MAR2020, "A5")" shall be "23APR2020 23:59" on leg 1 on trip 1 on roster 1
    Then rave "recency.%expiry_date%(20MAR2020, "A3")" shall be "31MAR1986 23:59" on leg 1 on trip 1 on roster 1
