@TRACKING
Feature: The calculation of OMA16 awake time rules should not only use scheduled block-on of the last active leg, 
        but also estimated block-on of the last active leg should be considered.
        
	  Scenario: Case passes if soft rule fails, hard rule passes.
	      
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | A    | CPH     | CPH     | 07OCT2018 | 05:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 19:00 | 20:01 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    
    Then rave "duty_period.%time_until_block_on%" shall be "15:01" on leg 1 on trip 1 on roster 1
    and rave "duty.%last_active_scheduled_block_on%" shall be "07OCT2018 20:01" on leg 1 on trip 1 on roster 1
    and rave "duty.%last_active_block_on%" shall be "07OCT2018 20:01" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall fail on leg 1 on trip 1 on roster 1