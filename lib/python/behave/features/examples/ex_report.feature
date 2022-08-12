@skip
Feature: Generate Reports

  Background:
    Given Tracking

  Scenario: run a report and verify outpout

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | dep   | arr   |
    | leg | 7511 |         | ARR     | 10:25 | 11:35 |
    | leg |      |         |         | 12:25 |       |
    | dh  |      |         |         | 15:45 | 16:10 |
    When I show "trips" in window 1
    and I select trip 1
    and I generate report "include/LegalityInfo.py"
    Then the report shall contain a line with "Roster is" and "legal"
