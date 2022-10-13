Feature: Rules that checks that LPC/OPC documents are handled correctly when you switch AC types

    Background:
        Given planning period from 01JAN2020 to 31JAN2020

        Given a crew member with
        | attribute | value | valid from | valid to |
        | base      | OSL   |            |          |
        | title rank| FC    |            |          |
        
        Given crew member 1 has qualification "ACQUAL+A2" from 01JAN2020 to 31DEC2020
        Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1DEC2020
        Given crew member 1 has document "REC+CRM" from 1JAN2018 to 1DEC2020
        Given crew member 1 has document "REC+PGT" from 1JAN2018 to 1DEC2020
        

    Scenario: Pilot has old 38 expiring after A2
        Given Tracking
        Given crew member 1 has qualification "ACQUAL+38" from 01JAN2018 to 01JAN2020
        Given table crew_document additionally contains the following
        |crew         | doc_typ | doc_subtype | validfrom | validto   | docno | maindocno | issuer| si | ac_qual|
        |crew member 1| REC     | OPC         | 01JAN2020 | 01JUN2020 |       |           |       |    | A2     |
        |crew member 1| REC     | OPC         | 01JUL2019 | 31DEC2020 |       |           |       |    | 38     |
        |crew member 1| REC     | LPC         | 01JAN2020 | 01MAY2020 |       |           |       |    | A2     |
        |crew member 1| REC     | LPC         | 01JUL2019 | 31DEC2020 |       |           |       |    | 38     |
        |crew member 1| REC     | LC          | 01JAN2020 | 01JUL2020 |       |           |       |    | A2     |
        |crew member 1| REC     | LC          | 01JUL2019 | 31DEC2020 |       |           |       |    | 38     |

        Given a trip with the following activities
        | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
        | leg | 0001 | OSL     | LHR     | 12JAN2020 | 10:00 | 11:00 | SK  | 320    |
        | leg | 0002 | LHR     | OSL     | 12JAN2020 | 12:00 | 13:00 | SK  | 320    |
        Given trip 1 is assigned to crew member 1 in position FC
      
        When I show "crew" in window 1
        Then rave "training.%all_required_recurrent_dates_registered_trip_start%" shall be "True" on leg 1 on trip 1 on roster 1
        and rave "crg_info.%lpc_str%" shall be " LPC: Apr20"
        and rave "crg_info.%opc_str%" shall be "OPC: May20"
        and rave "crg_info.%lc_str%" shall be " LC: Jun20 "
