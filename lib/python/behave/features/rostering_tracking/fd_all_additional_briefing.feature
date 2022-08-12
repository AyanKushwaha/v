Feature: Additional briefing time in connection with training activities for FD
#####################
# JIRA - SKCMS-2072 #
#####################

  @tracking @SCENARIO1
  Scenario: Additional check-in time for LIFUS
    Given Tracking
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FP      |             |           |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FC      |             |           |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2019 to 31JUL2019
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JUL2019 to 31JUL2019

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

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="LIFUS"

    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="LIFUS"
    
    When I show "crew" in window 1
    Then rave "leg.%check_in_fc_training_exception%" values shall be
    | leg | trip | roster | value |
    | 1   | 1    | 1      | 0:15  |
    | 2   | 1    | 1      | 0:00  |
    | 3   | 1    | 1      | 0:00  |
    | 4   | 1    | 1      | 0:00  |
    | 1   | 2    | 1      | 0:00  |
    | 2   | 2    | 1      | 0:00  |
    | 1   | 1    | 2      | 0:15  |
    | 2   | 1    | 2      | 0:00  |
    | 3   | 1    | 2      | 0:00  |
    | 4   | 1    | 2      | 0:00  |
    | 1   | 2    | 2      | 0:00  |
    | 2   | 2    | 2      | 0:00  |


  @tracking @SCENARIO2
  Scenario: Additional check-in time for FAM FLT
    Given Tracking
    Given planning period from 1JUL2019 to 31JUL2019
    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FP      |             |           |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JUL2019 to 31JUL2019

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FC      |             |           |

    Given crew member 2 has qualification "ACQUAL+A2" from 1JUL2019 to 31JUL2019
    Given crew member 2 has acqual qualification "ACQUAL+A2+INSTRUCTOR+LIFUS" from 1JUL2019 to 31JUL2019

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

    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"
    Given trip 2 is assigned to crew member 1 in position FP with attribute TRAINING="FAM FLT"

    Given trip 1 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="FAM FLT"
    Given trip 2 is assigned to crew member 2 in position FC with attribute INSTRUCTOR="FAM FLT"
    
    When I show "crew" in window 1
    Then rave "leg.%check_in_fc_training_exception%" values shall be
    | leg | trip | roster | value |
    | 1   | 1    | 1      | 0:15  |
    | 2   | 1    | 1      | 0:00  |
    | 3   | 1    | 1      | 0:00  |
    | 4   | 1    | 1      | 0:00  |
    | 1   | 2    | 1      | 0:00  |
    | 2   | 2    | 1      | 0:00  |
    | 1   | 1    | 2      | 0:15  |
    | 2   | 1    | 2      | 0:00  |
    | 3   | 1    | 2      | 0:00  |
    | 4   | 1    | 2      | 0:00  |
    | 1   | 2    | 2      | 0:00  |
    | 2   | 2    | 2      | 0:00  |
