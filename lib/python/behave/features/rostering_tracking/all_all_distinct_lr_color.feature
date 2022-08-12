@STUDIO @ALL @ROSTERING @TRACKING @SKCMS-2392 @A2NX
################################################################################
# These are tests to make sure A2L2 legs and trips are visually
# distinct from non-LR fights.
#
################################################################################

Feature: A2L2 should be visually distincts from other flight legs.

  Background: setting up planning period
    Given planning period from 01MAR2020 to 31MAR2020


 Scenario: Two A2NX and two A2 flights.

 Given table aircraft_type additionally contains the following
 | id  | maintype | crewbunkfc | crewbunkcc | maxfc | maxcc | class1fc | class1cc | class2cc | class3cc | version |
 | 35X | A320     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |         |
 | 32Q | A320     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        | LR      |
 | 35A | A350     | 2          | 4          | 4     | 10    | 2        | 1        | 0        | 0        |         |



 Given a trip with the following activities
  | act | num  | dep stn | arr stn | date      | dep   | arr   | ac_typ |
  | leg | 0001 | ARN     | CPH     | 27MAR2020 | 10:00 | 19:00 | 35X    |
  | leg | 0002 | CPH     | GOT     | 28MAR2020 | 10:00 | 19:00 | 32Q    |
  | leg | 0003 | GOT     | CPH     | 29MAR2020 | 10:00 | 19:00 | 35A    |


  # SKD_CC_AG
  Given a crew member with homebase "STO"
  Given crew member 1 has contract "V200"
  Given crew member 1 has a personal activity "F" at station "STO" that starts at 31JAN2019 00:00 and ends at 1FEB2019 23:59

  Given trip 1 is assigned to crew member 1

  When I load ruleset "Tracking"
  When I show "crew" in window 1
  Then rave "studio_config.%leg_color_middle%" shall be "11" on leg 2
