Feature: Check that correct document end are shown in info window
  Background: Set up common data

    Given a crew member with
      | attribute  | value |
      | crew rank  | FC    |
      | title rank | FC    |
      | region     | SKS   |
      | base       | STO   |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2019 to 31DEC2035

  @SCENARIO_1 @tracking
  Scenario: Check that earliest document end is shown when now is before pp
    Given planning period from 1NOV2019 to 30NOV2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1
    and I load rule set "Tracking"

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "10NOV2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec19" on roster 1


  @SCENARIO_2 @tracking
  Scenario: Check that earliest document end is shown when now is before document end
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1DEC2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec19" on roster 1


  @SCENARIO_3 @tracking
  Scenario: Check that latest document end is shown when now is at document end
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "10DEC2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec20" on roster 1


  @SCENARIO_4 @tracking
  Scenario: Check that latest document end is shown when now is after document end
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "11DEC2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec20" on roster 1


  @SCENARIO_5 @tracking
  Scenario: Check that latest document end is shown when now is at pp end
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "31DEC2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec20" on roster 1


  @SCENARIO_6 @tracking
  Scenario: Check that latest document end is shown when now is after document end
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 10DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 10DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "1JAN2020 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec20" on roster 1


  @SCENARIO_7 @tracking
  Scenario: Check that latest document end is shown when whole pp is overlapped
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019
    
    Given crew member 1 has document "REC+LC" from 1FEB2019 to 1JAN2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 1DEC2019 to 10DEC2020 and has qualification "A2"

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "10DEC2019 00:00"
    Then rave "training.%expiry_month_lc%" shall be "Dec20" on roster 1


  @SCENARIO_8 @tracking
    Scenario: Check all kinds of documents before training, (unrealistic scenario since document is created at time of course)
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019

    Given crew member 1 has document "REC+PGT" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+PGT" from 16DEC2019 to 30DEC2020
    Given crew member 1 has document "REC+PC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+PC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+CRM" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+CRM" from 16DEC2019 to 30DEC2020

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "10DEC2019 00:00"
    Then rave "crg_info.%training_row1%" shall be "PGT: Dec19 CRM: Dec19" on roster 1
    and rave "crg_info.%training_row2%" shall be " PC: Dec19" on roster 1
    and rave "crg_info.%training_row3%" shall be "OPC: Dec19" on roster 1
    and rave "crg_info.%training_row4%" shall be " LC: Dec19 " on roster 1

  @SCENARIO_9 @tracking
    Scenario: Check all kinds of documents after training, (unrealistic scenario since document is created at time of course)
    Given Tracking
    Given planning period from 1DEC2019 to 31DEC2019

    Given crew member 1 has document "REC+PGT" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+PGT" from 16DEC2019 to 30DEC2020
    Given crew member 1 has document "REC+PC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+PC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+CRM" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+CRM" from 16DEC2019 to 30DEC2020

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "16DEC2019 00:01"
    Then rave "crg_info.%training_row1%" shall be "PGT: Dec20 CRM: Dec20" on roster 1
    and rave "crg_info.%training_row2%" shall be " PC: Dec20" on roster 1
    and rave "crg_info.%training_row3%" shall be "OPC: Dec20" on roster 1
    and rave "crg_info.%training_row4%" shall be " LC: Dec20 " on roster 1

  @SCENARIO_10 @planning
    Scenario: Checking that it works in planning studio as well
    Given Rostering_FC
    Given planning period from 1DEC2019 to 31DEC2019

    Given crew member 1 has document "REC+PGT" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+PGT" from 16DEC2019 to 30DEC2020
    Given crew member 1 has document "REC+PC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+PC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+OPC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 15DEC2018 to 15DEC2019 and has qualification "A2"
    Given crew member 1 has document "REC+LC" from 16DEC2019 to 30DEC2020 and has qualification "A2"
    Given crew member 1 has document "REC+CRM" from 15DEC2018 to 15DEC2019
    Given crew member 1 has document "REC+CRM" from 16DEC2019 to 30DEC2020

    When I show "crew" in window 1

    When I set parameter "fundamental.%use_now_debug%" to "TRUE"
    When I set parameter "fundamental.%now_debug%" to "16DEC2019 00:01"
    Then rave "base_product.%is_rostering%" shall be "True" on roster 1
    and rave "crg_info.%training_row1%" shall be "PGT: Dec20 CRM: Dec20" on roster 1
    and rave "crg_info.%training_row2%" shall be " PC: Dec20" on roster 1
    and rave "crg_info.%training_row3%" shall be "OPC: Dec20" on roster 1
    and rave "crg_info.%training_row4%" shall be " LC: Dec20 " on roster 1