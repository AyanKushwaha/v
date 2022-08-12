@jcrt @cc @fc @all @tracking @planning
Feature: FTL Max 2000 duty hours per calendar year

   ###########################################################################################
   # Tracking cases
   ###########################################################################################
   @tracking
   Scenario: Rule fails if total cumulative hours of calendar year exceeds 2000

   Given planning period from 1NOV2018 to 30NOV2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                       | acckey        | tim      | val    |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jan2018 | 0:00   |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Feb2018 | 200:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Mar2018 | 400:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Apr2018 | 600:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1May2018 | 800:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jun2018 | 1000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jul2018 | 1200:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Aug2018 | 1400:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Sep2018 | 1600:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Oct2018 | 1800:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Nov2018 | 2000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Dec2018 | 2001:00|

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 14NOV2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 14NOV2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
   Then the rule "rules_caa_ccr.caa_oma16_max_duty_time_in_calendar_year_all" shall fail on leg 1 on trip 1 on roster 1

   ###########################################################################################
   @tracking
   Scenario: Rule passes if total cumulative hours of calendar year is lower than 2000

   Given planning period from 1NOV2018 to 30NOV2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                       | acckey        | tim      | val    |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jan2018 | 0:00   |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Feb2018 | 200:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Mar2018 | 400:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Apr2018 | 600:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1May2018 | 800:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jun2018 | 1000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jul2018 | 1200:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Aug2018 | 1400:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Sep2018 | 1600:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Oct2018 | 1800:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Nov2018 | 1900:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Dec2018 | 1950:00|

    Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 14NOV2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 14NOV2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
   Then the rule "rules_caa_ccr.caa_oma16_max_duty_time_in_calendar_year_all" shall pass on leg 1 on trip 1 on roster 1

   ############################################################################################
   @tracking
   Scenario: Rule fails with soft warning if total cumulative hours of calendar year exceeds 1995 hours but is
   lower than hard limit of 2000

   Given planning period from 1NOV2018 to 30NOV2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                       | acckey        | tim      | val    |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jan2018 | 0:00   |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Feb2018 | 200:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Mar2018 | 400:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Apr2018 | 600:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1May2018 | 800:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jun2018 | 1000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jul2018 | 1200:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Aug2018 | 1400:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Sep2018 | 1600:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Oct2018 | 1800:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Nov2018 | 1995:00|
   #| accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Dec2018 | 1996:00|

    Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 14NOV2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 14NOV2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
   Then the rule "rules_caa_ccr.caa_oma16_max_duty_time_in_calendar_year_all" shall fail on leg 1 on trip 1 on roster 1
   #and rave "rules_caa_ccr.%caa_oma16_max_duty_time_in_calendar_year_all_failtext%(1996:00, 1995:00)" shall be "Soft: OMA16 duty hours in calendar year; "

    ###########################################################################################
   # Rostering cases
   ###########################################################################################
   @planning
   Scenario: Rule fails if total cumulative hours of calendar year exceeds 2000

   Given planning period from 1NOV2018 to 30NOV2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                       | acckey        | tim      | val    |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jan2018 | 0:00   |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Feb2018 | 200:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Mar2018 | 400:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Apr2018 | 600:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1May2018 | 800:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jun2018 | 1000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jul2018 | 1200:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Aug2018 | 1400:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Sep2018 | 1600:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Oct2018 | 1800:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Nov2018 | 2000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Dec2018 | 2001:00|

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 14NOV2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 14NOV2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
   Then the rule "rules_caa_ccr.caa_oma16_max_duty_time_in_calendar_year_all" shall fail on leg 1 on trip 1 on roster 1

   ###########################################################################################
   @planning
   Scenario: Rule passes if total cumulative hours of calendar year is lower than 2000

   Given planning period from 1NOV2018 to 30NOV2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                       | acckey        | tim      | val    |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jan2018 | 0:00   |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Feb2018 | 200:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Mar2018 | 400:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Apr2018 | 600:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1May2018 | 800:00 |
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jun2018 | 1000:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Jul2018 | 1200:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Aug2018 | 1400:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Sep2018 | 1600:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Oct2018 | 1800:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Nov2018 | 1900:00|
   | accumulators.duty_time_in_period_caa_acc   | crew member 1 | 1Dec2018 | 1950:00|

    Given a trip with the following activities
   | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 14NOV2018 | 10:00 | 11:00 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 14NOV2018 | 12:00 | 13:00 | SK  | 320    |

   Given trip 1 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "rule_set_jcr"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "30NOV2018 00:00"
   Then the rule "rules_caa_ccr.caa_oma16_max_duty_time_in_calendar_year_all" shall pass on leg 1 on trip 1 on roster 1

   ############################################################################################