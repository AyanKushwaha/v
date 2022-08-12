@Tracking @FD @ALL @A2LR @ETOPS @LIFUS @SKCMS-2547
Feature: Instructor payments for LH ETOPS flights 


#################################################################################
Background:
    Given Tracking
    Given planning period from 1DEC2020 to 1JAN2021
    
    Given a crew member with
        | attribute   | value   |
        | base        | CPH     |
        | title rank  | FC      |

    Given another crew member with 
        | attribute   | value   |
        | base        | OSL     |
        | title rank  | FC      |

    Given another crew member with 
        | attribute   | value   |
        | base        | STO     |
        | title rank  | FC      |

    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A4" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 1 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1JAN2020 to 31DEC2035

    Given crew member 2 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A4" from 1JAN2020 to 31DEC2035
    Given crew member 2 has qualification "ACQUAL+A5" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 2 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1JAN2020 to 31DEC2035

    Given crew member 3 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A4" from 1JAN2020 to 31DEC2035
    Given crew member 3 has qualification "ACQUAL+A5" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 3 has acqual qualification "ACQUAL+AWB+INSTRUCTOR+LIFUS" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
        | act   | car  | num     | dep stn  | arr stn  | dep             | arr             | ac_typ | code |
        | leg   | SK   | 000101  | CPH      | SFO      | 16DEC2020 11:00 | 16DEC2020 22:00 | 33A    |      |
        | leg   | SK   | 000102  | SFO      | CPH      | 17DEC2020 22:00 | 18DEC2020 11:00 | 33A    |      |
    
    Given a trip with the following activities
        | act   | car  | num     | dep stn  | arr stn  | dep             | arr             | ac_typ | code |
        | leg   | SK   | 000101  | OSL      | LAX      | 16DEC2020 11:00 | 16DEC2020 22:00 | 33A    |      |
        | leg   | SK   | 000102  | LAX      | OSL      | 17DEC2020 22:00 | 18DEC2020 11:00 | 33A    |      |

    Given a trip with the following activities
        | act   | car  | num     | dep stn  | arr stn  | dep             | arr             | ac_typ | code |
        | leg   | SK   | 000101  | ARN      | SFO      | 16DEC2020 11:00 | 16DEC2020 22:00 | 33A    |      |
        | leg   | SK   | 000102  | SFO      | ARN      | 17DEC2020 22:00 | 18DEC2020 11:00 | 33A    |      |
    
#################################################################################
    @SCENARIO1 @SKD
    Scenario: Danish instructors get paid per leg

    Given trip 1 is assigned to crew member 1 in position FC with
        | type      | leg  | name       | value          |
        | attribute | 1,2  | INSTRUCTOR | ETOPS LIFUS/LC |

    When I set parameter "salary.%salary_month_start_p%" to "1DEC2020"
    and I set parameter "salary.%salary_month_end_p%" to "1JAN2021"
    and I show "crew" in window 1

    Then rave "salary.%inst_lci_lh%" shall be "2" on roster 1
    #and rave "salary.%inst_act_etops_lifus_lc%" shall be "True" on leg 1 on trip 1 on roster 1
    #and rave "salary.%inst_act_etops_lifus_lc%" shall be "True" on leg 2 on trip 1 on roster 1