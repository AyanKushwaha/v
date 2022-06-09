@tracking @ALL @JCRT
Feature: VISA license expiry warning
Develoer: Oscar Grandell, oscar.grandell@hiq.se
Date: 2019-09
############
# SKCMS-2236
############

  Background: set up for tracking
    Given Tracking
    Given planning period from 1OCT2018 to 31OCT2018


  Scenario: Rule passes on trip ending before visa license expiry, and fails on trip ending after
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |

    Given crew member 1 has document "PASSPORT+NO" from 15OCT2015 to 30OCT2018 with number "12345678"
    Given crew member 1 has document "VISA+CN,CREW" from 15OCT2015 to 15OCT2018 with number "AN345678" and maindoc number "12345678"


    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | PVG     | 14OCT2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | PVG     | OSL     | 14OCT2018 | 12:00 | 13:00 | SK  | 320    |

    Given another trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | OSL     | OSL     | 14OCT2018 | 15:00 | 16:00 |

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LAX     | 15OCT2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LAX     | OSL     | 15OCT2018 | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_caa_ccr.caa_valid_visa_all" shall pass on leg 1 on trip 1 on roster 1

