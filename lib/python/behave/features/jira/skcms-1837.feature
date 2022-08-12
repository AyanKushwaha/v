Feature: Test consecutive simulator night session rule

  Background: set up for tracking
    Given Tracking


  Scenario: Rule not active before October 1 2018
    Given planning period from 1SEP2018 to 30SEP2018

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 07SEP2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 08SEP2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 09SEP2018 | 00:00 | 04:00 |

    and a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 2 is assigned to crew member 1 in position FC
    and trip 3 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 3 on roster 1


  Scenario: Third consecutive simulator night session gives rule failure
    Given planning period from 1OCT2018 to 31OCT2018

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 06OCT2018 | 20:00 | 22:05 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 08OCT2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 09OCT2018 | 03:55 | 06:00 |

    and a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 2 is assigned to crew member 1 in position FC
    and trip 3 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall fail on leg 1 on trip 3 on roster 1


  Scenario: No failure when first consecutive session is not in the night
    Given planning period from 1OCT2018 to 31OCT2018

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 06OCT2018 | 20:00 | 22:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 08OCT2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 09OCT2018 | 00:00 | 04:00 |

    and a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 2 is assigned to crew member 1 in position FC
    and trip 3 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 3 on roster 1


  Scenario: No failure when third consecutive session is not in the night
    Given planning period from 1OCT2018 to 31OCT2018

    Given a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 07OCT2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 08OCT2018 | 00:00 | 04:00 |

    and a trip with the following activities
    | act    | code | dep stn | arr stn | date      | dep   | arr   |
    | ground | Z2   | ARN     | ARN     | 09OCT2018 | 04:00 | 06:00 |

    and a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | FC        |            |          |

    and trip 1 is assigned to crew member 1 in position FC
    and trip 2 is assigned to crew member 1 in position FC
    and trip 3 is assigned to crew member 1 in position FC
    
    When I show "crew" in window 1

    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 2 on roster 1
    and the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 1 on trip 3 on roster 1


  Scenario: Check that rule does not fail when scheduling a simulator after 6:00 the same day as the second night sim in a row.
    Given planning period from 1OCT2018 to 31OCT2018
    
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    | ground | 0003 | OSL     | OSL     | 02OCT2018 | 08:00 | 09:00 | S2   |    
    Given trip 1 is assigned to crew member 1 in position FC    

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 3 on trip 1 on roster 1    


  Scenario: Check that rule does not fail when scheduling a sim night shift the day after two night sim sessions in a row.
    Given planning period from 1OCT2018 to 31OCT2018
  
    Given a crew member with homebase "OSL"
    Given crew member 1 has qualification "ACQUAL+A2" from 1OCT2018 to 31OCT2018 
       
    Given a trip with the following activities
    | act    | num  | dep stn | arr stn | date      | dep   | arr   | code |
    | ground | 0001 | OSL     | OSL     | 01OCT2018 | 01:00 | 02:00 | S2   |
    | ground | 0002 | OSL     | OSL     | 02OCT2018 | 01:00 | 04:00 | S2   |
    | ground | 0003 | OSL     | OSL     | 04OCT2018 | 05:00 | 09:00 | S2   |    
    Given trip 1 is assigned to crew member 1 in position FC    

    When I show "crew" in window 1
    Then the rule "rules_indust_ccr.max_night_simulators_in_row" shall pass on leg 3 on trip 1 on roster 1 