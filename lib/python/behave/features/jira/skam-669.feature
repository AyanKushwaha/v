@tracking
Feature: View block hours (BLH) in right margin of tracking studio

    Background: set up for tracking
    Given Tracking
    Given dynamic planning period for this month

    Scenario: Check that values block hours are correct

      Given a crew member

      Given a trip with the following activities
      | act | num  | dep stn | arr stn | date   | dep   | arr   | car |
      | leg | 0005 | OSL     | LHR     | 05THIS | 10:00 | 11:00 | SK  |
      | leg | 0006 | LHR     | OSL     | 05THIS | 12:00 | 13:00 | SK  |
      Given trip 1 is assigned to crew member 1 in position FC

      When I show "rosters" in window 1
      and I select "trips" where rave "leg.%leg_number%" is "6"
      Then rave "report_common.%block_time_in_full_calendar_year%" shall be "2:00"
