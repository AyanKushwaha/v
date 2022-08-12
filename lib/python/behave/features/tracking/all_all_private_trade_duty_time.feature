Feature: Test private trade duty time

  Background: set up for Tracking
    Given Tracking
  @SCENARIO_1
  Scenario: Test private trade duty times for multi day trip

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 001589  | ARN     | BRU     | 07APR2019 08:50 | 07APR2019 10:55 | 320     |         |
           | leg     | SK      | 001590  | BRU     | ARN     | 07APR2019 11:35 | 07APR2019 13:45 | 320     |         |
           | dh      | SK      | 000165  | ARN     | GOT     | 07APR2019 16:15 | 07APR2019 17:10 | 320     |         |
           | leg     | SK      | 002080  | GOT     | UME     | 07APR2019 17:40 | 07APR2019 19:05 | 320     |         |
           | leg     | SK      | 002027  | UME     | ARN     | 08APR2019 10:55 | 08APR2019 11:55 | 73I     |         |
           | leg     | SK      | 000527  | ARN     | LHR     | 08APR2019 13:25 | 08APR2019 16:00 | 32G     |         |
           | leg     | SK      | 000528  | LHR     | ARN     | 08APR2019 17:15 | 08APR2019 19:40 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position AH with
           | type      | leg             | name            | value           |
           | attribute | 2,5             | MEAL_BREAK      | X               |
           | attribute | 1               | BRIEF_NOTIF_NUM | None            |

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Freeday    |           |
           |           | PRIVATELYTRADED |            | 08APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Production |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |
           | 08APR2019 21:55 |          | DT_PART            | crew member 1 | 08APR2019 12:10 | 09APR2019 00:00 | 9:45      | 08APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "rescheduling.%wop_duty_times_per_day%" shall be "1120,945," on leg 1 on trip 1 on roster 1


    @SCENARIO_2
    Scenario: Test private trade duty times for single day trip

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 001589  | ARN     | BRU     | 07APR2019 08:50 | 07APR2019 10:55 | 320     |         |
           | leg     | SK      | 001590  | BRU     | ARN     | 07APR2019 11:35 | 07APR2019 13:45 | 320     |         |
           | dh      | SK      | 000165  | ARN     | GOT     | 07APR2019 15:15 | 07APR2019 16:10 | 320     |         |
           | leg     | SK      | 002080  | GOT     | UME     | 07APR2019 16:40 | 07APR2019 18:05 | 320     |         |
           | leg     | SK      | 002027  | UME     | ARN     | 07APR2019 19:55 | 07APR2019 20:55 | 73I     |         |

    Given trip 1 is assigned to crew member 1 in position AH with
           | type      | leg             | name            | value           |
           | attribute | 2,5             | MEAL_BREAK      | X               |
           | attribute | 1               | BRIEF_NOTIF_NUM | None            |

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Freeday    |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "rescheduling.%wop_duty_times_per_day%" shall be "1120," on leg 1 on trip 1 on roster 1


  @SCENARIO_3
  Scenario: Test private trade duty times for three day trip

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 001589  | ARN     | BRU     | 07APR2019 08:50 | 07APR2019 10:55 | 320     |         |
           | leg     | SK      | 001590  | BRU     | ARN     | 07APR2019 11:35 | 07APR2019 13:45 | 320     |         |
           | dh      | SK      | 000165  | ARN     | GOT     | 07APR2019 16:15 | 07APR2019 17:10 | 320     |         |
           | leg     | SK      | 002080  | GOT     | UME     | 07APR2019 17:40 | 07APR2019 19:05 | 320     |         |
           | leg     | SK      | 002027  | UME     | ARN     | 08APR2019 10:55 | 08APR2019 11:55 | 73I     |         |
           | leg     | SK      | 000527  | ARN     | LHR     | 08APR2019 13:25 | 08APR2019 16:00 | 32G     |         |
           | leg     | SK      | 000528  | LHR     | ARN     | 08APR2019 17:15 | 08APR2019 19:40 | 32G     |         |
           | leg     | SK      | 002589  | ARN     | BRU     | 09APR2019 08:50 | 09APR2019 10:55 | 320     |         |
           | leg     | SK      | 002590  | BRU     | ARN     | 09APR2019 11:35 | 09APR2019 13:45 | 320     |         |
           | dh      | SK      | 000265  | ARN     | GOT     | 09APR2019 16:15 | 09APR2019 17:10 | 320     |         |

    Given trip 1 is assigned to crew member 1 in position AH with
           | type      | leg             | name            | value           |
           | attribute | 2,5,9           | MEAL_BREAK      | X               |
           | attribute | 1,8             | BRIEF_NOTIF_NUM | None            |

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Freeday    |           |
           |           | PRIVATELYTRADED |            | 08APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Production |           |
           |           | PRIVATELYTRADED |            | 08APR2019 22:00 |    | crew member 1 |           | 09APR2019 22:00 | Freeday    |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |
           | 08APR2019 21:55 |          | DT_PART            | crew member 1 | 08APR2019 12:10 | 09APR2019 00:00 | 9:45      | 08APR2019 00:00 | 0:00          |
           | 09APR2019 21:20 |          | DT_PART            | crew member 1 | 09APR2019 10:00 | 10APR2019 00:00 | 11:20     | 09APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "rescheduling.%wop_duty_times_per_day%" shall be "1120,945,1120," on leg 1 on trip 1 on roster 1

  @SCENARIO_4
  Scenario: Test if duty time is calculated correctly

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given a trip with the following activities
           | act     | car     | num     | dep stn | arr stn | dep             | arr             | ac_typ  | code    |
           | leg     | SK      | 001589  | ARN     | BRU     | 07APR2019 08:50 | 07APR2019 10:55 | 320     |         |
           | leg     | SK      | 001590  | BRU     | ARN     | 07APR2019 11:35 | 07APR2019 13:45 | 320     |         |
           | dh      | SK      | 000165  | ARN     | GOT     | 07APR2019 16:15 | 07APR2019 17:10 | 320     |         |
           | leg     | SK      | 002080  | GOT     | UME     | 07APR2019 17:40 | 07APR2019 19:05 | 320     |         |
           | leg     | SK      | 002027  | UME     | ARN     | 08APR2019 10:55 | 08APR2019 11:55 | 73I     |         |
           | leg     | SK      | 000527  | ARN     | LHR     | 08APR2019 13:25 | 08APR2019 16:00 | 32G     |         |
           | leg     | SK      | 000528  | LHR     | ARN     | 08APR2019 17:15 | 08APR2019 19:40 | 32G     |         |
    Given trip 1 is assigned to crew member 1 in position AH with
           | type      | leg             | name            | value           |
           | attribute | 2,5             | MEAL_BREAK      | X               |
           | attribute | 1               | BRIEF_NOTIF_NUM | None            |

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Freeday    |           |
           |           | PRIVATELYTRADED |            | 08APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Production |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |
           | 08APR2019 21:55 |          | DT_PART            | crew member 1 | 08APR2019 12:10 | 09APR2019 00:00 | 9:45      | 08APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "report_common.%duty_duty_time%" shall be "11:20" on leg 1 on trip 1 on roster 1


  @SCENARIO_5
  Scenario: Test private trade duty times for multi day fredays as one activity

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 06APR2019 22:00 and ends at 08APR2019 22:00

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Production |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |
           | 08APR2019 21:55 |          | DT_PART            | crew member 1 | 08APR2019 12:10 | 09APR2019 00:00 | 9:45      | 08APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "rescheduling.%wop_duty_times_per_day%" shall be "1120,945," on leg 1 on trip 1 on roster 1


  @SCENARIO_6
  Scenario: Test private trade duty times for multi day fredays as several activities

    Given planning period from 01APR2019 to 30APR2019

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | AH         | 26NOV2018  | 01JAN2036 |
           | region          | SKS        | 26NOV2018  | 01JAN2036 |
           | base            | STO        | 26NOV2018  | 01JAN2036 |
           | title rank      | AH         | 26NOV2018  | 01JAN2036 |
           | contract        | V00863     | 01MAR2019  | 31DEC2035 |
           | published       | 01MAY2019  | 01JAN1986  |           |
    Given crew member 1 has qualification "ACQUAL+38" from 26NOV2018 to 01JAN2036
    Given crew member 1 has qualification "ACQUAL+A2" from 19MAR2019 to 01JAN2036

    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 06APR2019 22:00 and ends at 07APR2019 22:00
    Given crew member 1 has a personal activity "F" at station "ARN" that starts at 07APR2019 22:00 and ends at 08APR2019 22:00

    Given table roster_attr additionally contains the following
           | value_abs | attr            | value_bool | start_time      | si | crew          | value_rel | end_time        | value_str  | value_int |
           |           | PRIVATELYTRADED |            | 06APR2019 22:00 |    | crew member 1 |           | 08APR2019 22:00 | Production |           |

    Given table privately_traded_days additionally contains the following
           | duty_end        | crew_ref | duty_overtime_type | crew          | duty_start      | period_end      | duty_time | period_start    | duty_overtime |
           | 07APR2019 21:20 |          | DT_PART            | crew member 1 | 07APR2019 10:00 | 08APR2019 00:00 | 11:20     | 07APR2019 00:00 | 0:00          |
           | 08APR2019 21:55 |          | DT_PART            | crew member 1 | 08APR2019 12:10 | 09APR2019 00:00 | 9:45      | 08APR2019 00:00 | 0:00          |


    When I show "crew" in window 1
    Then rave "rescheduling.%wop_duty_times_per_day%" shall be "1120,945," on leg 1 on trip 1 on roster 1
