@JCRT @CC @TRACKING @TRAINING
Feature: Additional briefing time in connection with UX SUPERNUM and RELEASE
########################
# JIRA - SKCMS-1875/2028
########################

  @tracking @SKN
  Scenario: Additional check-in time on SUPERNUM for region SKN
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | ARN     | OSL     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:10" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 2 on roster 1

  @tracking @SKD
  Scenario: Additional check-in time on SUPERNUM for region SKD
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 1 has contract "V300"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | CPH     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | ARN     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:10" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 2 on roster 1

  @tracking @SKS
  Scenario: Additional check-in time on SUPERNUM for region SKS
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | AH      |             |           |
    | region     | SKS     |             |           |
    Given crew member 1 has contract "V340"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | GOT     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | GOT     | UME     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | UME     | GOT     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | GOT     | ARN     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | GOT     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | GOT     | ARN     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:10" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 2 on roster 1
    
  @tracking @SKN
  Scenario: Additional check-out time on RELEASE for region SKN
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | ARN     | OSL     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:10" on leg 2 on trip 2 on roster 1

  @tracking @SKD
  Scenario: Additional check-out time on RELEASE for region SKD
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 1 has contract "V300"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | CPH     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | ARN     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:10" on leg 2 on trip 2 on roster 1


  @tracking @SKS
  Scenario: Additional check-out time on RELEASE for region SKS
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | AH      |             |           |
    | region     | SKS     |             |           |
    Given crew member 1 has contract "V340"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | GOT     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | GOT     | UME     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | UME     | GOT     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | GOT     | ARN     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | GOT     | 10JUL2019 | 08:00 | 09:10 | SK  | 320    |
    | leg | 0002 | GOT     | ARN     | 10JUL2019 | 11:20 | 12:30 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 2 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 2 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:10" on leg 2 on trip 2 on roster 1
    
  @tracking @SKN
  Scenario: No additional check-in or check-out without training attribute for region SKN
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | OSL     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1

  @tracking @SKD
  Scenario: No additional check-in or check-out without training attribute for region SKD
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | AH      |             |           |
    | region     | SKD     |             |           |
    Given crew member 1 has contract "V300"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | ARN     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | CPH     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | CPH     | DBV     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | DBV     | CPH     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1

  @tracking @SKS
  Scenario: No additional check-in or check-out without training attribute for region SKS
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | AH      |             |           |
    | region     | SKS     |             |           |
    Given crew member 1 has contract "V340"

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | ARN     | GOT     | 09JUL2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | GOT     | UME     | 09JUL2019 | 07:55 | 09:10 | SK  | 320    |
    | leg | 0003 | UME     | GOT     | 09JUL2019 | 10:10 | 12:30 | SK  | 32W    |
    | leg | 0004 | GOT     | ARN     | 09JUL2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
    When I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 3 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 4 on trip 1 on roster 1

  @tracking @SKN @SKD
  Scenario: No additional check-in on SUPERNUM training before validity date for SKN and SKD
    Given planning period from 1APR2019 to 30APR2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09APR2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | OSL     | 09APR2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="X SUPERNUM"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1APR2019 00:00"
    When I set parameter "fundamental.%end_para%" to "30APR2019 00:00"
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_in_cc_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1

  @tracking @SKN @SKD
  Scenario: No additional check-out on RELEASE training before validity date for SKN and SKD
    Given planning period from 1APR2019 to 30APR2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | AH      |             |           |
    | region     | SKN     |             |           |
    Given crew member 1 has contract "V301"
    
    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | ARN     | 09APR2019 | 06:00 | 07:10 | SK  | 320    |
    | leg | 0002 | ARN     | OSL     | 09APR2019 | 13:20 | 15:45 | SK  | 32W    |
   
    Given trip 1 is assigned to crew member 1 in position AH with attribute TRAINING="RELEASE"
    
    When I show "crew" in window 1
    When I load rule set "rule_set_jcr"
    When I set parameter "fundamental.%start_para%" to "1APR2019 00:00"
    When I set parameter "fundamental.%end_para%" to "30APR2019 00:00"
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 1 on trip 1 on roster 1
    Then rave "leg.%check_out_training_exception%" shall be "0:00" on leg 2 on trip 1 on roster 1
