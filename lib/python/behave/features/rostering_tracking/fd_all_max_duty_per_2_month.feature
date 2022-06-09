@JCR @ALL @FD @SKCMS-2177 @K19
Feature: Rule checks that max working days arent exceeded.

  ##############################################################################
  # Notes:
  # K19 - It is decided that VG and FG group crew in all countries should be controlled by the same duty time rule
  # For VG crew the liumit is 8h48m times number of p days, for FG crew the limit is 9h30m times number of p days
  # Case 1-3 is SKN VG
  # Case 4-6 is SKS VG
  # Case 7-9 is SKD VG
  # Case 10-12 is SKD FG
  # Developer: Oscar Grandell <oscar.grandell@hiq.se>

  ##############################################################################
  Background:
    Given planning period from 1FEB2019 to 28FEB2019

  ##############################################################################
  @PASS_1
  Scenario: Rule passes for SKN with duty time less then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00200" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:39 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_2
  Scenario: Rule passes for SKN with duty time equals 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00200" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:40 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_3
  Scenario: Rule passes for SKN with duty time greater then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | OSL    |
    | title rank | FD     |
    | region     | SKN    |
    Given crew member 1 has contract "V00200" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:41 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_4
  Scenario: Rule passes for SKS with duty time less then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:39 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_5
  Scenario: Rule passes for SKS with duty time equals 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:40 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_6
  Scenario: Rule passes for SKS with duty time greater then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | STO    |
    | title rank | FD     |
    | region     | SKS    |
    Given crew member 1 has contract "V133" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:41 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_7
  Scenario: Rule passes for SKD with duty time less then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:39 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_8
  Scenario: Rule passes for SKD with duty time equals 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:40 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_9
  Scenario: Rule passes for SKD with duty time greater then 8:48 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "V131" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 116:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:41 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall fail on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_10
  Scenario: Rule passes for SKD with duty time less then 9:30 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "F127" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 250:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:39 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_11
  Scenario: Rule passes for SKD with duty time equals 9:30 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "F127" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 250:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:40 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall pass on leg 1 on trip 1 on roster 1

  ##############################################################################
  @PASS_12
  Scenario: Rule passes for SKD with duty time greater then 9:30 times number of prod days

    Given a crew member with
    | attribute  | value  |
    | base       | CPH    |
    | title rank | FD     |
    | region     | SKD    |
    Given crew member 1 has contract "F127" from 01JAN2017 to 01JAN2020

    Given table accumulator_rel additionally contains the following
    | name                                       | acckey         | tim      | val    |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Jan2019 | 8:00   |
    | accumulators.planned_duty_time_fc_vg_acc   | crew member 1  | 1Feb2019 | 250:00 |

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   |
    | leg | 0001 | OSL     | EWR     | 01FEB2019 | 10:00 | 18:48 |
    | leg | 0002 | EWR     | OSL     | 02FEB2019 | 00:05 | 08:41 |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1
    When I load ruleset "Rostering_FC"
    When I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
    When I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

    Then rave "rules_indust_ccr.%ind_max_duty_time_2_months_fc_valid%" shall be "True" on leg 1 on trip 1 on roster 1
    and the rule "rules_indust_ccr.ind_max_duty_time_2_months_fc" shall fail on leg 1 on trip 1 on roster 1