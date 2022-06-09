@JCRT @RECURRENT @TRAINING
Feature: Checks to see that recurrent training is performed
  Background: Set up for Tracking
    Given Tracking
    Given planning period from 1May2019 to 31May2019

    @SCENARIO1
    Scenario: Recurrent document must be valid for production, even if training in trip (CRM)
      Lack recurrent document
      Given a crew member with
             | attribute       | value      | valid from | valid to  |
             | crew rank       | FC         | 01JAN2016  | 31DEC2035 |
             | region          | SKN        | 01JAN2016  | 31DEC2035 |
             | base            | OSL        | 01JAN2016  | 31DEC2035 |
             | title rank      | FC         | 01JAN2016  | 31DEC2035 |
             | contract        | F134       | 12SEP2018  | 21MAR2020 |
      Given crew member 1 has qualification "ACQUAL+38" from 05JAN2015 to 31DEC2035
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 12FEB2015 to 31MAR2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 11FEB2015 to 31AUG2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KSU" from 19FEB2015 to 16OCT2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 17FEB2015 to 31MAR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 13FEB2015 to 31MAR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+INSTRUCTOR+LIFUS" from 31DEC2018 to 04FEB2020
      Given crew member 1 has document "REC+CRM" from 1JAN2018 to 30APR2019

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | leg     | SK      | 000484  | OSL     | ARN     | 03MAY2019 09:05 | 03MAY2019 10:00 | 73S     |         |
             | ground  |         |         | ARN     | ARN     | 04MAY2019 06:30 | 04MAY2019 14:30 |         | CRM     |
             | dh      | SK      | 000883  | ARN     | OSL     | 04MAY2019 16:20 | 04MAY2019 17:20 | 738     |         |
      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 1 on trip 1 on roster 1
      and rave "rules_qual_ccr.%missed_recurrent_training_failtext%" shall be "OMA: Rec. expiry dates passed, needs: CRM, LC, CRM, PC, PGT" on leg 1 on trip 1 on roster 1

    @SCENARIO2
    Scenario: Recurrent document must be valid for production, even if training in trip (CRM)
      Has recurrent document.
      Given a crew member with
             | attribute       | value      | valid from | valid to  |
             | crew rank       | FC         | 01JAN2016  | 31DEC2035 |
             | region          | SKN        | 01JAN2016  | 31DEC2035 |
             | base            | OSL        | 01JAN2016  | 31DEC2035 |
             | title rank      | FC         | 01JAN2016  | 31DEC2035 |
             | contract        | F134       | 12SEP2018  | 21MAR2020 |
      Given crew member 1 has qualification "ACQUAL+38" from 05JAN2015 to 31DEC2035
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 12FEB2015 to 31MAR2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 11FEB2015 to 31AUG2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KSU" from 19FEB2015 to 16OCT2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+LYR" from 17FEB2015 to 31MAR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 13FEB2015 to 31MAR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+INSTRUCTOR+LIFUS" from 31DEC2018 to 04FEB2020
      Given crew member 1 has document "REC+CRM" from 1JAN2018 to 30APR2020

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | leg     | SK      | 000484  | OSL     | ARN     | 03MAY2019 09:05 | 03MAY2019 10:00 | 73S     |         |
             | ground  |         |         | ARN     | ARN     | 04MAY2019 06:30 | 04MAY2019 14:30 |         | CRM     |
             | dh      | SK      | 000883  | ARN     | OSL     | 04MAY2019 16:20 | 04MAY2019 17:20 | 738     |         |
      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1


    @SCENARIO3
    Scenario: Recurrent document must be valid for production, even if training in trip (PGT)
      Has recurrent document
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | FC          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | FC          | 05JAN2016  | 01APR2021 |
             | contract        | F134        | 03MAY2018  | 01JUN2020 |
      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 04OCT2018 to 31DEC2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 01JAN2012 to 31MAY2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 28FEB2021
      Given crew member 1 has document "REC+PGT" from 1JAN2018 to 30APR2020

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | dh      | SK      | 004024  | SVG     | OSL     | 10MAY2019 11:25 | 10MAY2019 12:15 | 73K     |         |
             | leg     | SK      | 001312  | OSL     | SVG     | 10MAY2019 12:45 | 10MAY2019 13:55 | 73K     |         |
             | leg     | SK      | 001313  | SVG     | OSL     | 10MAY2019 14:25 | 10MAY2019 15:35 | 73K     |         |
             | ground  |         |         | OSL     | OSL     | 11MAY2019 07:00 | 11MAY2019 14:00 |         | E3      |
             | dh      | SK      | 004045  | OSL     | SVG     | 11MAY2019 16:50 | 11MAY2019 17:45 | 73S     |         |
      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1

    @SCENARIO4
    Scenario: Recurrent document must be valid for production, even if training in trip (PGT)
      Lack recurrent document
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | FC          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | FC          | 05JAN2016  | 01APR2021 |
             | contract        | F134        | 03MAY2018  | 01JUN2020 |
      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 04OCT2018 to 31DEC2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 01JAN2012 to 31MAY2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 28FEB2021
      Given crew member 1 has document "REC+PGT" from 1JAN2018 to 30APR2019

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | dh      | SK      | 004024  | SVG     | OSL     | 10MAY2019 11:25 | 10MAY2019 12:15 | 73K     |         |
             | leg     | SK      | 001312  | OSL     | SVG     | 10MAY2019 12:45 | 10MAY2019 13:55 | 73K     |         |
             | leg     | SK      | 001313  | SVG     | OSL     | 10MAY2019 14:25 | 10MAY2019 15:35 | 73K     |         |
             | ground  |         |         | OSL     | OSL     | 11MAY2019 07:00 | 11MAY2019 14:00 |         | E3      |
             | dh      | SK      | 004045  | OSL     | SVG     | 11MAY2019 16:50 | 11MAY2019 17:45 | 73S     |         |
      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 2 on trip 1 on roster 1

    @SCENARIO5
    Scenario: Recurrent document must be valid for production, even if training in trip (PGT)
      Recurrent document expires during trip
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | FC          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | FC          | 05JAN2016  | 01APR2021 |
             | contract        | F134        | 03MAY2018  | 01JUN2020 |
      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 04OCT2018 to 31DEC2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 01JAN2012 to 31MAY2020
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 28FEB2021
      Given crew member 1 has document "REC+PGT" from 1JAN2018 to 11MAY2019

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | dh      | SK      | 004024  | SVG     | OSL     | 10MAY2019 11:25 | 10MAY2019 12:15 | 73K     |         |
             | leg     | SK      | 001312  | OSL     | SVG     | 13MAY2019 12:45 | 13MAY2019 13:55 | 73K     |         |
             | leg     | SK      | 001313  | SVG     | OSL     | 13MAY2019 14:25 | 13MAY2019 15:35 | 73K     |         |
             | ground  |         |         | OSL     | OSL     | 14MAY2019 07:00 | 14MAY2019 14:00 |         | E3      |
             | dh      | SK      | 004045  | OSL     | SVG     | 14MAY2019 16:50 | 14MAY2019 17:45 | 73S     |         |
      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall pass on leg 1 on trip 1 on roster 1
      Then the rule "rules_qual_ccr.qln_recurrent_training_performed_ALL" shall fail on leg 2 on trip 1 on roster 1
      
    @SCENARIO6
    Scenario: Recurrent document must be valid for production, even if training in trip (CRM, CRMC)
      Recurrent document expires during trip.
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | AS          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | AS          | 05JAN2016  | 01APR2021 |
             | contract        | V300        | 03MAY2018  | 01JUN2021 |
      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 04OCT2018 to 31DEC2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 01JAN2012 to 31MAY2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 28FEB2021
      Given crew member 1 has document "REC+REC" from 1JAN2018 to 30MAY2019
      Given crew member 1 has document "REC+CRMC" from 1JAN2018 to 30MAY2019
      

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | dh      | SK      | 004024  | SVG     | OSL     | 29MAY2019 11:25 | 30MAY2019 12:15 | 73K     |         |
             | leg     | SK      | 001312  | OSL     | SVG     | 31MAY2019 12:45 | 01JUN2019 13:55 | 73K     |         |

      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then rave "rules_qual_ccr.%all_needed_recurrent_training_performed_trip%" shall be "False" on leg 1 on trip 1 on roster 1      
      Then rave "rules_qual_ccr.%all_needed_recurrent_training_performed_trip%" shall be "False" on leg 2 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%all_needed_recurrent_training_performed_duty%" shall be "True" on leg 1 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%all_needed_recurrent_training_performed_duty%" shall be "False" on leg 2 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%active_duty_in_trip_after_rec_doc_expiry_date%" shall be "True" on leg 2 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%qln_recurrent_training_performed_ALL_valid%" shall be "True" on leg 2 on trip 1 on roster 1
      

    @SCENARIO7 @To_Be_Checked
    Scenario: Recurrent document must be valid for production, even if training in trip (CRM, CRMC)
      Recurrent document expires during trip and next flight is deadhead.
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | AS          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | AS          | 05JAN2016  | 01APR2021 |
             | contract        | V300        | 03MAY2018  | 01JUN2021 |
      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+ALF" from 04OCT2018 to 31DEC2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+KKN" from 01JAN2012 to 31MAY2021
      Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+TOS" from 03NOV2014 to 28FEB2021
      Given crew member 1 has document "REC+REC" from 1JAN2018 to 30MAY2019
      Given crew member 1 has document "REC+CRMC" from 1JAN2018 to 30MAY2019
      

      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | leg     | SK      | 004024  | SVG     | OSL     | 29MAY2019 11:25 | 30MAY2019 12:15 | 73K     |         |
             | dh      | SK      | 001312  | OSL     | SVG     | 31MAY2019 12:45 | 01JUN2019 13:55 | 73K     |         |

      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then rave "rules_qual_ccr.%qln_recurrent_training_performed_ALL_valid%" shall be "True" on leg 1 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%qln_recurrent_training_performed_ALL_valid%" shall be "False" on leg 2 on trip 1 on roster 1     
      Then rave "rules_qual_ccr.%active_duty_in_trip_after_rec_doc_expiry_date%" shall be "True" on leg 2 on trip 1 on roster 1


    @SCENARIO8
    Scenario: Rule alerts on leg if recurrent document expires before duty with standby ends.
      Given a crew member with
             | attribute       | value       | valid from | valid to  |
             | crew rank       | AS          | 05JAN2016  | 01APR2021 |
             | region          | SKN         | 05JAN2016  | 01APR2021 |
             | base            | SVG         | 05JAN2016  | 01APR2021 |
             | title rank      | AS          | 05JAN2016  | 01APR2021 |
             | contract        | V300        | 03MAY2018  | 01JUN2021 |
#      Given crew member 1 has qualification "ACQUAL+38" from 10AUG1987 to 01APR2021
      Given crew member 1 has document "REC+REC" from 1JAN2018 to 30MAY2019


      Given a trip with the following activities
             | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
             | leg     | SK      | 004024  | SVG     | OSL     | 29MAY2019 11:25 | 30MAY2019 12:15 | 73K     |         |

      Given crew member 1 has a personal activity "A" at station "OSL" that starts at 31MAY2019 07:00 and ends at 31MAY2019 15:00

      Given trip 1 is assigned to crew member 1 in position TL

      When I show "crew" in window 1
      Then rave "rules_qual_ccr.%qln_recurrent_training_performed_ALL_valid%" shall be "True" on leg 1 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%qln_recurrent_training_performed_ALL_valid%" shall be "True" on leg 2 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%active_duty_in_trip_after_rec_doc_expiry_date%" shall be "True" on leg 1 on trip 1 on roster 1
      Then rave "rules_qual_ccr.%active_duty_in_trip_after_rec_doc_expiry_date%" shall be "True" on leg 2 on trip 1 on roster 1
      
      