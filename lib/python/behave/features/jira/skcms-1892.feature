Feature: Test salary time for standbys for RP crew

  Background: set up for tracking
    Given Tracking

  Scenario: Test paid time for unused standby, before September 1 2018

    Given planning period from 1MAY2018 to 31MAY2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"


    and crew member 1 has a personal activity "RC" at station "CPH" that starts at 29MAY2018 04:15 and ends at 29MAY2018 12:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 27MAY2018 22:00 and ends at 28MAY2018 22:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 29MAY2018 22:00 and ends at 30MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"


    and crew member 2 has a personal activity "RC" at station "ARN" that starts at 29MAY2018 04:15 and ends at 29MAY2018 12:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 27MAY2018 22:00 and ends at 28MAY2018 22:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 29MAY2018 22:00 and ends at 30MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"


    and crew member 3 has a personal activity "RC" at station "OSL" that starts at 29MAY2018 04:15 and ends at 29MAY2018 12:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 27MAY2018 22:00 and ends at 28MAY2018 22:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 29MAY2018 22:00 and ends at 30MAY2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1MAY2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1JUN2018 0:00"
    and I show "crew" in window 1
    Then rave "report_overtime.%temporary_crew_hours_for_day%(29may2018)" shall be "1:56" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(29may2018)" shall be "6:00" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours_for_day%(29may2018)" shall be "6:00" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for unused standby, after September 1 2018

    Given planning period from 1SEP2018 to 30SEP2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"


    and crew member 1 has a personal activity "RC" at station "CPH" that starts at 29SEP2018 04:15 and ends at 29SEP2018 12:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 27SEP2018 22:00 and ends at 28SEP2018 22:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 29SEP2018 22:00 and ends at 30SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"


    and crew member 2 has a personal activity "RC" at station "ARN" that starts at 29SEP2018 04:15 and ends at 29SEP2018 12:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 27SEP2018 22:00 and ends at 28SEP2018 22:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 29SEP2018 22:00 and ends at 30SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"


    and crew member 3 has a personal activity "RC" at station "OSL" that starts at 29SEP2018 04:15 and ends at 29SEP2018 12:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 27SEP2018 22:00 and ends at 28SEP2018 22:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 29SEP2018 22:00 and ends at 30SEP2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1SEP2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1OCT2018 0:00"
    and I show "crew" in window 1
    Then rave "report_overtime.%temporary_crew_hours_for_day%(29SEP2018)" shall be "6:00" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(29SEP2018)" shall be "6:00" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours_for_day%(29SEP2018)" shall be "6:00" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for callout standby, before September 1 2018

    Given planning period from 1MAY2018 to 31MAY2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0002 | DBV     | CPH     | 25MAY2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0003 | CPH     | OSL     | 25MAY2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0004 | OSL     | CPH     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 1 has a personal activity "R" at station "CPH" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0006 | DBV     | ARN     | 25MAY2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0007 | ARN     | OSL     | 25MAY2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0008 | OSL     | ARN     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 2 has a personal activity "R" at station "ARN" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0010 | DBV     | OSL     | 25MAY2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0011 | OSL     | CPH     | 25MAY2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0012 | CPH     | OSL     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 3 has a personal activity "R" at station "OSL" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1MAY2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1JUN2018 0:00"
    and I show "crew" in window 1
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "12:17" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "12:00" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "12:00" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for callout standby, after September 1 2018

    Given planning period from 1SEP2018 to 30SEP2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0002 | DBV     | CPH     | 25SEP2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0003 | CPH     | OSL     | 25SEP2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0004 | OSL     | CPH     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 1 has a personal activity "R" at station "CPH" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0006 | DBV     | ARN     | 25SEP2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0007 | ARN     | OSL     | 25SEP2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0008 | OSL     | ARN     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 2 has a personal activity "R" at station "ARN" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0010 | DBV     | OSL     | 25SEP2018 | 09:10 | 11:35 | SK  | 320    |
    | leg | 0011 | OSL     | CPH     | 25SEP2018 | 13:30 | 14:40 | SK  | 320    |
    | leg | 0012 | CPH     | OSL     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 3 has a personal activity "R" at station "OSL" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1SEP2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1OCT2018 0:00"
    and I show "crew" in window 1
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "12:00" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "12:00" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "12:00" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for callout standby with split duty, after September 1 2018

    Given planning period from 1SEP2018 to 30SEP2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0004 | DBV     | CPH     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 1 has a personal activity "R" at station "CPH" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0008 | DBV     | ARN     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 2 has a personal activity "R" at station "ARN" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0012 | DBV     | OSL     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 3 has a personal activity "R" at station "OSL" that starts at 25SEP2018 02:00 and ends at 25SEP2018 3:25
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1SEP2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1OCT2018 0:00"
    and I show "crew" in window 1
    # For DK we expect 1/4 payment for started callby hours and full payment for all time between ci and co:
    # 2:00 / 4 + 16:40 - 5:10 = 12:00
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "12:00" on leg 1 on trip 1 on roster 1

    # For SE we expect 1/4 payment for started callby hours and full payment for all time between ci and co:
    # 2:00 / 4 + 16:40 - 5:10 = 12:00
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "12:00" on leg 1 on trip 1 on roster 2

    # For NO we expect 1/4 payment for started callby hours and full payment for time between ci and co,
    # except for time at the hotel which has half payment:
    # 2:00 / 4 + 9:35 - 5:10 + (13:15 - 9:35) / 2 + 16:40 - 13:15 = 0:30 + 4:25 + 3:40 / 2 + 3:25 = 10:10
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "10:10" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for callout standby with split duty, before September 1 2018

    Given planning period from 1MAY2018 to 31MAY2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0004 | DBV     | CPH     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 1 has a personal activity "R" at station "CPH" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0008 | DBV     | ARN     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 2 has a personal activity "R" at station "ARN" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0012 | DBV     | OSL     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 3 has a personal activity "R" at station "OSL" that starts at 25MAY2018 02:00 and ends at 25MAY2018 3:25
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1MAY2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1JUN2018 0:00"
    and I show "crew" in window 1
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "12:17" on leg 1 on trip 1 on roster 1

    # For SE we expect 1/4 payment for started callby hours and full payment for all time between ci and co:
    # 2:00 / 4 + 16:40 - 5:10 = 12:00
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "12:00" on leg 1 on trip 1 on roster 2

    # For NO we expect 1/4 payment for started callby hours and full payment for time between ci and co,
    # except for time at the hotel which has half payment:
    # 2:00 / 4 + 9:35 - 5:10 + (13:15 - 9:35) / 2 + 16:40 - 13:15 = 0:30 + 4:25 + 3:40 / 2 + 3:25 = 10:10
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "10:10" on leg 1 on trip 1 on roster 3


  Scenario: Test paid time for split duty, before September 1 2018

    Given planning period from 1MAY2018 to 31MAY2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0004 | DBV     | CPH     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0008 | DBV     | ARN     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25MAY2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0012 | DBV     | OSL     | 25MAY2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23MAY2018 22:00 and ends at 24MAY2018 22:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25MAY2018 22:00 and ends at 26MAY2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1MAY2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1JUN2018 0:00"
    and I show "crew" in window 1

    # For SE and DK we expect payment for all time between ci and co:
    # 16:40 - 5:10 = 11:30
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "11:30" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours%" shall be "11:30" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "11:30" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours%" shall be "11:30" on leg 1 on trip 1 on roster 2

    # For NO we expect full payment for time between ci and co, except for time at the hotel which has half payment:
    # 9:35 - 5:10 + (13:15 - 9:35) / 2 + 16:40 - 13:15 = 4:25 + 3:40 / 2 + 3:25 = 9:40
    and rave "report_overtime.%temporary_crew_hours_for_day%(25MAY2018)" shall be "9:40" on leg 1 on trip 1 on roster 3
    and rave "report_overtime.%temporary_crew_hours%" shall be "9:40" on leg 1 on trip 1 on roster 3



  Scenario: Test paid time for split duty, after September 1 2018

    Given planning period from 1SEP2018 to 30SEP2018

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | CPH       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKD       |            |          |

    and crew member 1 has contract "V345"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0001 | CPH     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0004 | DBV     | CPH     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 1 is assigned to crew member 1 in position AP
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 1 has a personal activity "F" at station "CPH" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | STO       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKS       |            |          |

    and crew member 2 has contract "V00863"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0005 | ARN     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0008 | DBV     | ARN     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 2 is assigned to crew member 2 in position AP
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 2 has a personal activity "F" at station "ARN" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    Given a crew member with
    | attribute       | value     | valid from | valid to |
    | base            | OSL       |            |          |
    | title rank      | AP        |            |          |
    | region          | SKN       |            |          |

    and crew member 3 has contract "V851"

    and a trip with the following activities
    | act | num  | dep stn | arr stn | date      | dep   | arr   | car | ac_typ |
    | leg | 0009 | OSL     | DBV     | 25SEP2018 | 06:00 | 08:20 | SK  | 320    |
    | leg | 0012 | DBV     | OSL     | 25SEP2018 | 15:15 | 16:25 | SK  | 320    |

    and trip 3 is assigned to crew member 3 in position AP
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 23SEP2018 22:00 and ends at 24SEP2018 22:00
    and crew member 3 has a personal activity "F" at station "OSL" that starts at 25SEP2018 22:00 and ends at 26SEP2018 22:00

    When I set parameter "salary.%salary_month_start_p%" to "1SEP2018 0:00"
    and I set parameter "salary.%salary_month_end_p%" to "1OCT2018 0:00"
    and I show "crew" in window 1

    # For SE and DK we expect payment for all time between ci and co:
    # 16:40 - 5:10 = 11:30
    Then rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "11:30" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours%" shall be "11:30" on leg 1 on trip 1 on roster 1
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "11:30" on leg 1 on trip 1 on roster 2
    and rave "report_overtime.%temporary_crew_hours%" shall be "11:30" on leg 1 on trip 1 on roster 2

    # For NO we expect full payment for time between ci and co, except for time at the hotel which has half payment:
    # 9:35 - 5:10 + (13:15 - 9:35) / 2 + 16:40 - 13:15 = 4:25 + 3:40 / 2 + 3:25 = 9:40
    and rave "report_overtime.%temporary_crew_hours_for_day%(25SEP2018)" shall be "9:40" on leg 1 on trip 1 on roster 3
    and rave "report_overtime.%temporary_crew_hours%" shall be "9:40" on leg 1 on trip 1 on roster 3
