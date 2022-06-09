@sks @cc @tracking
Feature: Tests for ensuring actual duty time is reported in new SCHEDULECCSE report

  Background:
    Given Tracking

  #############################################################
  Scenario: Actual duty time is reported on short work day
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | STO     |             |           |
  | title rank | CC      |             |           |
  | region     | SKS     |             |           |
  Given crew member 1 has contract "F00428"
  
  
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | ARN     | LHR     | 14MAY2019 | 10:00 | 11:00 | SK  | 320    |
  | leg | 0002 | LHR     | ARN     | 14MAY2019 | 12:00 | 13:00 | SK  | 320    |
  
  Given trip 1 is assigned to crew member 1
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "4:20" on leg 1 on trip 1 on roster 1
  ##############################################################
  Scenario: Actual duty time is reported on long work day
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F00428"
  
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | ARN     | LHR     | 14MAY2019 | 06:00 | 11:00 | SK  | 320    |
  | leg | 0002 | LHR     | ARN     | 14MAY2019 | 12:00 | 19:00 | SK  | 320    |
  
  Given trip 1 is assigned to crew member 1
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "14:20" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Duty reported for rehab contracts IL8
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F00640"
  
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | ARN     | LHR     | 14MAY2019 | 06:00 | 11:00 | SK  | 320    |
  | leg | 0002 | LHR     | ARN     | 14MAY2019 | 12:00 | 19:00 | SK  | 320    |
  
  Given trip 1 is assigned to crew member 1
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "14:20" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: No duty reported for non SKS crew
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | OSL   |
  | title rank | CC    |
  | region     | SKN   |
  Given crew member 1 has contract "F00648"
  
  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0001 | OSL     | LHR     | 14MAY2019 | 06:00 | 11:00 | SK  | 320    |
  | leg | 0002 | LHR     | OSL     | 14MAY2019 | 12:00 | 19:00 | SK  | 320    |
  
  Given trip 1 is assigned to crew member 1
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "0:00" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 100% contract
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "V00863"
  
  Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "5:27" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 80% contract
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F00428"
  
  Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "4:22" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 75% contract
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F10"
  
  Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "4:05" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 60% contract
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F00429"
  
  Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "3:16" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 50% contract
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "F15"
  
  Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "2:44" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 100% contract VA1
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "V00863"
  
  Given crew member 1 has a personal activity "VA1" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "5:27" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 100% contract F7
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "V00863"
  
  Given crew member 1 has a personal activity "F7" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "5:27" on leg 1 on trip 1 on roster 1
  ###############################################################  
  Scenario: Fixed hours reported on vacation 100% contract on blank days
  
  Given planning period from 1MAY2019 to 31MAY2019
  
  Given a crew member with
  | attribute  | value |
  | base       | STO   |
  | title rank | CC    |
  | region     | SKS   |
  Given crew member 1 has contract "V00863"
  
  Given crew member 1 has a personal activity "BL" at station "ARN" that starts at 13MAY2019 22:00 and ends at 14MAY2019 22:00
  
  When I show "crew" in window 1
  Then rave "report_overtime.%crew_calculated_duty_hours%(14MAY2019)" shall be "7:38" on leg 1 on trip 1 on roster 1
  