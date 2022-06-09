Feature: JCRT : Max 2 split duties in one wop
  Background: set up for tracking
    Given Tracking
    Given a crew member with 
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FP      |             |           |
    | region     | SVS     |             |           |
    
    
@SCENARIO1
  Scenario: ind_max_split_duty_in_wop_svs should pass for less than 2 split duties in one wop

    Given planning period from 1AUG2020 to 31AUG2020

    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 21AUG2020 10:00 and ends at 22AUG2020 11:00
    Given crew member 1 has a personal activity "F" at station "OSL" that starts at 29AUG2020 22:00 and ends at 29AUG2020 22:00

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car  | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0002 | DBV     | OSL     | 25AUG2020 | 11:15 | 16:25 | SVS  | 320    |
    | leg | 0003 | OSL     | DBV     | 25AUG2020 | 17:00 | 20:00 | SVS  | 320    |

    | leg | 0004 | DBV     | OSL     | 26AUG2020 | 01:15 | 04:25 | SVS | 320    |
    | leg | 0005 | OSL     | DBV     | 26AUG2020 | 06:00 | 08:20 | SVS | 320    |
    | leg | 0006 | DBV     | CPH     | 26AUG2020 | 15:15 | 16:25 | SVS | 320    |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_svs_indust_cct.ind_max_split_duty_in_wop_svs" shall pass on leg 1 on trip 1 on roster 1

@SCENARIO2
    Scenario: ind_max_split_duty_in_wop_svs should fail for more than two split duties in wop
    Given Tracking

    Given planning period from 1AUG2020 to 15SEP2020
    

    Given table agreement_validity additionally contains the following
        | id                             | validfrom | validto   |   
        | has_agmt_group_svs_cc          | 01MAR2020 | 31Dec2035 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car  | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0002 | DBV     | OSL     | 25AUG2020 | 11:15 | 16:25 | SVS  | 320    |
    | leg | 0003 | OSL     | DBV     | 25AUG2020 | 17:00 | 20:00 | SVS  | 320    |

    | leg | 0004 | DBV     | OSL     | 26AUG2020 | 01:15 | 04:25 | SVS  | 320    |
    | leg | 0005 | OSL     | DBV     | 26AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0006 | DBV     | CPH     | 26AUG2020 | 15:15 | 16:25 | SVS  | 320    |

   Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0007 | CPH     | LHR     | 27AUG2020 | 04:15 | 05:25 | SVS  | 320    |
    | leg | 0008 | LHR     | DBV     | 27AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0009 | DBV     | OSL     | 27AUG2020 | 15:15 | 16:25 | SVS  | 320    |

    | leg | 0010 | OSL     | LHR     | 28AUG2020 | 01:15 | 04:25 | SVS  | 320    |
    | leg | 0011 | LHR     | DBV     | 28AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0012 | DBV     | CPH     | 28AUG2020 | 15:15 | 16:25 | SVS  | 320    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0007 | CPH     | LHR     | 29AUG2020 | 04:15 | 05:25 | SVS  | 320    |
    | leg | 0008 | LHR     | DBV     | 29AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0009 | DBV     | OSL     | 29AUG2020 | 15:15 | 16:25 | SVS  | 320    |

    | leg | 0010 | OSL     | LHR     | 30AUG2020 | 01:15 | 04:25 | SVS  | 320    |
    | leg | 0011 | LHR     | DBV     | 30AUG2020 | 06:00 | 08:20 | SVS  | 320    |
    | leg | 0012 | DBV     | CPH     | 30AUG2020 | 15:15 | 16:25 | SVS  | 320    |

    Given trip 1 is assigned to crew member 1 in position FP
    Given trip 2 is assigned to crew member 1 in position FP
    Given trip 3 is assigned to crew member 1 in position FP

    When I show "crew" in window 1
    Then the rule "rules_svs_indust_cct.ind_max_split_duty_in_wop_svs" shall fail on leg 1 on trip 1 on roster 1