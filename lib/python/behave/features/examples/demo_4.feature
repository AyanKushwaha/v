@skip
Feature: Demo 4, advanced data setup

  Scenario: Create 2 legs, 1:01 check leg cxn

    Create a trip with two specific legs, verify leg connection rule

    Given a trip
    and the trip has a "leg" that arrives at 10:00
    and the trip has another "leg" that departs at 11:01
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    Then rave "leg.%connection_time%" shall be "1:01" on leg 1 on trip 1

  Scenario: Create 2 legs, 0:46 cxn, check leg cxn rule

    Create a trip with two specific legs, verify failed leg connection rule

    Given a trip
    and the trip has a "leg" that arrives at 10:00
    and the trip has another "leg" that departs at 10:46
    When I show "trips" in window 1
    and I load rule set "rule_set_jcp"
    Then rave "leg.%connection_time%" shall be "0:46" on leg 1 on trip 1
