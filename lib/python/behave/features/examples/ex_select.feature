@skip
Feature: Example select, create trips and select
	 requires the variable studio_sno.%num_marked_trips% to be defined as:
	 studio_sno.%num_marked_trips% = count(trip_set) where (%trip_is_marked%);

  Background: setup planning period
    Given planning period from 1JUL2003 to 30JUL2003

  Scenario: Create two legs and select on Rave variable
    Given a "leg" that departs at 10:00
    and another "leg" that departs from "ARN" at 10:00
    When I show "leg sets" in window 1
    and prettyprint
    and I select "leg sets" where rave "leg.%start_utc%" is "6jul2003 10:00" in window 1
    Then there shall be 2 selected "leg sets"

  Scenario: Create two trips with and select on Rave variable

    Given a trip
    and the trip has a "leg" that departs from "GOT"
    and the trip has a "dh" that arrives at "ARR"
    and the trip has a "leg"
    and the trip has a "dh"
    Given another trip with homebase "ARN" with the following activities
    | act | dep   | arr   | dep stn | arr stn |
    | leg | 8:00  | 10:00 | ARN     | GOT     |
    | dh  | 10:46 | 12:00 | GOT     | OSL     |
    | leg | 13:00 | 14:00 | OSL     | ARN     |
    When I show "trips" in window 1
    Then there shall be 0 selected "trips"
    When I select "trips" where rave "leg.%connection_time%" is "0:46"
    Then there shall be 1 selected "trip"
