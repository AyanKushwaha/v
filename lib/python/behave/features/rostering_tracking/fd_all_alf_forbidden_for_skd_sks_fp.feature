Feature: SKS and SKD pilots with rank FP are forbidden to fly to ALF due to limitations in training.

  @SCENARIO_1_SKS
  Scenario: SKS FC rank pilot can fly to ALF in position FC with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_2_SKS
  Scenario: SKS FC rank pilot cant fly to ALF in position FC without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO_3_SKS
  Scenario: SKS FC rank pilot can fly to ALF in position FP L with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_4_SKS
  Scenario: SKS FC rank pilot cant fly to ALF in position FP L without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%alf_forbidden_for_skd_sks_fp_failtext%" shall be "OMA: ALF is forbidden destination for SKD/SKS FP"
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_5_SKS
  Scenario: SKS FP rank pilot cant fly to ALF in FP position
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKS        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%alf_forbidden_for_skd_sks_fp_failtext%" shall be "OMA: ALF is forbidden destination for SKD/SKS FP"
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1

  @SCENARIO_1_SKD
  Scenario: SKD FC rank pilot can fly to ALF in position FC with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKD        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_2_SKD
  Scenario: SKD FC rank pilot cant fly to ALF in position FC without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKD        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO_3_SKD
  Scenario: SKD FC rank pilot can fly to ALF in position FP L with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKD        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_4_SKD
  Scenario: SKD FC rank pilot cant fly to ALF in position FP L without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKD        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%alf_forbidden_for_skd_sks_fp_failtext%" shall be "OMA: ALF is forbidden destination for SKD/SKS FP"
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_5_SKD
  Scenario: SKD FP rank pilot cant fly to ALF in FP position
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKD        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall fail on leg 1 on trip 1 on roster 1
    and rave "rules_qual_ccr.%alf_forbidden_for_skd_sks_fp_failtext%" shall be "OMA: ALF is forbidden destination for SKD/SKS FP"
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1

  @SCENARIO_1_SKN
  Scenario: SKN FC rank pilot can fly to ALF in position FC with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKN        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_2_SKN
  Scenario: SKN FC rank pilot can fly to ALF in position FC without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKN        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FC

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall fail on leg 1 on trip 1 on roster 1


  @SCENARIO_3_SKN
  Scenario: SKN FC rank pilot can fly to ALF in position FP L with airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKN        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035
    and crew member 1 has acqual qualification "ACQUAL+A2+AIRPORT+ALF" from 15FEB2018 to 15FEB2021

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_4_SKN
  Scenario: SKN FC rank pilot can fly to ALF in position FP L without airport qualification
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FC         | 01FEB2016  | 01JAN2036 |
           | region          | SKN        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FC         | 01FEB2016  | 01JAN2036 |

    and crew member 1 has qualification "ACQUAL+A2" from 1JAN2018 to 31DEC2035

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1


  @SCENARIO_5_SKN
  Scenario: SKN FP rank pilot can fly to ALF in FP position
    Given Rostering_FC
    Given planning period from 1DEC2020 to 31DEC2020

    Given a crew member with
           | attribute       | value      | valid from | valid to  |
           | crew rank       | FP         | 01FEB2016  | 01JAN2036 |
           | region          | SKN        | 01FEB2016  | 01JAN2036 |
           | base            | STO        | 01FEB2016  | 01JAN2036 |
           | title rank      | FP         | 01FEB2016  | 01JAN2036 |

    and a trip with the following activities
      | act | car | num | dep stn | arr stn | dep             | arr            | ac_typ | code |
      | leg | SK  | 001 | ARN     | ALF     | 20DEC2020 10:00 | 20DEC2020 11:00 | 320    |      |

    and trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then the rule "rules_qual_ccr.alf_forbidden_for_skd_sks_fp" shall pass on leg 1 on trip 1 on roster 1
    and the rule "rules_qual_ccr.qln_arr_airport_ok_fc" shall pass on leg 1 on trip 1 on roster 1
