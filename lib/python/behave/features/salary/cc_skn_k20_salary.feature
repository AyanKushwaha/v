Feature: K20 SKN CC Salary: Remove Public Holiday per diem. Crew should instead get 1500 NOK/ day


 Background: Set up k20_skn_cc_no_ph_perdiem in  agreement_validity table
    Given Tracking
    
    Given table agreement_validity is overridden with the following
      | id                                  | validfrom | validto   |
      | k20_skn_cc_no_ph_perdiem            | 01FEB2021 | 31DEC2035 |

    ############################################################################
    # Scenarios that shall pass
    ############################################################################

        @SCENARIO_1
        Scenario: Norwegian cabin crew should not get doubled perdiem on public holidays
        Given planning period from 1Mar2021 to 31Mar2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKN        | 26NOV2018  | 01JAN2036 |
        | base            | OSL        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
        Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

        Given table account_entry additionally contains the following
	      | id   | crew          | tim      | account | source           | amount | man   |
	      | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | OSL     | ARN     | 28Mar2021 | 10:55 | 11:55 | SK  | 320     |
        | leg | 0002 | ARN     | OSL     | 28Mar2021 | 13:55 | 14:55 | SK  | 320     |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_per_diem_extra%" shall be "0" on leg 1 on trip 1 on roster 1
        


        @SCENARIO_2
        Scenario: Norwegian cabin crew should not get doubled perdiem on public holidays where trip doesn't start on PH but ends on PH
        Given planning period from 1Mar2021 to 31Mar2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKN        | 26NOV2018  | 01JAN2036 |
        | base            | OSL        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given crew member 1 has qualification "ACQUAL+A3" from 26NOV2018 to 01JAN2036
        Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

        Given table account_entry additionally contains the following
	      | id   | crew          | tim      | account | source           | amount | man   |
	      | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        Given a trip with the following activities
         | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | CPH      | 26Mar2021 | 09:00 | 10:10 | SK  | 320    |
        | leg | 0002 | CPH     | SFO      | 26Mar2021 | 11:25 | 22:45 | SK  | 33A    |
        | leg | 0003 | SFO     | CPH      | 28Mar2021 | 01:30 | 12:20 | SK  | 33A    |
        | leg | 0004 | CPH     | OSL      | 28Mar2021 | 13:20 | 14:30 | SK  | 32W    |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_per_diem_extra%" shall be "0,0,0" on leg 4 on trip 1 on roster 1


        @SCENARIO_3
        Scenario: Swedish cabin crew should get extra perdiem on public holidays
        Given planning period from 1Mar2021 to 31Mar2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKS        | 26NOV2018  | 01JAN2036 |
        | base            | ARN        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
        Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

        Given table account_entry additionally contains the following
	      | id   | crew          | tim      | account | source           | amount | man   |
	      | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | ARN     | OSL     | 28Mar2021 | 10:55 | 11:55 | SK  | 320     |
        | leg | 0002 | OSL     | ARN     | 28Mar2021 | 13:55 | 14:55 | SK  | 320     |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_per_diem_extra%" shall be "1" on leg 1 on trip 1 on roster 1


        @SCENARIO_4
        Scenario: Dannish cabin crew should get extra perdiem on public holidays
        Given planning period from 1Mar2021 to 31Mar2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKD        | 26NOV2018  | 01JAN2036 |
        | base            | CPH        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        
        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | CPH     | OSL     | 28Mar2021 | 10:55 | 11:55 | SK  | 320     |
        | leg | 0002 | OSL     | CPH     | 28Mar2021 | 13:55 | 14:55 | SK  | 320     |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_per_diem_extra%" shall be "1" on leg 1 on trip 1 on roster 1

        @SCENARIO_5
        Scenario: Norwegian cabin crew should not get National Holiday compensation for public holidays on sunday
        Given planning period from 1Mar2021 to 31Mar2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKN        | 26NOV2018  | 01JAN2036 |
        | base            | OSL        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given table account_entry additionally contains the following
	      | id   | crew          | tim      | account | source           | amount | man   |
	      | 0001 | crew member 1 | 1JAN2018 | F0      | Entitled F0 days | 100    | False |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ  |
        | leg | 0001 | OSL     | ARN     | 28Mar2021 | 10:55 | 11:55 | SK  | 320     |
        | leg | 0002 | ARN     | OSL     | 28Mar2021 | 13:55 | 14:55 | SK  | 320     |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_extra_compensation_skn_ph%" shall be "0" on leg 1 on trip 1 on roster 1

        @SCENARIO_6
        Scenario: Norwegian cabin crew should get 1500 NOK for each public holiday
        Given planning period from 1Apr2021 to 30Apr2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKN        | 26NOV2018  | 01JAN2036 |
        | base            | OSL        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date     | dep   | arr   | car | ac_typ  |
        | leg | 0001 | OSL     | CDG     | 1Apr2021 | 10:55 | 11:55 | SK  | 320     |
        | leg | 0002 | CDG     | EWR     | 1Apr2021 | 14:55 | 23:35 | SK  | 350     |
        | leg | 0003 | EWR     | CDG     | 2Apr2021 | 12:15 | 18:35 | SK  | 350     |
        | dh  | 0004 | CDG     | OSL     | 3Apr2021 | 09:15 | 11:00 | SK  | 350     |
       
        Given trip 1 is assigned to crew member 1 in position AH

        When I show "crew" in window 1
        Then rave "report_per_diem.%trip_extra_compensation_skn_ph%" shall be "1500,1500,0" on leg 1 on trip 1 on roster 1


        @SCENARIO_7
        Scenario: Norwegian cabin crew should get not get 1500 NOK rescheduled leg
        Given planning period from 1Apr2021 to 30Apr2021

        Given a crew member with
        | attribute       | value      | valid from | valid to  |
        | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
        | region          | SKN        | 26NOV2018  | 01JAN2036 |
        | base            | OSL        | 26NOV2018  | 01JAN2036 |
        | title rank      | AH         | 26NOV2018  | 01JAN2036 |
        | employee number | 48203      |            |           |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | dep            | arr            | car | ac_typ  |
        | leg | 0001 | OSL     | CDG     | 1Apr2021 10:55 | 1Apr2021 11:55 | SK  | 320     |
        | leg | 0002 | CDG     | EWR     | 1Apr2021 14:55 | 1Apr2021 23:35 | SK  | 350     |
        | leg | 0003 | EWR     | CDG     | 2Apr2021 12:15 | 2Apr2021 18:35 | SK  | 350     |
        | leg | 103  | CDG     | OSL     | 3Apr2021 09:15 | 3Apr2021 11:00 | SK  | 350     |
       
        Given trip 1 is assigned to crew member 1 in position AH
        
        Given the roster is published
        When I show "rosters" in window 1
        and I select leg 4
        and I Change to/from Deadhead
        When I reschedule leg 4 of crew member 1 flight 103 to depart from CDG 4Apr2021 09:15 and arrive at OSL 4Apr2021 11:00

        Then rave "report_per_diem.%trip_extra_compensation_skn_ph%" shall be "1500,1500,0,0" on leg 1 on trip 1 on roster 1