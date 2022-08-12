Feature: Number of active asian  service crew  allowed on flights  between scandinavia and asia dhould not
          exceed the allowed limit of 20 percent.
   Background: This check already exists for the number of asian countries but not for Hongkong. 

  ###################################################################################
  @tracking_1
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is equal to 20 percent (flight origin CPH)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | HKG     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | HKG     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 5

  ###################################################################################
@tracking_2
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is greater than 20 percent (flight origin CPH)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | HKG     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | HKG     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    Given trip 1 is assigned to crew member 6 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 5
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 6
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall fail on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall fail on leg 1 on trip 1 on roster 6
    
  ###################################################################################
@tracking_3
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is less than 20 percent (flight origin CPH)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | HKG     | 15DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | HKG     | CPH     | 15DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    Given trip 1 is assigned to crew member 6 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 5
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 6
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 6
  ###################################################################################
  ###################################################################################
  @tracking_4
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is equal to 20 percent (flight origin HKG)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | HKG     | CPH     | 16DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | CPH     | HKG     | 16DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 5

  ###################################################################################
@tracking_5
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is greater than 20 percent (flight origin HKG)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | HKG     | CPH     | 16DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | CPH     | HKG     | 16DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    Given trip 1 is assigned to crew member 6 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 5
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 6
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall fail on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall fail on leg 1 on trip 1 on roster 6

  ###################################################################################
@tracking_6
    Scenario: Check that rule sft_asian_crew_limit_sk_asia_sk_flights is unsuccessful, when percentage of the  asian
              service crew is less than 20 percent (flight origin CPH)
    Given Tracking
    Given planning period from 1Jan2018 to 31dec2018

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | HKG       |            |          |
    | title rank      | AH        |            |          |
    | region          |           |            |          |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | HKG     | CPH     | 16DEC2018 | 08:00 | 11:30 | SK  | 320    |
    | leg | 0002 | CPH     | HKG     | 16DEC2018 | 14:00 | 17:30 | SK  | 320    |

    Given trip 1 is assigned to crew member 1 in position AH
    Given trip 1 is assigned to crew member 2 in position AH
    Given trip 1 is assigned to crew member 3 in position AH
    Given trip 1 is assigned to crew member 4 in position AH
    Given trip 1 is assigned to crew member 5 in position AH
    Given trip 1 is assigned to crew member 6 in position AH
    When I show "crew" in window 1
    Then rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 1
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 2
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 3
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 4
    and rave "crew.%homebase%" shall be "CPH" on leg 1 on trip 1 on roster 5
    and rave "crew.%homebase%" shall be "HKG" on leg 1 on trip 1 on roster 6
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 2
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 3
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 4
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 5
    and the rule "rules_soft_cct.sft_asian_crew_limit_sk_asia_sk_flights" shall pass on leg 1 on trip 1 on roster 6
  ###################################################################################



