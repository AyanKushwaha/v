@TRACKING
Feature: Re-introduce the rule for standby outside airport 

  @SCENARIO_1
  Scenario: Crew has standby away from airport and rule should pass even if ci is after standby end.

    Given planning period from 1Nov2019 to 30Nov2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FC        |            |          |

    # additionally contains the following
    Given table published_standbys is overridden with the following
    | crew          | sby_start       | sby_end         |
    | crew member 1 | 10Nov2019 09:10 | 10Nov2019 19:40 |

    # Standby at airport
    Given crew member 1 has a personal activity "R" at station "ARN" that starts at 10Nov2019 09:10 and ends at 10Nov2019 20:30

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | ARN     | LHR     | 10NOV2019 | 21:40 | 23:30 |
    | leg | 0002 | LHR     | ARN     | 11NOV2019 | 01:00 | 03:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    
    Then rave "leg.%is_standby_at_home%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_ci_not_after_standby_end_all" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_2
  Scenario: Crew has standby at airport and rules should fail if ci is after standby end.

    Given planning period from 1Nov2019 to 30Nov2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FC        |            |          |

    Given another crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FC        |            |          |

     # additionally contains the following
    Given table published_standbys is overridden with the following
    | crew          | sby_start       | sby_end         |
    | crew member 1 | 10Nov2019 09:10 | 10Nov2019 20:00 |
    | crew member 2 | 10Nov2019 09:10 | 10Nov2019 20:00 |

    Given table crew_publish_info is overridden with the following
    | crew          | start_date       | end_date       | pcat | checkout        |
    | crew member 1 | 10Nov2019        | 11Nov2019      | 10   | 10Nov2019 21:00 |
    | crew member 2 | 10Nov2019        | 11Nov2019      | 10   | 10Nov2019 21:00 |

    # Standby at airport
    Given crew member 1 has a personal activity "A" at station "ARN" that starts at 10Nov2019 09:10 and ends at 10Nov2019 20:00
    Given crew member 2 has a personal activity "W" at station "ARN" that starts at 10Nov2019 09:10 and ends at 10Nov2019 20:00

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | ARN     | LHR     | 10NOV2019 | 21:40 | 23:30 |
    | leg | 0002 | LHR     | ARN     | 11NOV2019 | 01:00 | 03:00 |

    Given trip 1 is assigned to crew member 1
    Given trip 1 is assigned to crew member 2

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    
    Then rave "leg.%is_standby_at_airport%" shall be "True" on leg 1 on trip 1 on roster 1
    and rave "leg.%is_standby_at_airport%" shall be "True" on leg 1 on trip 1 on roster 2
    and the rule "rules_caa_cct.caa_oma16_ci_not_after_standby_end_all" shall fail on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_ci_not_after_standby_end_all" shall fail on leg 1 on trip 1 on roster 2

  @SCENARIO_3
  Scenario: Crew has standby at home and rule should fail if ci is after standby end plus travel time from home.

    Given planning period from 1Nov2019 to 30Nov2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FC        |            |          |

    Given table published_standbys is overridden with the following
    | crew          | sby_start       | sby_end         |
    | crew member 1 | 10Nov2019 09:10 | 10Nov2019 20:40 |

    # Standby at airport
    Given crew member 1 has a personal activity "R" at station "ARN" that starts at 10Nov2019 09:10 and ends at 10Nov2019 20:30

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | ARN     | LHR     | 10NOV2019 | 23:30 | 23:50 |
    | leg | 0002 | LHR     | ARN     | 11NOV2019 | 01:00 | 03:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    
    Then rave "leg.%is_standby_at_home%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_time_btw_standby_end_and_check_in" shall fail on leg 1 on trip 1 on roster 1

  @SCENARIO_4
  Scenario: Crew has standby at home and rule should fail if ci is after standby end plus travel time from hotel.

    Given planning period from 1Nov2019 to 30Nov2019

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FC        |            |          |

    Given table published_standbys is overridden with the following
    | crew          | sby_start       | sby_end         |
    | crew member 1 | 10Nov2019 09:10 | 10Nov2019 20:40 |

    # Standby at airport
    Given crew member 1 has a personal activity "H" at station "ARN" that starts at 10Nov2019 09:10 and ends at 10Nov2019 20:30

    Given another trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | ARN     | LHR     | 10NOV2019 | 23:30 | 23:50 |
    | leg | 0002 | LHR     | ARN     | 11NOV2019 | 01:00 | 03:00 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load rule set "rule_set_jct"
    
    Then rave "leg.%is_standby_at_hotel%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_caa_cct.caa_oma16_max_time_btw_standby_end_and_check_in" shall fail on leg 1 on trip 1 on roster 1
