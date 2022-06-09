@tracking @ALL @JCRT
Feature: Medical license expiry warning
############
# SKCMS-1972
############

  Background: set up for tracking
    Given Tracking
    Given planning period from 1OCT2018 to 31OCT2018


  Scenario: Rule passes on trip ending before medical license expiry, and fails on trip ending after
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    
    Given crew member 1 has document "MEDICAL" from 15OCT2015 to 15OCT2018 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 14OCT2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 14OCT2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | LHR     | 15OCT2018 | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | OSL     | 15OCT2018 | 12:00 | 13:00 | SK  | 320    |
    
    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1
    
    When I show "crew" in window 1
    Then the rule "rules_caa_ccr.caa_valid_medical_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_ccr.caa_valid_medical_all" shall fail on leg 1 on trip 2 on roster 1


############
# SKCMS-2236
############
  @SCENARIO2
  Scenario: Rule should be able to fail even if there are only activities without only flight duties

    Given Tracking
    Given planning period from 1OCT2018 to 31OCT2018
    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |

    Given crew member 1 has document "MEDICAL" from 15OCT2015 to 05OCT2018

    Given a trip with the following activities
      | act    | code | dep stn | arr stn | date      | dep   | arr   | car | num | ac_typ |
      | ground |  C6  | OSL     | OSL     | 14OCT2018 | 06:00 | 08:00 |     |     |        |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ | code |
      | leg | 0001 | OSL     | CPH     | 14OCT2018 | 10:00 | 11:00 | SK  | 320    |      |
      | leg | 0002 | CPH     | LHR     | 14OCT2018 | 12:00 | 13:00 | SK  | 320    |      |
      | leg | 0003 | LHR     | OSL     | 14OCT2018 | 14:00 | 15:00 | SK  | 320    |      |

    Given another trip with the following activities
      | act    | code | dep stn | arr stn | date      | dep   | arr   | car | num | ac_typ |
      | ground | C6   | OSL     | OSL     | 15OCT2018 | 06:00 | 08:00 |     |     |        |

    Given another trip with the following activities
      | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ | code |
      | leg | 0001 | OSL     | LHR     | 15OCT2018 | 10:00 | 11:00 | SK  | 320    |      |
      | leg | 0002 | LHR     | OSL     | 15OCT2018 | 12:00 | 13:00 | SK  | 320    |      |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1
    Given trip 3 is assigned to crew member 1

    When I show "crew" in window 1
    Then rave "trip.%is_last_flt_sby_or_bl_in_month%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_ccr.caa_valid_medical_all" shall fail on leg 1 on trip 1 on roster 1
