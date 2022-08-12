Feature: Test ZFTT LIFUS checkin times

  Background: set up for tracking
    Given Tracking
    Given planning period from 1MAY2017 to 31MAY2017

  Scenario: Test check in time for ZFTT LIFUS student and instructor on CONV TYPERATING course

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 
    Given crew member 1 has the following training need
    | part | course          | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | CONV TYPERATING | ZFTT LIFUS | 27FEB2017  | 05JUN2017  | 4       | 0        | A4     |

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |

    Given crew member 2 has qualification "ACQUAL+A4" from 1FEB2017 to 01JAN2036 
    Given crew member 2 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 1FEB2017 to 01JAN2036

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 3 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 09MAY2017 | 10:25 | 21:45 | SK  | 34A    |
    | leg | 0002 | SFO     | CPH     | 11MAY2017 | 00:35 | 11:15 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC
    Given trip 1 is assigned to crew member 3 in position FP


    When I show "crew" in window 1
    Then rave "leg.%check_in%" shall be "1:50" on leg 1 on trip 1 on roster 1
    and rave "leg.%check_in%" shall be "1:50" on leg 1 on trip 1 on roster 2
    and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 3


  Scenario: Test check in time for ZFTT LIFUS student and instructor on CCQ-A3A4 course

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 
    Given crew member 1 has the following training need
    | part | course   | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | CCQ-A3A4 | ZFTT LIFUS | 27FEB2017  | 05JUN2017  | 4       | 0        | A4     |

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |

    Given crew member 2 has qualification "ACQUAL+A4" from 1FEB2017 to 01JAN2036 
    Given crew member 2 has acqual qualification "ACQUAL+A4+INSTRUCTOR+TRI" from 1FEB2017 to 01JAN2036

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 3 has qualification "ACQUAL+A4" from 27FEB2017 to 01JAN2036 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 09MAY2017 | 10:25 | 21:45 | SK  | 34A    |
    | leg | 0002 | SFO     | CPH     | 11MAY2017 | 00:35 | 11:15 | SK  | 34A    |
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC
    Given trip 1 is assigned to crew member 3 in position FP


    When I show "crew" in window 1
    Then rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 1
    and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 2
    and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 3


  Scenario: Test check in time for ZFTT LIFUS student and instructor on CCQ-A4A3 course

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 1 has qualification "ACQUAL+A3" from 27FEB2017 to 01JAN2036 
    Given crew member 1 has the following training need
    | part | course   | attribute  | valid from | valid to   | flights | max days | acqual |
    | 1    | CCQ-A4A3 | ZFTT LIFUS | 27FEB2017  | 05JUN2017  | 4       | 0        | A3     |

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FC        |            |          |

    Given crew member 2 has qualification "ACQUAL+A3" from 1FEB2017 to 01JAN2036 
    Given crew member 2 has acqual qualification "ACQUAL+A3+INSTRUCTOR+TRI" from 1FEB2017 to 01JAN2036

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | FP        |            |          |

    Given crew member 3 has qualification "ACQUAL+A3" from 27FEB2017 to 01JAN2036 

    Given a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | SFO     | 09MAY2017 | 10:25 | 21:45 | SK  | 33A    |
    | leg | 0002 | SFO     | CPH     | 11MAY2017 | 00:35 | 11:15 | SK  | 33A    |
    Given trip 1 is assigned to crew member 1 in position FP with attribute TRAINING="ZFTT LIFUS"
    Given trip 1 is assigned to crew member 2 in position FC
    Given trip 1 is assigned to crew member 3 in position FP


    When I show "crew" in window 1
    Then rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 1
    and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 2
    and rave "leg.%check_in%" shall be "1:20" on leg 1 on trip 1 on roster 3
