@TRACKING @JCRT @FD @RECENCY
Feature: Test the rule rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH

##############################################################################
  Background: Setup common data
    Given planning period from 1JAN2021 to 1FEB2021

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 27NOV2020  | 09DEC2022 |
           | base            | CPH        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FC         | 01DEC2020  | 31DEC2035 |
           | contract        | V131-LH     | 28SEP2020  | 08JAN2022 |

    Given crew member 1 has qualification "ACQUAL+A3" from 28SEP2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 11NOV1996 to 31DEC2035

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 27NOV2020  | 09DEC2022 |
           | base            | CPH        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FP         | 01DEC2020  | 31DEC2035 |
           | contract        | V131-LH     | 28SEP2020  | 08JAN2022 |

    Given crew member 2 has qualification "ACQUAL+A3" from 28SEP2020 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 11NOV1996 to 31DEC2035

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | region          | SKD        | 27NOV2020  | 09DEC2022 |
           | base            | CPH        | 27NOV2020  | 09DEC2022 |
           | crew rank       | FP         | 01DEC2020  | 31DEC2035 |
           | contract        | V131-LH     | 28SEP2020  | 08JAN2022 |

    Given crew member 3 has qualification "ACQUAL+A3" from 28SEP2020 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A5" from 11NOV1996 to 31DEC2035
    Given crew member 3 has document "REC+PCA3A5" from 20DEC2020 to 1JUN2021

    Given table agreement_validity additionally contains the following
        | id                       | validfrom      | validto    |
        | min_sectors_in_max_days_lh  | 01JAN2021      | 31DEC2035  |
    
   
##############################################################################


  @SCENARIO_1
  Scenario: All crew unrecent

   Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
    | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
    Given trip 1 is assigned to crew member 1 in position FC
    Given trip 1 is assigned to crew member 2 in position FP
    Given trip 1 is assigned to crew member 3 in position FR

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
    | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
    Given trip 2 is assigned to crew member 1 in position FC
    Given trip 2 is assigned to crew member 2 in position FP
    Given trip 2 is assigned to crew member 3 in position FR

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%total_nr_of_sectors_lh%" shall be "1" on leg 2 on trip 1 on roster 1
  and rave "recency.%total_nr_of_sectors_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "0" on leg 2 on trip 1 on roster 2  
  and rave "rules_training_ccr.%nr_unrecent_crew_in_leg_lh%" shall be "3" on leg 2 on trip 1 on roster 2  
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "1" on leg 2 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "1" on leg 2 on trip 1 on roster 2  
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_LH_failtext%" shall be "Min sectors 1 [4] in last 35 days, must fly with recent" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall fail on leg 2 on trip 1 on roster 2

  @SCENARIO_2
  Scenario: One crew recent - A5 sectors
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP
  Given trip 1 is assigned to crew member 3 in position FR

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP
  Given trip 2 is assigned to crew member 3 in position FR

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew001      | 23DEC2020 00:00 | 4    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "3" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "4" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_unrecent_crew_in_leg_lh%" shall be "2" on leg 2 on trip 1 on roster 2  
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_LH_failtext%" shall be "Min sectors 1 [4] in last 45 days, must fly with recent" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall fail on leg 2 on trip 1 on roster 2


  @SCENARIO_3
  Scenario: One crew recent - with simulator
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP
  Given trip 1 is assigned to crew member 3 in position FR

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP
  Given trip 2 is assigned to crew member 3 in position FR

  Given table accumulator_int is overridden with the following
   | name                               | acckey     | tim             | val  |
   | accumulators.sim_sectors_daily_acc | Crew001    | 20DEC2020 00:00 | 1    |
   | accumulators.sim_sectors_daily_acc | Crew001    | 23DEC2020 00:00 | 3    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "5" on leg 2 on trip 1 on roster 1
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_unrecent_crew_in_leg_lh%" shall be "2" on leg 2 on trip 1 on roster 2  
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_LH_failtext%" shall be "Min sectors 1 [4] in last 45 days, must fly with recent" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall fail on leg 2 on trip 1 on roster 2


  @SCENARIO_4
  Scenario: One crew recent - qual A3A5 sectors

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP
  Given trip 1 is assigned to crew member 3 in position FR

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP
  Given trip 2 is assigned to crew member 3 in position FR

  Given table accumulator_int is overridden with the following
   | name                                       | acckey     | tim             | val  |
   | accumulators.a3_flights_sectors_daily_acc  | Crew001    | 20DEC2020 00:00 | 1    |
   | accumulators.a3_flights_sectors_daily_acc  | Crew001    | 23DEC2020 00:00 | 3    |
   | accumulators.a5_flights_sectors_daily_acc  | Crew002    | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc  | Crew002    | 23DEC2020 00:00 | 5    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 1 on trip 1 on roster 2
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "5" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_unrecent_crew_in_leg_lh%" shall be "2" on leg 2 on trip 1 on roster 2  
  and rave "rules_training_ccr.%qln_min_sectors_in_max_days_recency_FC_LH_failtext%" shall be "Min sectors 3 [4] in last 45 days, must fly with recent" on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall fail on leg 2 on trip 1 on roster 1


@SCENARIO_5
  Scenario: Two crew recent - A5 sectors

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP
  Given trip 1 is assigned to crew member 3 in position FR

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP
  Given trip 2 is assigned to crew member 3 in position FR

  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew001      | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew001      | 23DEC2020 00:00 | 4    |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 23DEC2020 00:00 | 4    |
  
   Given table accumulator_time additionally contains the following
    | name                           | acckey        | tim       | filt |
    | accumulators.last_landing_a350 | crew member 3 | 25Dec2020 |      |

  Given table aircraft_type additionally contains the following
      | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc |
      | 35X | A350     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |

  Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 3 | ASF     | A5   | 12Jan2021 10:22 |
      | crew member 3 | ASF     | A5   | 12Jan2021 12:22 |
  
  Given table crew_training_need additionally contains the following
    | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
    | crew member 3 | 1    | 1FEB2020  | 31JAN2021 | CTR-A3A5 | FAM FLT   | 2       | 21       | A5     |            |

  Given crew member 3 has a personal activity "K5" at station "CPH" that starts at 02JAN2021 08:00 and ends at 02JAN2021 18:30

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "3" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "3" on leg 1 on trip 1 on roster 2
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 2 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "4" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "2" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_unrecent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2  
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 2 on roster 3


@SCENARIO_6
  Scenario: One crew recent with sim sectors and one crew recent with A5 sectors

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP
  Given trip 1 is assigned to crew member 3 in position FR

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP
  Given trip 2 is assigned to crew member 3 in position FR

  Given table accumulator_int is overridden with the following
   | name                               | acckey     | tim             | val  |
   | accumulators.sim_sectors_daily_acc | Crew001    | 20DEC2020 00:00 | 1    |
   | accumulators.sim_sectors_daily_acc | Crew001    | 23DEC2020 00:00 | 3    |
  
  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 23DEC2020 00:00 | 4    |
  
   Given table accumulator_time additionally contains the following
    | name                           | acckey        | tim       | filt |
    | accumulators.last_landing_a350 | crew member 3 | 25Dec2020 |      |

  Given table aircraft_type additionally contains the following
      | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc |
      | 35X | A350     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |

  Given table crew_training_log additionally contains the following
      | crew          | typ     | code | tim             |
      | crew member 3 | ASF     | A5   | 12Jan2021 10:22 |
      | crew member 3 | ASF     | A5   | 12Jan2021 12:22 |
  
  Given table crew_training_need additionally contains the following
    | crew          | part | validfrom | validto   | course   | attribute | flights | maxdays | acqual | completion |
    | crew member 3 | 1    | 1FEB2020  | 31JAN2021 | CTR-A3A5 | FAM FLT   | 2       | 21       | A5     |            |
 
  Given crew member 3 has a personal activity "K5" at station "CPH" that starts at 02JAN2021 08:00 and ends at 02JAN2021 18:30

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "3" on leg 1 on trip 1 on roster 2
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "5" on leg 2 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "4" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "2" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 2 on roster 3

@SCENARIO_7
  Scenario: One crew recent in 35 days and other crew recent in 45 days with A5 sectors

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP

  Given table accumulator_int is overridden with the following
   | name                               | acckey     | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew001    | 20DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew001    | 23DEC2020 00:00 | 4    |
  
  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 04DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 06DEC2020 00:00 | 4    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "3" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "3" on leg 1 on trip 1 on roster 2
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 2 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "4" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 2

  @SCENARIO_8
  Scenario: One crew recent in 35 days with simulator and other crew recent in 45 days with A5 sectors

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 15Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 17Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 1 is assigned to crew member 1 in position FC
  Given trip 1 is assigned to crew member 2 in position FP

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | CPH     | SFO     | 25Jan2021 | 10:25 | 21:45 | SK  |  35A   |
  | leg | 0002 | SFO     | CPH     | 27Jan2021 | 00:35 | 11:15 | SK  |  35A   |
  Given trip 2 is assigned to crew member 1 in position FC
  Given trip 2 is assigned to crew member 2 in position FP

  Given table accumulator_int is overridden with the following
   | name                               | acckey     | tim             | val  |
   | accumulators.sim_sectors_daily_acc | Crew001    | 20DEC2020 00:00 | 1    |
   | accumulators.sim_sectors_daily_acc | Crew001    | 23DEC2020 00:00 | 3    |
  
  Given table accumulator_int additionally contains the following
   | name                                      | acckey       | tim             | val  |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 04DEC2020 00:00 | 1    |
   | accumulators.a5_flights_sectors_daily_acc | Crew002      | 06DEC2020 00:00 | 4    |

  When I show "crew" in window 1
  and I load rule set "Tracking"
  Then rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "4" on leg 1 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "3" on leg 1 on trip 1 on roster 2
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot1%" shall be "5" on leg 2 on trip 1 on roster 1
  and rave "recency.%number_of_active_sectors_on_max_days_lh_pilot2%" shall be "4" on leg 2 on trip 1 on roster 2
  and rave "rules_training_ccr.%nr_recent_crew_in_leg_lh%" shall be "1" on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.qln_min_sectors_in_max_days_recency_FC_LH" shall pass on leg 2 on trip 1 on roster 2
