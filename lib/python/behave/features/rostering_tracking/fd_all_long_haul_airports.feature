@TRACKING @JCRT @FD
Feature: test airports that initially are not long haul as timezones not bigger than 3

##############################################################################
  Background: Setup common data
        Given planning period from 1JAN2021 to 1FEB2021

        Given a crew member with
        | attribute  | value  |
        | base       | CPH    |
        | title rank | FP     |
        | region     | SKD    |

##############################################################################

    @SCENARIO_1
    Scenario: Test that DBX and GRU are LH airport

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | GRU     | 17JAN2021 | 02:25 | 14:35 | SK  | 359    |
    | leg | 0002 | GRU     | CPH     | 20JAN2021 | 06:35 | 17:45 | SK  | 359    |
    Given trip 1 is assigned to crew member 1 in position FP

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0003 | CPH     | DBX     | 24JAN2021 | 02:25 | 14:35 | SK  | 359    |
    | leg | 0004 | DBX     | CPH     | 28JAN2021 | 06:35 | 17:45 | SK  | 359    |
    Given trip 2 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    and I load rule set "Tracking"
    Then rave "leg.%_is_long_haul%" shall be "True" on leg 1 on trip 1
    and rave "leg.%_is_long_haul%" shall be "True" on leg 1 on trip 2