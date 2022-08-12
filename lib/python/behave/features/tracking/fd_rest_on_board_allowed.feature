@tracking @oma16 @FC
Feature: Rest on board allowed should use the number of assigned flight deck crew members for tracking, when evaluating
         the max FDP limit.

   Background: Number of booked FD crew does not always equal the number of assigned FD crews in tracking. Use the number of assigned FD crew when evaluating the max FDP instead of the number of booked FD crew



  ###################################################################################

@tracking @oma16 @FC @TC1
    Scenario: Check that the calculation of max FDP allowed limit is evaluated correctly based on
        The number of assigned FD crews (FD crew = FC + FP + FR)
        Rest on board is allowed
        The flight is longhaul
        Rest facility exist on the aircraft
        Relief pilot on board
        Number of extra flight deck crew = 1

    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FP        |            |          |
    | region          | SKS       |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FR        |            |          |
    | region          | SKS       |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | HKG     | 13OCT2018 | 10:00 | 23:30 | SK  | 33R    |
    | leg | 0002 | HKG     | CPH     | 15OCT2018 | 10:00 | 23:30 | SK  | 33R    |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 1 is assigned to crew member 2 in position FP
    and trip 1 is assigned to crew member 3 in position FR
    When I show "crew" in window 1
    Then rave "trip.%is_long_haul%" shall be "True"
    and rave "crew_pos.%number_of_booked_flight_deck_crew%" shall be "3" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_on_board_allowed%" shall be "True" on leg 1 on trip 1 on roster 3
    and rave "Oma16.%max_daily_fdp%" shall be "17:00" on leg 1 on trip 1 on roster 1
    and rave "Oma16.%max_daily_fdp%" shall be "17:00" on leg 1 on trip 1 on roster 2
    and rave "Oma16.%max_daily_fdp%" shall be "17:00" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_time_sufficient_on_leg_fd%" shall be "True" on leg 1 on trip 1 on roster 3
    and rave "oma16.%number_of_extra_flight_deck_crew%" shall be "1" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_facilities_exists_fd%" shall be "True" on leg 1 on trip 1 on roster 3
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall pass on leg 1 on trip 1 on roster 3

  ###################################################################################

@tracking @oma16 @FC @TC2
    Scenario: Check that the calculation of max FDP allowed limit is evaluated correctly based on
        The number of assigned FD crews (FD crew = FC + FP + FR)
        Rest on board is not allowed
        The flight is longhaul
        Rest facility does not exist on the aircraft
        Relief pilot on board
        Number of extra flight deck crew = 1

    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKS       |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FP        |            |          |
    | region          | SKS       |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FR        |            |          |
    | region          | SKS       |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | HKG     | 13OCT2018 | 10:00 | 23:30 | SK  | 330    |
    | leg | 0002 | HKG     | CPH     | 15OCT2018 | 10:00 | 23:30 | SK  | 330    |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 1 is assigned to crew member 2 in position FP
    and trip 1 is assigned to crew member 3 in position FR
    When I show "crew" in window 1
    Then rave "trip.%is_long_haul%" shall be "True"
    and rave "crew_pos.%number_of_booked_flight_deck_crew%" shall be "3" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_on_board_allowed%" shall be "False" on leg 1 on trip 1 on roster 1
    and rave "oma16.%rest_on_board_allowed%" shall be "False" on leg 1 on trip 1 on roster 2
    and rave "oma16.%rest_on_board_allowed%" shall be "False" on leg 1 on trip 1 on roster 3
    and rave "duty_period.%is_fdp%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "Oma16.%max_daily_fdp%" shall be "14:00" on leg 1 on trip 1 on roster 1
    and rave "Oma16.%max_daily_fdp%" shall be "14:00" on leg 1 on trip 1 on roster 2
    and rave "Oma16.%max_daily_fdp%" shall be "14:00" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_time_sufficient_on_leg_fd%" shall be "True" on leg 1 on trip 1 on roster 3
    and rave "oma16.%number_of_extra_flight_deck_crew%" shall be "1" on leg 1 on trip 1 on roster 3
    and rave "oma16.%rest_facilities_exists_fd%" shall be "False" on leg 1 on trip 1 on roster 3
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall fail on leg 1 on trip 1 on roster 2
    and the rule "rules_caa_common.caa_oma16_max_duty_in_fdp_ALL" shall fail on leg 1 on trip 1 on roster 3

  ###################################################################################




