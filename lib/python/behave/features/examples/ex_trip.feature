@skip
Feature: Example, data setup trip

  Background: set up for pairing
    Given JCP
    Given planning period from 1JUL2003 to 30JUL2003

  Scenario: Create trips with legs

    Given a trip
    and the trip has a "leg"
    and the trip has another "leg"
    and the trip has a "leg" that departs from "GOT"
    and the trip has a "leg" that arrives at "ARR"
    Given another trip with homebase "ARN"
    and the trip has a "leg"
    and the trip has a "leg" that departs from "ARN" at 10:00
    and the trip has a "leg" that arrives at "ARR" at 16:00
    When I show "trips" in window 1
    Then there shall be 2 rows

  # Scenario: Create trips with dhs

  #   Given a trip
  #   and the trip has a "dh"
  #   and the trip has another "dh"
  #   and the trip has a "dh" that departs from "GOT"
  #   and the trip has a "dh" that arrives at "ARR"
  #   Given another trip with homebase "ARN"
  #   and the trip has a "dh"
  #   and the trip has a "dh" that departs from "ARN" at 10:00
  #   and the trip has a "dh" that arrives at "ARR" at 16:00
  #   When I show "trips" in window 1
  #   Then there shall be 2 rows

  Scenario: Create more trips

    Given a trip
    and the trip has a "leg" that departs at 10:00
    and the trip has a "leg" that arrives at 12:05
    Given another trip
    and the trip has a "leg" that arrives at "ARN" at 12:00
    and the trip has a "leg" that departs from "ARN" at 12:05
    When I show "trips" in window 1
    Then there shall be 2 rows

  # Scenario: Create a trip from an activity table
  # ac type col missing, use default values

  #   Given a trip with the following activities
  #   | act | num  | dep stn | arr stn | dep   | arr   |
  #   | leg | 7511 |         | ARR     | 10:25 | 11:35 |
  #   | leg |      |         |         | 12:25 |       |
  #   Given a trip with homebase "GOT" with the following activities
  #   | act | num  | dep stn | arr stn | dep   | arr   |
  #   | leg | 7511 |         | ARR     | 10:25 | 11:35 |
  #   | leg |      |         |         | 12:25 |       |
  #   When I show "trips" in window 1
  #   Then there shall be 2 rows

  Scenario: Create trips on specific dates

    Given a trip with homebase "GOT"
    given the trip has a "leg" that departs at 10:00
    and the trip has a "leg" that departs at 9Jul2003
    and the trip has a "leg" that departs at 9Jul2003 10:00
    given the trip has a "leg" that arrives at 14:00
    given the trip has a "leg" that arrives at 11Jul2003
    given the trip has a "leg" that arrives at 11Jul2003 16:30
    When I show "trips" in window 1
    Then there shall be 1 row