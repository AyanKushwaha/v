@skip
Feature: Example, data setup crew

  Background: setup planning period
    Given planning period from 1feb2018 to 28feb2018
    Given Rostering_CC

  @SCENARIO1
  Scenario: Create 3 crew members

    Given a crew member
    Given another crew member with homebase "GOT"
    Given another crew member with homebase "ARN"
    When I show "crew" in window 2
    Then there shall be 3 rows


  @SCENARIO2
  Scenario: Create 1 crew member and assign 1 trip

    Given a crew member
    Given another crew member
    Given a trip
    and the trip has a "leg"
    and the trip has another "leg" that departs at 20:00
    Given trip 1 is assigned to crew member 2
    When I show "crew" in window 1
    Then rave "leg.%start_utc%" shall be "06FEB2018 20:00" on leg 2 on trip 1 on roster 2
    and the rule "rules_indust_ccr.ind_min_rest_after_trip_all" shall pass on leg 2 on trip 1 on roster 2


  @SCENARIO3
  Scenario: Create a crew with attributes specified in a table

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | employee number | 56789     |            |          |
    | sex             | M         |            |          |
    | main function   | C         |            |          |
    | base            | ARN       |            | 1JUN2018 |
    | base            | OSL       | 1JUN2018   |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |
    | published       | 01JUL2018 | 01JAN1986  |          |
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | GZP     | 01FEB2018 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | GZP     | OSL     | 01FEB2018 | 12:00 | 13:00 | SK  | A2     |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then rave "crew.%sex%" shall be "M"
    and rave "attributes.%crew_last_published%" shall be "01JUL2018 00:00"
# FIXME: crew_employment?    and rave "crew.%employee_number%" shall be "56789"
# FIXME: where?   and rave "crew.%main_func%" shall be "C"



  @SCENARIO4
  Scenario: Test that crew.employment_date can be set

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       | 1FEB2018   |          |
    | contract        | V00863    | 1FEB2018   |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | STO     | GZP     | 01FEB2018 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | GZP     | STO     | 01FEB2018 | 12:00 | 13:00 | SK  | A2     |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    Then rave "crew.%employment_date%" shall be "01FEB2018 00:00"

