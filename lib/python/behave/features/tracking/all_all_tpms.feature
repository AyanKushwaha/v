@tracking
Feature: Check expressions used in TPMS reports

   Background:
     Given Tracking
     Given planning period from 1DEC2019 to 31DEC2019

   @SCENARIO1 @TPMS @LC
   Scenario: Check qual to update for LC on A330 with no previous document

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2019 | 10:00 | 11:00 | SK  | 33A    |
   | leg | 0002 | LHR     | ARN     | 26DEC2019 | 12:00 | 13:00 | SK  | 33A    |

   Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

   When I show "crew" in window 1

   Then rave "report_tpms.%qual_to_update%" shall be "LC" on leg 1 on trip 1 on roster 1

   @SCENARIO2 @TPMS @LC
   Scenario: Check qual to update for LC on A330 with current LC document for A4

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |

   Given crew member 1 has document "REC+LC" from 1JAN2019 to 31DEC2019 and has qualification "A4"

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2019 | 10:00 | 11:00 | SK  | 33A    |
   | leg | 0002 | LHR     | ARN     | 26DEC2019 | 12:00 | 13:00 | SK  | 33A    |

   Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

   When I show "crew" in window 1

   Then rave "report_tpms.%qual_to_update%" shall be "LC_A4" on leg 1 on trip 1 on roster 1


   @SCENARIO3 @TPMS @LC
   Scenario: Check qual to update for LC on A320 with current LC document for A2

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | crew rank       | FC        |            |          |
    | title rank      | FC        |            |          |

   Given crew member 1 has document "REC+LC" from 1JAN2019 to 31DEC2019 and has qualification "A2"

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 26DEC2019 | 12:00 | 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 26DEC2019 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 26DEC2019 | 12:00 | 13:00 | SK  | 320    |


   Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="LC"

   When I show "crew" in window 1

   Then rave "report_tpms.%qual_to_update%" shall be "LC" on leg 1 on trip 1 on roster 1


   @SCENARIO4 @TPMS @CRMCC
   Scenario: Check that event id is correct for activities CRMC, OLCRMC, OXCRMC

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | AH        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | AH        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | AH        |            |          |


   Given crew member 1 has the following personal activities
     | code   | stn | start_date | end_date  | end_time |
     | CRMCC  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

   Given crew member 2 has the following personal activities
     | code    | stn | start_date | end_date  | end_time |
     | OLCRMC  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

   Given crew member 3 has the following personal activities
     | code    | stn | start_date | end_date  | end_time |
     | OXCRMC  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMCCARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMCCARN26Dec2019" on leg 1 on trip 1 on roster 2
     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMCCARN26Dec2019" on leg 1 on trip 1 on roster 3

   @SCENARIO5 @TPMS @CRMFD
   Scenario: Check that event id is correct for activities CRM, OLCRM, OXCRM

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | CRM  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


    Given crew member 2 has the following personal activities
      | code  | stn | start_date | end_date  | end_time |
      | OLCRM | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 3 has the following personal activities
      | code  | stn | start_date | end_date  | end_time |
      | OXCRM | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     #Then rave "leg.%code%" shall be "OLCRM" on leg 1 on trip 1 on roster 2
     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMFDARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMFDARN26Dec2019" on leg 1 on trip 1 on roster 2
     Then rave "report_tpms.%leg_id%" shall be "TPMSCRMFDARN26Dec2019" on leg 1 on trip 1 on roster 3




   @SCENARIO7 @TPMS @LIFUS_BRIEFING
   Scenario: Check that event id is correct for activities LIFUSB, OXLIFB

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | LIFUSB | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OXLIFB | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSLIFUSBARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSLIFUSBARN26Dec2019" on leg 1 on trip 1 on roster 2


   @SCENARIO8 @TPMS @OCCRM
   Scenario: Check that event id is correct for activities OCC CRM FD

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code  | stn | start_date | end_date  | end_time |
      | OCCRM | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OXOCRM | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSOCCRMARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSOCCRMARN26Dec2019" on leg 1 on trip 1 on roster 2

   @SCENARIO9 @TPMS @OCCRM
   Scenario: Check that event id is correct for activities OCCRM4, OLCRM4

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OCCRM4 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLCRM4 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM4ARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM4ARN26Dec2019" on leg 1 on trip 1 on roster 2

   @SCENARIO10 @TPMS @OCCRM
   Scenario: Check that event id is correct for activities OCCRM5, OLCRM5

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OCCRM5 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLCRM5 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM5ARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM5ARN26Dec2019" on leg 1 on trip 1 on roster 2


   @SCENARIO11 @TPMS @OCCRM
   Scenario: Check that event id is correct for activities OCCRMC6, OLCRM6

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

    Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OCCRM6 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLCRM6 | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM6ARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRM6ARN26Dec2019" on leg 1 on trip 1 on roster 2



   @SCENARIO12 @TPMS @OCCRM
   Scenario: Check that event id is correct for activities OCRC, OLOCRC, OXOCRC

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | OCRC | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OLOCRC | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code   | stn | start_date | end_date  | end_time |
      | OXOCRC | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRCARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSOCRCARN26Dec2019" on leg 1 on trip 1 on roster 2


   @SCENARIO13 @TPMS @RTG
   Scenario: Check that event id is correct for activities CX7, E1, E2, E3, OLR

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |


    Given crew member 1 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | CX7  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | E1   | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 3 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | E2   | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 4 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | E3   | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 5 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | OLR  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |



     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSRECARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSPGTARN26Dec2019" on leg 1 on trip 1 on roster 2
     Then rave "report_tpms.%leg_id%" shall be "TPMSPGTARN26Dec2019" on leg 1 on trip 1 on roster 3
     Then rave "report_tpms.%leg_id%" shall be "TPMSPGTARN26Dec2019" on leg 1 on trip 1 on roster 4
     Then rave "report_tpms.%leg_id%" shall be "TPMSRECARN26Dec2019" on leg 1 on trip 1 on roster 5

   @SCENARIO14 @TPMS @WET_DRILL
   Scenario: Check that event id is correct for activities WD1, WD2, WD3, OLWD

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |

   Given a crew member with
      | attribute       | value     | valid from | valid to |
      | base            | STO       |            |          |
      | title rank      | FC        |            |          |



    Given crew member 1 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | WD1  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 2 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | WD2  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 3 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | WD3  | ARN | 26DEC2019  | 26DEC2019 | 12:00    |

    Given crew member 4 has the following personal activities
      | code | stn | start_date | end_date  | end_time |
      | OLWD | ARN | 26DEC2019  | 26DEC2019 | 12:00    |


     When I show "crew" in window 1

     Then rave "report_tpms.%leg_id%" shall be "TPMSWETARN26Dec2019" on leg 1 on trip 1 on roster 1
     Then rave "report_tpms.%leg_id%" shall be "TPMSWETARN26Dec2019" on leg 1 on trip 1 on roster 2
     Then rave "report_tpms.%leg_id%" shall be "TPMSWETARN26Dec2019" on leg 1 on trip 1 on roster 3
     Then rave "report_tpms.%leg_id%" shall be "TPMSWETARN26Dec2019" on leg 1 on trip 1 on roster 4
