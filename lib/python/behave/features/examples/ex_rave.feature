@skip
Feature: Example, rave tests

 Background: setup planning period
     Given planning period from 1JAN2018 to 31JAN2018

 Scenario: Create 2 legs, verify rave vars

    Create a trip with two specific legs, verify leg connection rule

    Given a trip
    and the trip has a "leg" that arrives at 10:00
    and the trip has another "leg" that departs at 10:46
    Given another trip
    and the trip has a "leg" that arrives at 11:00
    and the trip has another "leg" that departs at 11:47
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    and prettyprint
    Then rave "leg.%connection_time%" shall be "0:46" on leg 1 on trip 1
    and rave "leg.%start_od_utc%" shall be "9:00"
    and rave "leg.%start_od_utc%" shall be "10:46" on leg 2
    Then rave "leg.%start_od_utc%" shall be "11:47" on leg 2 on trip 2


  Scenario: Create 2 legs, verify rave vars 2

    Create a trip with two specific legs, verify leg connection rule

    Given a trip
    and the trip has a "leg" that departs at 9:42
    and the trip has another "leg" that arrives at 13:47
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    and prettyprint
    Then rave "leg.%start_od_utc%" shall be "9:42" on leg 1 on trip 1
    and rave "leg.%end_od_utc%" shall be "13:47" on leg 2


  Scenario: Check that leg.start_utc can be read

    Create a trip with two specific legs, verify leg connection rule

    Given a trip
    and the trip has a "leg" that departs at 9:42
    and the trip has another "leg" that arrives at 13:47
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    and prettyprint
    Then rave "leg.%start_od_utc%" shall be "9:42" on leg 1 on trip 1
    and rave "leg.%end_od_utc%" shall be "13:47" on leg 2


  Scenario: Check that leg.start_hb can be read

    Create a trip with two specific legs, verify leg connection rule

    Given a trip
    and the trip has a "leg" that departs at 8:42
    and the trip has another "leg" that arrives at 12:47
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    and prettyprint
    Then rave "leg.%start_od%" shall be "9:42" on leg 1 on trip 1
    and rave "leg.%end_od%" shall be "13:47" on leg 2


