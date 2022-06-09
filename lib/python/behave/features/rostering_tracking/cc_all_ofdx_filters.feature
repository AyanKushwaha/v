@CC @TRAINING
Feature: Test office day filters

    Background: Set up

    @SCENARIO_TW99_1 @planning
    Scenario: Check that TW99 activity is needed for crew in SKD_CC_AG with AL qualification in filter period
       Given planning period from 1JUL2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       # 33 -> TW99 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(33)" shall be "True" on leg 1 on trip 1 on roster 1

    @SCENARIO_TW99_2 @tracking
    Scenario: Check that TW99 activity is not needed for crew in SKD_CC_AG without AL qualification in filter period
       Given planning period from 1JUL2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       # 33 -> TW99 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(33)" shall be "False" on leg 1 on trip 1 on roster 1


    @SCENARIO_TW99_3 @planning
    Scenario: Check that TW99 activity is not needed for crew in SKD_CC_AG with AL qualification outside of filter period
       Given planning period from 1JUN2019 to 1JUL2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUN2019 22:00 and ends at 4JUN2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUN2019 00:00"
       and I set parameter "fundamental.%end_para%" to "30JUN2019 00:00"

       # 33 -> TW99 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(33)" shall be "False" on leg 1 on trip 1 on roster 1

    @SCENARIO_TW99_4 @planning
    Scenario: Check that TW99 activity is not needed for crew in SKD_CC_AG with AL qualification in filter period and TW99 in roster
       Given planning period from 1JUL2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2019 to 31DEC2035

       Given crew member 1 has a personal activity "TW99" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JUL2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JUL2019 00:00"

       # 33 -> TW99 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(33)" shall be "False" on leg 1 on trip 1 on roster 1


    @SCENARIO_TW10_1 @planning
    Scenario: Check that TW10 activity is needed for crew in SKD_CC_AG with AL qualification in filter period
       Given planning period from 1FEB2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2018 to 31DEC2035

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
       and I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

       # 6 -> TW10 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(6)" shall be "True" on leg 1 on trip 1 on roster 1

    @SCENARIO_TW10_2 @tracking
    Scenario: Check that TW10 activity is needed for crew in SKD_CC_AG without AL qualification in filter period
       Given planning period from 1FEB2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Tracking"

       # 6 -> TW10 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(6)" shall be "True" on leg 1 on trip 1 on roster 1


    @SCENARIO_TW10_3 @planning
    Scenario: Check that TW10 activity is not needed for crew in SKD_CC_AG with AL qualification outside of filter period
       Given planning period from 1JAN2019 to 1FEB2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2018 to 31DEC2035

       Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 3JUN2019 22:00 and ends at 4JUN2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1JAN2019 00:00"
       and I set parameter "fundamental.%end_para%" to "31JAN2019 00:00"

       # 6 -> TW10 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(6)" shall be "False" on leg 1 on trip 1 on roster 1

    @SCENARIO_TW10_4 @planning
    Scenario: Check that TW10 activity is not needed for crew in SKD_CC_AG with AL qualification in filter period and TW10 in roster
       Given planning period from 1FEB2019 to 1AUG2019

       Given a crew member with
       | attribute  | value  | valid from | valid to  |
       | base       | CPH    |            |           |
       | title rank | AH     |            |           |
       | region     | SKD    |            |           |
       | contract   | V345   |            |           |

       Given crew member 1 has qualification "ACQUAL+AL" from 1APR2018 to 31DEC2035

       Given crew member 1 has a personal activity "TW10" at station "CPH" that starts at 3JUL2019 22:00 and ends at 4JUL2019 22:00

       When I show "crew" in window 1
       and I load rule set "Rostering_CC"
       and I set parameter "fundamental.%start_para%" to "1FEB2019 00:00"
       and I set parameter "fundamental.%end_para%" to "28FEB2019 00:00"

       # 6 -> TW10 in task.%ofdx_code%
       Then rave "training.%reqd_ofdx_training_missing%(6)" shall be "False" on leg 1 on trip 1 on roster 1

