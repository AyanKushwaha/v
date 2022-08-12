Feature: Test visualization of A2NX qualified crew members


 
 @SCENARIO_1
  Scenario: Check that FD with POSITION A2NX and ACQUAL A2, A3 is displayed correctly
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A2     |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A2NXA3" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A2NX A3" on leg 1 on trip 1 on roster 1

 @SCENARIO_2
  Scenario: Check that CC with ACQUAL 38 AL and POSITION A2NX is displayed correctly
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | CC        |            |          |

    Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+38" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+AL" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A2     |


    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A2NXAL38" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A2NX 38 AL" on leg 1 on trip 1 on roster 1

 @SCENARIO_3
  Scenario: Check that FC with A2NX without ACQUAL A2 displays LR
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A3 LR" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A3 LR" on leg 1 on trip 1 on roster 1

 @SCENARIO_4
  Scenario: A2NX A3 A5 in case A5 is included in MFF case to see if working as expected
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A2NXA3A5" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A2NX A3 A5" on leg 1 on trip 1 on roster 1


 @SCENARIO_5
  Scenario: Check that FD with ACQUAL A2, A3 and without POSITION A2NX is displayed correctly
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A2     |

    Given trip 1 is assigned to crew member 1 in position FP

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A2A3" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A2 A3" on leg 1 on trip 1 on roster 1

 @SCENARIO_6
  Scenario: Check that CC with ACQUAL 38 AL and without POSITION A2NX is displayed correctly
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | CC        |            |          |

    Given crew member 1 has qualification "ACQUAL+38" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+AL" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A2     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A2     |


    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "ALA238" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "38 AL A2" on leg 1 on trip 1 on roster 1

 @SCENARIO_7
  Scenario: Check that FC with A2NX without ACQUAL A2 or POSITION A2NX displays correctly
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A3" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A3" on leg 1 on trip 1 on roster 1

 @SCENARIO_8
  Scenario: A3 A5 in case A5 is included in MFF case, without POSITION A2NX to see if working as expected
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A2" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A3" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "ACQUAL+A5" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "A2A3A5" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "A2 A3 A5" on leg 1 on trip 1 on roster 1


 @SCENARIO_9
  Scenario: No active ac qual and POSITION A2NX should show LR
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+A2NX" from 1JAN2020 to 31DEC2035
    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be " LR" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be " LR" on leg 1 on trip 1 on roster 1


 @SCENARIO_10
  Scenario: No active ac qual and no POSITION A2NX should show nothing
    Given Tracking

    Given planning period from 1MAR2020 to 31MAR2020

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | ARN       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "POSITION+LCP" from 1JAN2020 to 31DEC2035

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | OSL     | AMS     | 12MAR2020 | 10:00 | 11:00 | SK  | A3     |
    | leg | 0002 | AMS     | OSL     | 12MAR2020 | 12:00 | 13:00 | SK  | A3     |

    Given trip 1 is assigned to crew member 1

    When I show "crew" in window 1

    Then rave "crg_info.%ac_quals%" shall be "" on leg 1 on trip 1 on roster 1
    Then rave "crg_info.%aircraft_qlns%" shall be "" on leg 1 on trip 1 on roster 1
