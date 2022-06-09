@tracking @FD @ALL @A2LR
Feature: Salary: Instructor pay for A2LR training
##############
## SKCMS-2547
############## 

Background:
  Given planning period from 1AUG2019 to 1SEP2019
  Given Tracking

 @scenario1
  Scenario: FC crew member has ETOPS LIFUS LC long haul.

   Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01JAN2015  | 25DEC2019 |
           | region          | SKD        | 01JAN2015  | 25DEC2019 |
           | base            | SFO        | 01JAN2015  | 25DEC2019 |
           | title rank      | FC         | 01JAN2015  | 25DEC2019 |
           | contract        | V00163     | 01MAY2018  | 07OCT2019 |
           | published       | 01OCT2019  | 01JAN1986  |           |

        Given crew member 1 has qualification "ACQUAL+A3" from 21JUN2010 to 01JAN2036
        Given crew member 1 has qualification "ACQUAL+A4" from 17APR2010 to 01JAN2036
        Given crew member 1 has qualification "POSITION+LCP" from 26AUG2010 to 31DEC2035
        Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 22MAY2010 to 01JAN2036
        Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 13AUG2010 to 31DEC2035

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 002547  | SFO     | MAN     | 25AUG2019 07:30 | 25AUG2019 10:00 | 73E     |         |
           | leg     | SK      | 002548  | MAN     | SFO     | 25AUG2019 10:40 | 25AUG2019 12:55 | 73E     |         |
           | dh      | SK      | 001020  | SFO     | SFT     | 25AUG2019 14:45 | 25AUG2019 15:55 | 73G     |         |
           | leg     | SK      | 001011  | SFT     | SFO     | 26AUG2019 04:35 | 26AUG2019 05:45 | 73B     |         |
           | leg     | SK      | 001040  | SFO     | KRN     | 26AUG2019 06:25 | 26AUG2019 07:55 | 73B     |         |
           | leg     | SK      | 001041  | KRN     | SFO     | 26AUG2019 08:25 | 26AUG2019 09:55 | 73B     |         |
           | dh      | SK      | 000010  | SFO     | LLA     | 26AUG2019 12:15 | 26AUG2019 13:30 | 73D     |         |
           | leg     | SK      | 000001  | LLA     | SFO     | 27AUG2019 04:05 | 27AUG2019 05:30 | 73I     |         |
           | leg     | SK      | 001012  | SFO     | SFT     | 27AUG2019 06:10 | 27AUG2019 07:20 | 73I     |         |
           | leg     | SK      | 001013  | SFT     | SFO     | 27AUG2019 07:45 | 27AUG2019 08:50 | 73I     |         |

    Given trip 1 is assigned to crew member 1 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2,4,5,6,8,9,10 | INSTRUCTOR     | ETOPS LIFUS/LC  |


   When I set parameter "salary.%salary_month_start_p%" to "1AUG2019"
   and I set parameter "salary.%salary_month_end_p%" to "1SEP2019"
   and I show "crew" in window 1

   Then rave "salary.%inst_lci_lh%" shall be "4" on roster 1
   
 @scenario2
  Scenario: FC crew member has ETOPS LIFUS LC long haul Norwegian Instructor.

   Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01JAN2015  | 25DEC2019 |
           | region          | SKN        | 01JAN2015  | 25DEC2019 |
           | base            | SFO        | 01JAN2015  | 25DEC2019 |
           | title rank      | FC         | 01JAN2015  | 25DEC2019 |
           | contract        | V00001-LH  | 01MAY2018  | 07OCT2019 |
           | published       | 01OCT2019  | 01JAN1986  |           |

        Given crew member 1 has qualification "ACQUAL+A3" from 21JUN2010 to 01JAN2036
        Given crew member 1 has qualification "ACQUAL+A4" from 17APR2010 to 01JAN2036
        Given crew member 1 has qualification "POSITION+LCP" from 26AUG2010 to 31DEC2035
        Given crew member 1 has acqual qualification "ACQUAL+AWB+AIRPORT+US" from 22MAY2010 to 01JAN2036
        Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 13AUG2010 to 31DEC2035

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 002547  | SFO     | MAN     | 25AUG2019 07:30 | 25AUG2019 10:00 | 73E     |         |
           | leg     | SK      | 002548  | MAN     | SFO     | 25AUG2019 10:40 | 25AUG2019 12:55 | 73E     |         |
           | dh      | SK      | 001020  | SFO     | SFT     | 25AUG2019 14:45 | 25AUG2019 15:55 | 73G     |         |
           | leg     | SK      | 001011  | SFT     | SFO     | 26AUG2019 04:35 | 26AUG2019 05:45 | 73B     |         |
           | leg     | SK      | 001040  | SFO     | KRN     | 26AUG2019 06:25 | 26AUG2019 07:55 | 73B     |         |
           | leg     | SK      | 001041  | KRN     | SFO     | 26AUG2019 08:25 | 26AUG2019 09:55 | 73B     |         |
           | dh      | SK      | 000010  | SFO     | LLA     | 26AUG2019 12:15 | 26AUG2019 13:30 | 73D     |         |
           | leg     | SK      | 000001  | LLA     | SFO     | 27AUG2019 04:05 | 27AUG2019 05:30 | 73I     |         |
           | leg     | SK      | 001012  | SFO     | SFT     | 27AUG2019 06:10 | 27AUG2019 07:20 | 73I     |         |
           | leg     | SK      | 001013  | SFT     | SFO     | 27AUG2019 07:45 | 27AUG2019 08:50 | 73I     |         |

    Given trip 1 is assigned to crew member 1 in position FC with
           | type      | leg             | name            | value           |
           | attribute | 1,2,4,5,6,8,9,10 | INSTRUCTOR     | ETOPS LIFUS/LC  |


   When I set parameter "salary.%salary_month_start_p%" to "1AUG2019"
   and I set parameter "salary.%salary_month_end_p%" to "1SEP2019"
   and I show "crew" in window 1

   Then rave "salary.%inst_lci_lh%" shall be "3" on roster 1 



 @scenario3
  Scenario: FC crew member has LR REFRESH long haul.

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
           | attribute | 1,2,4,5,6,8,9,10 | INSTRUCTOR     | LR REFRESH      |

   When I set parameter "salary.%salary_month_start_p%" to "1AUG2019"
   and I set parameter "salary.%salary_month_end_p%" to "1SEP2019"
   and I show "crew" in window 1

   Then rave "salary.%inst_lifus_act%" shall be "3" on roster 1
   
