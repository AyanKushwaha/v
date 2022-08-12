Feature: Training code attributes should be assignable on duty codes starting with OL

  @SCENARIO_1 @tracking @OLOCRC
  Scenario: Training attributes should be assignable to duty OLOCRC
    Given Tracking
    Given planning period from 1DEC2019 to 28DEC2019
    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |
    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLOCRC | ARN | 26DEC2019  | 26DEC2019 | 12:00    |
     
     When I show "crew" in window 1
     Then rave "leg.%can_have_attribute_assigned%" shall be "True" on leg 1 on trip 1 on roster 1
     Then rave "leg.%is_cc_inst_activity_ntc17%" shall be "True" on leg 1 on trip 1 on roster 1
     Then rave "leg.%can_have_attribute%" shall be "True" on leg 1 on trip 1 on roster 1

  @SCENARIO_2 @tracking @OLI2C
  Scenario: Training attributes should be assignable to duty OLI2C
    Given Tracking
    Given planning period from 1DEC2019 to 28DEC2019
    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |
    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLI2C | ARN | 26DEC2019  | 26DEC2019 | 12:00    |
     
     When I show "crew" in window 1
     Then rave "leg.%can_have_attribute_assigned%" shall be "True" on leg 1 on trip 1 on roster 1
     Then rave "leg.%is_cc_inst_activity_ntc17%" shall be "True" on leg 1 on trip 1 on roster 1
     Then rave "leg.%can_have_attribute%" shall be "True" on leg 1 on trip 1 on roster 1
