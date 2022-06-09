#@TRACKING @FD @ALL
Feature: JCRT OM: ILC at Commander Upgrade requires normal crew composition
##############
## SKCMS-1745
##############

Background:
  Given planning period from 1Dec2018 to 31Dec2018
  Given Tracking


  ##############################################################################
  @CASE_1
  Scenario: FC crew in FC seat and FP in FP seat passes

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FP      |             |           |
  | region     | SKN     |             |           |

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | dh  | 0001 | OSL     | ARN     | 8DEC2018  | 10:00 | 11:00 | SK  | 320    |
  | leg | 0002 | ARN     | OSL     | 8Dec2018  | 13:00 | 14:00 | SK  | 320    |

  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | ARN     | ARN     | 9Dec2018  | 00:00 | 23:59 |

  Given trip 1 is assigned to crew member 1
  Given trip 1 is assigned to crew member 2
  Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 2 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 2 on roster 2

  ##############################################################################
  @CASE_2
  Scenario: FC in FC seat but FC also wrongly in FP seat as sim assist

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | dh  | 0001 | OSL     | ARN     | 8DEC2018  | 10:00 | 11:00 | SK  | 320    |

  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | ARN     | ARN     | 8Dec2018  | 13:00 | 17:00 |

  Given another trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | dh  | 0002 | ARN     | OSL     | 8DEC2018  | 18:00 | 19:00 | SK  | 320    |

  Given trip 1 is assigned to crew member 1
  Given trip 1 is assigned to crew member 2
  Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"
  Given trip 3 is assigned to crew member 1
  Given trip 3 is assigned to crew member 2

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall fail on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 3 on trip 1 on roster 2
  ##############################################################################
  @CASE_3
  Scenario: Case fails on correct leg and correct crew simple

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |


  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | ARN     | ARN     | 8Dec2018  | 13:00 | 17:00 |


  Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 2
  ##############################################################################
  @CASE_4
  Scenario: Ensure that multiple similar courses at same date are not affected by rule

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | STO     |             |           |
  | title rank | FC      |             |           |
  | region     | SKS     |             |           |
  Given crew member 3 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | STO     |             |           |
  | title rank | FP      |             |           |
  | region     | SKS     |             |           |


  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | CPH     |             |           |
  | title rank | FC      |             |           |
  | region     | SKD     |             |           |

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | CPH     |             |           |
  | title rank | FC      |             |           |
  | region     | SKD     |             |           |


  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | OSL     | OSL     | 8Dec2018  | 13:00 | 17:00 |

  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | STO     | STO     | 8Dec2018  | 13:00 | 17:00 |

  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | CPH     | CPH     | 8Dec2018  | 13:00 | 17:00 |


  # Failing trip with FC in FP position
  Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"

  # Correct trip should be unaffected by failing trip
  Given trip 2 is assigned to crew member 3 in position FC with attribute TRAINING="ILC"
  Given trip 2 is assigned to crew member 4 in position FP with attribute TRAINING="SIM ASSIST"

  # A trip that isn't skill test or cdr.  Should not be evaluated by rule.
  Given trip 3 is assigned to crew member 5 in position FC
  Given trip 3 is assigned to crew member 6 in position FP

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 3
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 4
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 5
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 6
  ##############################################################################
  @CASE_5
  Scenario: Correct case fail when same activity code is used on overlapping periods

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 3 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FP      |             |           |
  | region     | SKN     |             |           |

  Given a trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | OSL     | OSL     | 8Dec2018  | 13:00 | 17:00 |

  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | OSL     | OSL     | 8Dec2018  | 14:00 | 18:00 |

  Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"
  Given trip 2 is assigned to crew member 3 in position FC with attribute TRAINING="ILC"
  Given trip 2 is assigned to crew member 4 in position FP with attribute TRAINING="SIM ASSIST"

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall fail on leg 1 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 3
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 4
  ##############################################################################
  @CASE_6
  Scenario: Passes if skill test but not captain upgrade

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |


  Given another trip with the following activities
  | act    | code | dep stn | arr stn | date      | dep   | arr   |
  | ground | S3   | ARN     | ARN     | 8Dec2018  | 13:00 | 17:00 |


  Given trip 1 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 1 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 2


  ##############################################################################
  @CASE_7
  Scenario: FC crew in FC seat and FP in FP seat passes

  Given a crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FC      |             |           |
  | region     | SKN     |             |           |
  Given crew member 1 has restriction "TRAINING+CAPT" from 1DEC2018 to 31DEC2018

  Given another crew member with
  | attribute  | value   | valid from  | valid to  |
  | base       | OSL     |             |           |
  | title rank | FP      |             |           |
  | region     | SKN     |             |           |

  Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | dh  | 0001 | OSL     | ARN     | 8DEC2018  | 10:00 | 11:00 | SK  | 320    |
  | leg | 0002 | ARN     | OSL     | 8Dec2018  | 13:00 | 14:00 | SK  | 320    |

  Given another trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
  | leg | 0003 | OSL     | ARN     | 8DEC2018  | 10:00 | 11:00 | SK  | 320    |
  | leg | 0004 | ARN     | OSL     | 8Dec2018  | 13:00 | 14:00 | SK  | 320    |

  Given trip 1 is assigned to crew member 1
  Given trip 1 is assigned to crew member 2
  Given trip 2 is assigned to crew member 1 in position FC with attribute TRAINING="ILC"
  Given trip 2 is assigned to crew member 2 in position FP with attribute TRAINING="SIM ASSIST"

  When I show "crew" in window 1
  Then the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 2 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 1 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 2 on trip 1 on roster 2
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 3 on trip 1 on roster 1
  and the rule "rules_training_ccr.trng_normal_crew_comp_at_ilc_cdr_upgrade" shall pass on leg 4 on trip 1 on roster 2