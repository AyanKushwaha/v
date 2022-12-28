Feature: Test LPC and OPC

   Background:
     Given Tracking
     Given planning period from 1NOV2018 to 30NOV2018

   ###################
   # JIRA - SKCMS-2009
   ###################
   @TRACKING @SCENARIO1 @SUB_CATEGORY @LIFUS
   Scenario: Check that sub category is Q for AWB pilot with LIFUS instructor qualification

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 21JAN2007  | 01MAY2023 |
           | region          | SKI        | 21JAN2007  | 01MAY2023 |
           | base            | STO        | 21JAN2007  | 01MAY2023 |
           | title rank      | FC         | 21JAN2007  | 01MAY2023 |
           | published       | 01MAR2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+A3" from 21JAN2007 to 01MAY2023
    Given crew member 1 has qualification "ACQUAL+A4" from 21JAN2007 to 01MAY2023
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 08APR2009 to 30SEP2022
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 10JUN2014 to 31DEC2035
    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000945  | ARN     | ORD     | 19NOV2018 14:30 | 19NOV2018 23:45 | 33A     |         |
           | leg     | SK      | 000946  | ORD     | ARN     | 21NOV2018 01:45 | 21NOV2018 10:10 | 33A     |         |
    Given trip 1 is assigned to crew member 1 in position FC

     When I show "crew" in window 1

     Then rave "crew.%sub_category_leg_start%" shall be "Q" on leg 1 on trip 1 on roster 1


   ###################
   # JIRA - SKCMS-2009
   ###################
   @TRACKING @SCENARIO2 @SUB_CATEGORY @LIFUS
   Scenario: Check that sub category is Q for A2 pilot with LIFUS instructor qualification

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 05JAN2017  | 01JAN2036 |
           | region          | SKS        | 05JAN2017  | 01JAN2036 |
           | base            | STO        | 05JAN2017  | 01JAN2036 |
           | title rank      | FC         | 05JAN2017  | 01JAN2036 |
           | published       | 01MAR2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+A2" from 09OCT2016 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 11NOV2017 to 31DEC2035
    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 001016  | ARN     | SFT     | 20NOV2018 13:25 | 20NOV2018 14:35 | 32G     |         |
           | leg     | SK      | 001017  | SFT     | ARN     | 20NOV2018 15:00 | 20NOV2018 16:10 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then rave "crew.%sub_category_leg_start%" shall be "Q" on leg 1 on trip 1 on roster 1


   ###################
   # JIRA - SKCMS-2009
   ###################
   @TRACKING @SCENARIO3 @SUB_CATEGORY @LCP
   Scenario: Check that sub category is I for A2 pilot with LCP instructor qualification

    Given planning period from 1FEB2019 to 28FEB2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 30OCT2016  | 31DEC2035 |
           | title rank      | FC         | 30OCT2016  | 31DEC2035 |
    Given crew member 1 has qualification "ACQUAL+A2" from 14SEP2015 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 21AUG2016 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 18JUN2016 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRE" from 11AUG2016 to 01OCT2019
    Given crew member 1 has acqual qualification "ACQUAL+A2+INSTRUCTOR+TRI" from 08JUL2016 to 01OCT2021
    Given a trip with the following activities
           | act     | car     | num | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 1   | ARN     | LHR     | 05FEB2019 15:05 | 05FEB2019 17:45 | 32G     |         |
           | leg     | SK      | 2   | LHR     | ARN     | 05FEB2019 19:00 | 05FEB2019 21:30 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then rave "crew.%sub_category_leg_start%" shall be "I" on leg 1 on trip 1 on roster 1


   ###################
   # JIRA - SKCMS-2009
   ###################
   @TRACKING @SCENARIO4 @SUB_CATEGORY @LIFUS @LCP @SFE @TRI
   Scenario: Check that sub category is I for AWB pilot with LIFUS, SFE, TRI and LCP instructor qualification

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01JAN2016  | 31DEC2035 |
           | region          | SKI        | 01JAN2016  | 31DEC2035 |
           | base            | OSL        | 01JAN2016  | 31DEC2035 |
           | title rank      | FC         | 01JAN2016  | 31DEC2035 |
    Given crew member 1 has qualification "ACQUAL+A3" from 03OCT2011 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A4" from 08DEC2011 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 07APR2016 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+SFE" from 30APR2014 to 01MAY2020
    Given crew member 1 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 14MAY2014 to 01JUL2020
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+SFE" from 30APR2014 to 01MAY2020
    Given crew member 1 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 14MAY2014 to 01JUL2020
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 01MAY2011 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 01MAR2016 to 31DEC2035

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 000945  | OSL     | ORD     | 19NOV2018 14:30 | 19NOV2018 23:45 | 33A     |         |
           | leg     | SK      | 000946  | ORD     | OSL     | 21NOV2018 01:45 | 21NOV2018 10:10 | 33A     |         |
    Given trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then rave "crew.%sub_category_leg_start%" shall be "I" on leg 1 on trip 1 on roster 1
