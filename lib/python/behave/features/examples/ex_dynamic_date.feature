@skip
Feature: Example, dynamic dates (month and year)

  Background: setup planning period
    Given dynamic planning period for this month
    Given Tracking

    Scenario: Create dynamic trips
      Given a trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
      | leg | 0001 | OSL     | GZP     | 01FEBTHIS | 10:00 | 11:00 | SK  | A2     |

      Given another trip with the following activities
      | act | num  | dep stn | arr stn | date   | dep   | arr   | car |
      | leg | 0002 | OSL     | LHR     | 05THIS | 10:00 | 11:00 | SK  |
      | leg | 0003 | LHR     | OSL     | 05THIS | 12:00 | 13:00 | SK  |

      When I show "trips" in window 1
      Then there shall be 1 rows