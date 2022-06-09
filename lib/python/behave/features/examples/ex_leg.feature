@skip
Feature: Example, data setup leg

  Background: setup planning period
    Given planning period from 1JUL2003 to 30JUL2003

  Scenario: Create legs that are not assigned to any trip

    Given a "leg"
    Given another "leg"
    Given a "leg" that departs at 10:00
    Given a "leg" that arrives at 12:00
    Given a "leg" that departs at 10:00 and arrives at 12:00
    Given a "leg" that departs from "DEP"
    Given a "leg" that arrives at "ARR"
    Given a "leg" that departs from "DEP" at 14:00
    Given a "leg" that arrives at "ARR" at 16:00
    and leg 5 has onward flight leg 6
    When I show "leg sets" in window 1
    Then there shall be 9 rows

  Scenario: Create legs from a table

    Given the following activities
    | act | num  | dep stn | arr stn | dep   | arr   |
    | leg | 7511 |         | ARR     | 10:25 | 11:35 |
    | leg |      |         |         | 12:25 |       |
    | leg |      |         |         | 12:25 |       |
    | leg |      |         |         |       | 17:00 |
    When I show "leg sets" in window 1
    Then there shall be 4 rows

 Scenario: Create legs on specific dates

    Given a "leg" that departs at 10:00
    given a "leg" that departs at 9Jul2003
    given a "leg" that departs at 9Jul2003 12:00
    Given a "leg" that arrives at 14:00
    given a "leg" that arrives at 11Jul2003
    given a "leg" that arrives at 11Jul2003 14:00
    When I show "leg sets" in window 1
    Then there shall be 6 rows

