@skip
Feature: Example core menus, simple menu entries

  Scenario: Create one trip and split it

    Given a trip
    and the trip has a "leg"
    and the trip has another "leg"
    When I show "trips" in window 1
    and I select leg 1
    and I Split after
    Then there shall be 2 rows

 Scenario: Create one trip and toggle first leg to DH

    Given a trip
    and the trip has a "leg"
    and the trip has another "leg"
    When I show "trips" in window 1
    and I select leg 1
    and I Change to/from Deadhead
    Then rave "deadhead" shall be "True"
    
 # Scenario: Create one trip and toggle first leg to DH

 #    Given a trip
 #    and the trip has a "leg"
 #    and the trip has another "leg"
 #    When I show "trips" in window 1
 #    and I select trip 1
 #    and I Slice Completely
 #    Then there shall be 2 rows

    