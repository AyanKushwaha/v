@skip
Feature: Example filter, create trips and filter

  # Scenario: Create two trips with and filter on homebase

  #   Given a trip
  #   and the trip has a "leg" that departs from "GOT"
  #   and the trip has a "dh" that arrives at "ARR"
  #   and the trip has a "leg"
  #   and the trip has a "dh"
  #   Given another trip with homebase "ARN" with the following activities
  #   | act | dep   | arr   | dep stn | arr stn |
  #   | leg | 8:00  | 10:00 | ARN     | GOT     |
  #   | dh  | 11:00 | 12:00 | GOT     | OSL     |
  #   | leg | 13:00 | 14:00 | OSL     | ARN     |
  #   When I filter "trips" where homebase is "GOT" in window 1
  #   Then there shall be 1 row

  # Scenario: Create two trips with and filter on Rave variable

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
    When I filter "trips" where rave "leg.%connection_time%" is "0:46" in window 1
    Then there shall be 1 row

  Scenario: Create two trips with and filter on Rave variable

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
    When I toggle the "leg" filter "off"
    and I filter "legs" where rave "arrival_airport_name" is "ARN" in window 1
    Then there shall be 3 rows
