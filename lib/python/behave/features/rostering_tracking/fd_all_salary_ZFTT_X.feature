@JCRT @CC @TRACKING
Feature: ZFTT X should give same instructor compensation as LIFUS

########################
# JIRA - SKCMS-2172
########################

Background:
  Given planning period from 1Aug2019 to 1Sep2019
  Given Tracking

  ##############################################################################
  @scenario1
  Scenario: FC crew member has ZFTT X short haul.

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 20MAY2017  | 01JAN2020 |
           | region          | SKI        | 20MAY2017  | 01JAN2020 |
           | base            | OSL        | 20MAY2017  | 01JAN2020 |
           | title rank      | FC         | 20MAY2017  | 01JAN2020 |
           | contract        | V134-LH    | 08MAR2016  | 01JAN2036 |
           | published       | 01OCT2019  | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+A3" from 21JUN2017 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A4" from 17APR2017 to 01JAN2036
    Given crew member 1 has qualification "POSITION+LCP" from 26AUG2019 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 22MAY2016 to 01JAN2036
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 13AUG2019 to 31DEC2035

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | dh      | SK      | 001419  | ARN     | CPH     | 25AUG2019 08:00 | 25AUG2019 09:10 | 32W     |         |
           | leg     | SK      | 000927  | CPH     | BOS     | 25AUG2019 10:50 | 25AUG2019 18:55 | 33B     |         |
           | leg     | SK      | 000928  | BOS     | CPH     | 26AUG2019 21:30 | 27AUG2019 04:55 | 33B     |         |
           | dh      | SK      | 001416  | CPH     | ARN     | 27AUG2019 06:00 | 27AUG2019 07:10 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 2,3             | INSTRUCTOR      | ZFTT X          |

   When I set parameter "salary.%salary_month_start_p%" to "1AUG2019"
   and I set parameter "salary.%salary_month_end_p%" to "1SEP2019"
   and I show "crew" in window 1
   Then rave "salary.%inst_lifus_act%" shall be "2" on roster 1


    @scenario2
  Scenario: FC crew member has ZFTT X long haul.

     Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01JAN2015  | 25DEC2019 |
           | region          | SKS        | 01JAN2015  | 25DEC2019 |
           | base            | STO        | 01JAN2015  | 25DEC2019 |
           | title rank      | FC         | 01JAN2015  | 25DEC2019 |
           | contract        | V00163     | 01MAY2018  | 07OCT2019 |
           | published       | 01OCT2019  | 01JAN1986  |           |

    Given crew member 1 has qualification "ACQUAL+38" from 01JAN2015 to 07OCT2019
    Given crew member 1 has qualification "POSITION+LCP" from 25FEB2016 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+38+AIRPORT+SMI" from 11MAY2014 to 01OCT2020
    Given crew member 1 has acqual qualification "ACQUAL+38+INSTRUCTOR+LIFUS" from 06NOV2015 to 31DEC2035

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 002547  | ARN     | MAN     | 25AUG2019 07:30 | 25AUG2019 10:00 | 73E     |         |
           | leg     | SK      | 002548  | MAN     | ARN     | 25AUG2019 10:40 | 25AUG2019 12:55 | 73E     |         |
           | dh      | SK      | 001020  | ARN     | SFT     | 25AUG2019 14:45 | 25AUG2019 15:55 | 73G     |         |
           | leg     | SK      | 001011  | SFT     | ARN     | 26AUG2019 04:35 | 26AUG2019 05:45 | 73B     |         |
           | leg     | SK      | 001040  | ARN     | KRN     | 26AUG2019 06:25 | 26AUG2019 07:55 | 73B     |         |
           | leg     | SK      | 001041  | KRN     | ARN     | 26AUG2019 08:25 | 26AUG2019 09:55 | 73B     |         |
           | dh      | SK      | 000010  | ARN     | LLA     | 26AUG2019 12:15 | 26AUG2019 13:30 | 73D     |         |
           | leg     | SK      | 000001  | LLA     | ARN     | 27AUG2019 04:05 | 27AUG2019 05:30 | 73I     |         |
           | leg     | SK      | 001012  | ARN     | SFT     | 27AUG2019 06:10 | 27AUG2019 07:20 | 73I     |         |
           | leg     | SK      | 001013  | SFT     | ARN     | 27AUG2019 07:45 | 27AUG2019 08:50 | 73I     |         |

    Given trip 1 is assigned to crew member 1 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2,4,5,6,8,9,10 | INSTRUCTOR     | ZFTT X          |

   When I set parameter "salary.%salary_month_start_p%" to "1AUG2019"
   and I set parameter "salary.%salary_month_end_p%" to "1SEP2019"
   and I show "crew" in window 1
   Then rave "salary.%inst_lifus_act%" shall be "3" on roster 1