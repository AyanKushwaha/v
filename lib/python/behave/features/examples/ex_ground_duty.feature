@skip
Feature: Example, data setup ground duty

  Background: set up for pairing
    Given Tracking
    Given planning period from 1JUL2018 to 30JUL2018

  Scenario: Create ground duties from table

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 07JUL2018 | 10:00 | 11:00 |

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |

    Given trip 1 is assigned to crew member 1
    When I show "crew" in window 1
    Then rave "leg.%code%" shall be "Z2" on leg 1 on trip 1 on roster 1
    and rave "leg.%start_utc%" shall be "07JUL2018 10:00"
    and rave "leg.%end_utc%" shall be "07JUL2018 11:00"
