Feature: Test that crew has correct amount fo FS days per month

###################
#  SKCMS-2568
###################

Background: Setup for tracking
    Given Tracking
    Given planning period from 01dec2018 to 31dec2018


#######################################################################
    @SCENARIO1
    Scenario: Check that rule fails when trying to add two FS days in a month for FD SKD


    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | CPH     |             |           |
    | title rank | FD      |             |           |
    | region     | SKD     |             |           |

     Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has a personal activity "FS" at station "CPH" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "CPH" that starts at 26dec2018 23:00 and ends at 27dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 27dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

     When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 2 on roster 1


#######################################################################
    @SCENARIO2
    Scenario: Check that rule fails when trying to add two FS days in a month for FD SKS


    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | STO     |             |           |
    | title rank | FD      |             |           |
    | region     | SKS     |             |           |

     Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "ARN" that starts at 26dec2018 23:00 and ends at 27dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 27dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

     When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 2 on roster 1

#######################################################################
    @SCENARIO3
    Scenario: Check that rule fails when trying to add two FS days in a month for FD SKN

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FD      |             |           |
    | region     | SKN     |             |           |

   Given crew member 1 has contract "V00007"

     Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 17dec2018 23:00
    and crew member 1 has a personal activity "FS" at station "OSL" that starts at 26dec2018 23:00 and ends at 27dec2018 23:00

    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |
    | 2  | crew member 1 | 27dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

     When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month" shall fail on leg 1 on trip 2 on roster 1

    #######################################################################
    @SCENARIO4
    Scenario: Check that rule passes when trying to add one FS day per month for FD SKN

    Given a crew member with
    | attribute  | value   | valid from  | valid to  |
    | base       | OSL     |             |           |
    | title rank | FD      |             |           |
    | region     | SKN     |             |           |

   Given crew member 1 has contract "V00007"

    Given crew member 1 has qualification "ACQUAL+A2" from 26MAR2008 to 09SEP2019
    Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16dec2018 23:00 and ends at 18dec2018 23:00


    Given table account_entry additionally contains the following
    | id | crew          | tim       | account | source          | amount | man  | published | rate | reasoncode     | entrytime | username |
    | 1  | crew member 1 | 17dec2018 | FS      | Granted daysoff | -100   | True | True      | 100  | OUT correction | 1dec2018  | carmadm  |

     When I show "crew" in window 1

    Then the rule "rules_indust_ccr.ind_max_fs_days_month" shall pass on leg 1 on trip 1 on roster 1