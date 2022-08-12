@TRACKING @JCRT @FD @RECENCY
Feature: Test the rule rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh

##############################################################################
  Background: Setup common data
    Given planning period from 1JAN2021 to 1FEB2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKN        | 27NOV2020  | 09DEC2022 |
           | base            | OSL        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FC         | 01DEC2020  | 31DEC2035 |
           | contract        | V00007     | 28SEP2020  | 08JAN2022 |

    Given crew member 1 has qualification "ACQUAL+A2" from 28SEP2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKN        | 27NOV2020  | 09DEC2022 |
           | base            | OSL        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FP         | 01DEC2020  | 31DEC2035 |
           | contract        | V00007     | 28SEP2020  | 08JAN2022 |

    Given crew member 2 has qualification "ACQUAL+A2" from 28SEP2020 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKN        | 27NOV2020  | 09DEC2022 |
           | base            | OSL        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FP         | 01DEC2020  | 31DEC2035 |
           | contract        | V00007     | 28SEP2020  | 28JAN2022 |

  Given crew member 3 has qualification "ACQUAL+A2" from 28SEP2020 to 31DEC2035
  Given crew member 3 has qualification "ACQUAL+38" from 11NOV1996 to 31DEC2035
  
  Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKN        | 27NOV2020  | 09DEC2022 |
           | base            | OSL        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FC         | 01DEC2020  | 31DEC2035 |
           | contract        | V00007     | 28SEP2020  | 08JAN2022 |
  
  Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFI" from 1FEB2020 to 28FEB2022
  Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+SFE" from 1FEB2020 to 28FEB2022
  Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 1FEB2020 to 28FEB2022
  Given crew member 4 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 1FEB2020 to 28FEB2022

    Given table agreement_validity additionally contains the following
        | id                       | validfrom      | validto    |
        | min_sectors_in_max_days  | 01JAN2021      | 31DEC2035  |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | CPH     | 10JAN2021 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | CPH     | OSL     | 10JAN2021 | 12:00 | 13:00 | SK  | 320    |
    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | OSL     | CPH     | 12JAN2021 | 10:00 | 11:00 | SK  | 73A    |
    | leg | 0004 | CPH     | OSL     | 12JAN2021 | 12:00 | 13:00 | SK  | 73A    |
    Given trip 2 is assigned to crew member 1 in position FC
    Given trip 2 is assigned to crew member 2 in position FP

##############################################################################


  @SCENARIO_1
  Scenario: Both crew unrecent

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "1" on leg 2 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "1" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "0" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_failtext%" shall be "Min 1 [8] sectors in last 30 days; must fly with recent" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 2 on trip 1 on roster 2

  @SCENARIO_2
  Scenario: One crew recent - A2 sectors

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 3    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 15DEC2020 00:00 | 10   |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "7" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "8" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 1 on roster 2


  @SCENARIO_3
  Scenario: One crew recent - with simulator

  Given table accumulator_int is overridden with the following
   | name                               | acckey     | tim             | val  |
   | accumulators.sim_sectors_daily_acc | Crew001    | 12DEC2020 00:00 | 3    |
   | accumulators.sim_sectors_daily_acc | Crew001    | 14DEC2020 00:00 | 5    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "12" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "13" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 1 on roster 2


  @SCENARIO_4
  Scenario: One crew recent - qual 38 sectors

  Given table accumulator_int is overridden with the following
   | name                                       | acckey     | tim             | val  |
   | accumulators.q38_flights_sectors_daily_acc | Crew002    | 14DEC2020 00:00 | 1    |
   | accumulators.q38_flights_sectors_daily_acc | Crew002    | 18DEC2020 00:00 | 8    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "7" on leg 1 on trip 2 on roster 2
  and rave "recency.%total_nr_of_sectors%" shall be "8" on leg 2 on trip 2 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 2 on trip 2 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 2 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 2 on roster 2

@SCENARIO_5
  Scenario: Both crew unrecent but together fulfill the condition - A2 sectors

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 15DEC2020 00:00 | 10   |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 15DEC2020 00:00 | 10   |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "5" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "6" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "0" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 1 on trip 1 on roster 2


  @SCENARIO_6
  Scenario: Both crew unrecent but together fulfill the condition for leg 2- A2 sectors

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 15DEC2020 00:00 | 9    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 15DEC2020 00:00 | 9    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "4" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "5" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "0" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 1 on roster 2


  @SCENARIO_7
  Scenario: Both crew unrecent and don't fulfill the condition together- A2 sectors

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 15DEC2020 00:00 | 8    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 15DEC2020 00:00 | 8    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "3" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "4" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "0" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 1 on roster 2


  @SCENARIO_8
  Scenario: Both crew unrecent and don't fulfill the condition together- A2 sectors

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 15DEC2020 00:00 | 8    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew002      | 15DEC2020 00:00 | 8    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "3" on leg 1 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors%" shall be "4" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "0" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 1 on roster 2

  @SCENARIO_9
  Scenario: Both crew unrecent and one crew has 10 sectors and other has 0 sectors- A2 sectors
 
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0005 | OSL     | ARN     | 15JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0006 | ARN     | OSL     | 15JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 3 is assigned to crew member 1 in position FC
  Given trip 3 is assigned to crew member 3 in position FP

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 5    |
   | accumulators.a2_flights_sectors_daily_acc | Crew001      | 31DEC2020 00:00 | 11   |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "8" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 2 on trip 3 on roster 1
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_failtext%" shall be "Min 0 active sectors in last 60 days; need 2 sectors w instr." on leg 1 on trip 3 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 2 on trip 3 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 3 on roster 1

  @SCENARIO_10
  Scenario: One of the crew is recent, but planned next two sectors with instructor- A2 sectors
 
 
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0005 | OSL     | ARN     | 15JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | dh  | 0006 | ARN     | OSL     | 15JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 3 is assigned to crew member 1 in position FC
  Given trip 3 is assigned to crew member 2 in position FP

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 16JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | dh  | 0008 | ARN     | OSL     | 16JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 4 is assigned to crew member 4 in position FC
  Given trip 4 is assigned to crew member 3 in position FP

    Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 17JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0008 | ARN     | OSL     | 17JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 5 is assigned to crew member 4 in position FC
  Given trip 5 is assigned to crew member 3 in position FP

  Given table accumulator_int additionally contains the following
  | name                                      | acckey       | tim             | val  |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 3    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 5    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 31DEC2020 00:00 | 11   |


  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "8" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%number_of_active_sectors_on_max_days_pilot2%" shall be "0" on leg 1 on trip 1 on roster 3
  and rave "rules_training_ccr.%next_sectors_with_instructor_pilot2%" shall be "3" on leg 1 on trip 1 on roster 3
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall pass on leg 1 on trip 1 on roster 3


   @SCENARIO_11
  Scenario: One of the crew is recent, but immediate next two sectors are not planned with instructor- A2 sectors
 
 
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0005 | OSL     | ARN     | 15JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0006 | ARN     | OSL     | 15JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 3 is assigned to crew member 1 in position FC
  Given trip 3 is assigned to crew member 3 in position FP

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 16JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0008 | ARN     | OSL     | 16JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 4 is assigned to crew member 1 in position FC
  Given trip 4 is assigned to crew member 3 in position FP

    Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 17JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0008 | ARN     | OSL     | 17JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 5 is assigned to crew member 4 in position FC
  Given trip 5 is assigned to crew member 3 in position FP

  Given table accumulator_int additionally contains the following
  | name                                      | acckey       | tim             | val  |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 3    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 5    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 31DEC2020 00:00 | 11   |


  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "8" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%number_of_active_sectors_on_max_days_pilot2%" shall be "0" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%next_sectors_with_instructor_pilot2%" shall be "0" on leg 1 on trip 3 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 3 on roster 1


   @SCENARIO_12
  Scenario: One of the crew is recent, but immediate next two sectors are planned after 14 days with instructor- A2 sectors
 
 
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0005 | OSL     | ARN     | 15JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0006 | ARN     | OSL     | 15JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 3 is assigned to crew member 1 in position FC
  Given trip 3 is assigned to crew member 3 in position FP

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 30JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0008 | ARN     | OSL     | 30JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 4 is assigned to crew member 4 in position FC
  Given trip 4 is assigned to crew member 3 in position FP

    Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0007 | OSL     | ARN     | 31JAN2021 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0008 | ARN     | OSL     | 31JAN2021 | 12:00 | 13:00 | SK  | 320    |
  Given trip 5 is assigned to crew member 4 in position FC
  Given trip 5 is assigned to crew member 3 in position FP

  Given table accumulator_int additionally contains the following
  | name                                      | acckey       | tim             | val  |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 12DEC2020 00:00 | 3    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 5    |
  | accumulators.a2_flights_sectors_daily_acc | Crew001      | 31DEC2020 00:00 | 11   |


  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors%" shall be "8" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg%" shall be "1" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%number_of_active_sectors_on_max_days_pilot2%" shall be "0" on leg 1 on trip 3 on roster 1
  and rave "rules_training_ccr.%next_sectors_with_instructor_pilot2%" shall be "0" on leg 1 on trip 3 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_sh" shall fail on leg 1 on trip 3 on roster 1