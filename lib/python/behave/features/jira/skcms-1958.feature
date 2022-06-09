@tracking @oma16
Feature: Calculation of OMA16 awake time and checking of rules
 ###################################################################################
 # Standby at home
 ###################################################################################
    Scenario: Standby at home, check correct calculation and rules passing
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R    | CPH     | CPH     | 07OCT2018 | 05:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "rules_caa_cct.%standby_and_fdp_time%" shall be "8:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at home, check correct calculation and rules passing
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R    | CPH     | CPH     | 07OCT2018 | 05:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 20:00 | 22:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "rules_caa_cct.%standby_and_fdp_time%" shall be "17:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at home, check correct calculation and soft rule fail, hard rule pass
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R    | CPH     | CPH     | 07OCT2018 | 05:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 20:00 | 22:01 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "rules_caa_cct.%standby_and_fdp_time%" shall be "17:01" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_standby_callout_all" shall fail on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at home, check correct calculation and hard rule failing, soft rule pass
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R    | CPH     | CPH     | 07OCT2018 | 04:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 20:00 | 22:01 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "rules_caa_cct.%standby_and_fdp_time%" shall be "18:01" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_standby_callout_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
 # Checking dead head
 ###################################################################################
    @deadhead
    Scenario: Standby at home, check correct calculation and rule passing when dead heading last leg
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | R    | CPH     | CPH     | 07OCT2018 | 04:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 20:00 | 22:01 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I load rule set "rule_set_jct"
    When I show "crew" in window 1
    and I select leg 5
    and I Change to/from Deadhead
    Then rave "rules_caa_cct.%standby_and_fdp_time%" shall be "14:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_standby_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
  # Standby at airport
 ###################################################################################
    Scenario: Standby at airport, check correct calculation and rules passing
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
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 11:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 12:00 | 13:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "duty_period.%time_until_block_on%" shall be "8:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at airport, check correct calculation and rules passing
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
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 19:00 | 20:00 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    Then rave "duty_period.%time_until_block_on%" shall be "15:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at airport, check correct calculation and soft rule fail, hard rule pass
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
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall fail on leg 1 on trip 1 on roster 1

 ###################################################################################
    Scenario: Standby at airport, check correct calculation and rules failing
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | A    | CPH     | CPH     | 07OCT2018 | 04:00 | 08:00 |

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
    Then rave "duty_period.%time_until_block_on%" shall be "16:01" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################
 # Checking Dead head
 ###################################################################################
    @deadhead
    Scenario: Standby at airport, check correct calculation and rule passing when dead heading last leg
    Given planning period from 1Oct2018 to 31Oct2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | FC        |            |          |
    | region          | SKD       |            |          |


    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | A    | CPH     | CPH     | 07OCT2018 | 04:00 | 08:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | LHR     | 7OCT2018  | 10:00 | 12:00 | SK  | 320    |
    | leg | 0002 | LHR     | CPH     | 7OCT2018  | 13:00 | 15:00 | SK  | 320    |
    | leg | 0003 | CPH     | LHR     | 7OCT2018  | 16:00 | 18:00 | SK  | 320    |
    | leg | 0004 | LHR     | CPH     | 7OCT2018  | 19:00 | 20:01 | SK  | 320    |

    Given trip 1 is assigned to crew member 1
    Given trip 2 is assigned to crew member 1 in position FC

    When I load rule set "rule_set_jct"
    When I show "crew" in window 1
    and I select leg 5
    and I Change to/from Deadhead
    Then rave "duty_period.%time_until_block_on%" shall be "14:00" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.soft_oma16_max_airport_callout_all" shall pass on leg 1 on trip 1 on roster 1

 ###################################################################################