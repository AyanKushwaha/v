@jcrt @cc @fc @all @tracking @planning
Feature: Max block time in 28 days

   ###########################################################################################
   # Rostering cases
   ###########################################################################################
   @SCENARIO1 @planning
   Scenario: Check calculation of block time for the last 28 days

   Given planning period from 1OCT2018 to 31DEC2018

   Given a crew member with homebase "STO"

   Given table accumulator_rel additionally contains the following
   | name                                | acckey        | tim       | val  |
   | accumulators.block_time_daily_acc   | crew member 1 | 3Oct2018  | 0:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 4Oct2018  | 0:30 |
   | accumulators.block_time_daily_acc   | crew member 1 | 5Oct2018  | 2:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 17Oct2018 | 2:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 18Oct2018 | 2:30 |
   | accumulators.block_time_daily_acc   | crew member 1 | 31Oct2018 | 4:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 1Nov2018  | 4:30 |
   | accumulators.block_time_daily_acc   | crew member 1 | 2Nov2018  | 6:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 14Nov2018 | 6:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 15Nov2018 | 8:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 29Nov2018 | 8:00 |
   | accumulators.block_time_daily_acc   | crew member 1 | 30Nov2018 | 8:30 |
   | accumulators.block_time_daily_acc   | crew member 1 | 1Dec2018  | 10:00|

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | dep             | arr             | car | ac_typ |
   | leg | 0001 | ARN     | LHR     | 31OCT2018 22:30 | 31OCT2018 23:30 | SK  | 320    |
   | leg | 0002 | LHR     | ARN     | 01NOV2018 00:30 | 01NOV2018 01:30 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | dep             | arr             | car | ac_typ |
   | leg | 0003 | ARN     | LHR     | 14NOV2018 10:00 | 14NOV2018 11:00 | SK  | 320    |
   | leg | 0004 | LHR     | ARN     | 14NOV2018 12:00 | 14NOV2018 13:00 | SK  | 320    |

   Given a trip with the following activities
   | act | num  | dep stn | arr stn | dep             | arr             | car | ac_typ |
   | leg | 0003 | ARN     | LHR     | 29NOV2018 21:00 | 29NOV2018 22:00 | SK  | 320    |
   | leg | 0004 | LHR     | ARN     | 29NOV2018 22:30 | 29NOV2018 23:30 | SK  | 320    |

   Given trip 1 is assigned to crew member 1
   Given trip 2 is assigned to crew member 1
   Given trip 3 is assigned to crew member 1

   When I show "crew" in window 1
   When I load rule set "Rostering_FC"
   When I set parameter "fundamental.%start_para%" to "1NOV2018 00:00"
   When I set parameter "fundamental.%end_para%" to "1DEC2018 00:00"

   Then rave "oma16.%block_time_in_last_28_days_start_day_hb%" values shall be
     | leg | trip | roster | value |
     | 1   | 1    | 1      | 4:00  |
     | 1   | 2    | 1      | 5:30  |
     | 1   | 3    | 1      | 3:30  |

   and rave "oma16.%block_time_in_last_28_days_end_day_hb%" values shall be
     | leg | trip | roster | value |
     | 1   | 1    | 1      | 4:00  |
     | 1   | 2    | 1      | 5:30  |
     | 1   | 3    | 1      | 4:00  |

# The following is kept as reference to keep track of what was wrong in SKCMS-1142
#   and rave "oma16.%block_time_in_last_28_days_start_day%" values shall be
#     | leg | trip | roster | value |
#     | 1   | 1    | 1      | 3:30  |
#     | 1   | 2    | 1      | 5:30  |
#     | 1   | 3    | 1      | 3:00  |
#
#   and rave "oma16.%block_time_in_last_28_days_end_day%" values shall be
#     | leg | trip | roster | value |
#     | 1   | 1    | 1      | 4:00  |
#     | 1   | 2    | 1      | 5:30  |
#     | 1   | 3    | 1      | 4:00  |
