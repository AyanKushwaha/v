"""
Test Timezone
"""


from carmtest.framework import *

from datetime import date, time, timedelta, datetime
from utils.dutycd import pos2dutycd, dutycd2pos


class TestPos2DutyCd(TestFixture):
    "Duty Pos2DutyCd"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    
    def test_001(self): self.assertEqual(pos2dutycd('AH', 'AH'), '')
    def test_002(self): self.assertEqual(pos2dutycd('AH', 'AS'), 'H')
    def test_003(self): self.assertEqual(pos2dutycd('AH', 'AP'), 'H')
    def test_004(self): self.assertEqual(pos2dutycd('AS', 'AH'), 'L')
    def test_005(self): self.assertEqual(pos2dutycd('AS', 'AS'), '')
    def test_006(self): self.assertEqual(pos2dutycd('AS', 'AP'), 'H')
    def test_007(self): self.assertEqual(pos2dutycd('AP', 'AH'), 'LL')
    def test_008(self): self.assertEqual(pos2dutycd('AP', 'AS'), 'L')
    def test_009(self): self.assertEqual(pos2dutycd('AP', 'AP'), '')
    def test_010(self): self.assertEqual(pos2dutycd('FR', 'FR'), '')
    def test_011(self): self.assertEqual(pos2dutycd('FR', 'FP'), 'H')
    def test_012(self): self.assertEqual(pos2dutycd('FR', 'FC'), 'HH')
    def test_013(self): self.assertEqual(pos2dutycd('FP', 'FR'), 'L')
    def test_014(self): self.assertEqual(pos2dutycd('FP', 'FP'), '')
    def test_015(self): self.assertEqual(pos2dutycd('FP', 'FC'), 'H')
    def test_016(self): self.assertEqual(pos2dutycd('FC', 'FR'), 'LL')
    def test_017(self): self.assertEqual(pos2dutycd('FC', 'FP'), 'L')
    def test_018(self): self.assertEqual(pos2dutycd('FC', 'FC'), '')
    def test_019(self): self.assertEqual(pos2dutycd('AH', 'DH'), 'P')
    def test_020(self): self.assertEqual(pos2dutycd('AS', 'DH'), 'P')
    def test_021(self): self.assertEqual(pos2dutycd('AP', 'DH'), 'P')
    def test_022(self): self.assertEqual(pos2dutycd('FR', 'DH'), 'P')
    def test_023(self): self.assertEqual(pos2dutycd('FP', 'DH'), 'P')
    def test_024(self): self.assertEqual(pos2dutycd('FC', 'DH'), 'P')
    def test_025(self): self.assertEqual(pos2dutycd('FC', 'FU'), 'U')
    def test_026(self): self.assertEqual(pos2dutycd('AH', 'AU'), 'U')
    def test_027(self): self.assertEqual(pos2dutycd('XX', 'XX'), '')


class TestDutyCd2Pos(TestFixture):
    "Duty Cd2Pos"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self): self.assertEqual(dutycd2pos('AH', ''), 'AH')
    def test_002(self): self.assertEqual(dutycd2pos('AH', 'H'), 'AP') # special case
    def test_003(self): self.assertEqual(dutycd2pos('AH', 'HH'), 'AP')
    def test_004(self): self.assertEqual(dutycd2pos('AH', 'L'), 'AH')
    def test_005(self): self.assertEqual(dutycd2pos('AH', 'LL'), 'AH')
    def test_006(self): self.assertEqual(dutycd2pos('AS', ''), 'AS')
    def test_007(self): self.assertEqual(dutycd2pos('AS', 'H'), 'AP')
    def test_008(self): self.assertEqual(dutycd2pos('AS', 'HH'), 'AP')
    def test_009(self): self.assertEqual(dutycd2pos('AS', 'L'), 'AH')
    def test_010(self): self.assertEqual(dutycd2pos('AS', 'LL'), 'AH')
    def test_011(self): self.assertEqual(dutycd2pos('AP', ''), 'AP')
    def test_012(self): self.assertEqual(dutycd2pos('AP', 'H'), 'AP')
    def test_013(self): self.assertEqual(dutycd2pos('AP', 'HH'), 'AP')
    def test_014(self): self.assertEqual(dutycd2pos('AP', 'L'), 'AH')
    def test_015(self): self.assertEqual(dutycd2pos('AP', 'LL'), 'AH')
    def test_016(self): self.assertEqual(dutycd2pos('FR', ''), 'FR')
    def test_017(self): self.assertEqual(dutycd2pos('FR', 'H'), 'FP')
    def test_018(self): self.assertEqual(dutycd2pos('FR', 'HH'), 'FC')
    def test_019(self): self.assertEqual(dutycd2pos('FR', 'L'), 'FR')
    def test_020(self): self.assertEqual(dutycd2pos('FR', 'LL'), 'FR')
    def test_021(self): self.assertEqual(dutycd2pos('FP', ''), 'FP')
    def test_022(self): self.assertEqual(dutycd2pos('FP', 'H'), 'FC')
    def test_023(self): self.assertEqual(dutycd2pos('FP', 'HH'), 'FC')
    def test_024(self): self.assertEqual(dutycd2pos('FP', 'L'), 'FR')
    def test_025(self): self.assertEqual(dutycd2pos('FP', 'LL'), 'FR')
    def test_026(self): self.assertEqual(dutycd2pos('FC', ''), 'FC')
    def test_027(self): self.assertEqual(dutycd2pos('FC', 'H'), 'FC')
    def test_028(self): self.assertEqual(dutycd2pos('FC', 'HH'), 'FC')
    def test_029(self): self.assertEqual(dutycd2pos('FC', 'L'), 'FP')
    def test_030(self): self.assertEqual(dutycd2pos('FC', 'LL'), 'FR')
    def test_031(self): self.assertEqual(dutycd2pos('AH', 'P'), 'DH')
    def test_032(self): self.assertEqual(dutycd2pos('AS', 'P'), 'DH')
    def test_033(self): self.assertEqual(dutycd2pos('AP', 'P'), 'DH')
    def test_034(self): self.assertEqual(dutycd2pos('FR', 'P'), 'DH')
    def test_035(self): self.assertEqual(dutycd2pos('FP', 'P'), 'DH')
    def test_036(self): self.assertEqual(dutycd2pos('FC', 'P'), 'DH')
    def test_037(self): self.assertEqual(dutycd2pos('FC', 'D'), 'DH')
    def test_038(self): self.assertEqual(dutycd2pos('AP', 'LXZ'), 'AH')
    def test_039(self): self.assertEqual(dutycd2pos('FC', 'UXZ'), 'FU')
    def test_040(self): self.assertEqual(dutycd2pos('AH', 'HHXZ'), 'AP')
    def test_041(self): self.assertEqual(dutycd2pos('AH', 'U'), 'AU')
    def test_042(self): self.assertEqual(dutycd2pos('AP', 'SL'), 'AH')
    def test_043(self): self.assertEqual(dutycd2pos('FC', 'TU'), 'FU')
    def test_044(self): self.assertEqual(dutycd2pos('DH', 'LL'), 'DH')
    def test_045(self): self.assertEqual(dutycd2pos('FS', ''), 'FU')
    def test_046(self): self.assertEqual(dutycd2pos('FE', ''), 'FU')
    def test_047(self): self.assertEqual(dutycd2pos('FO', ''), 'FU')
    def test_048(self): self.assertEqual(dutycd2pos('FA', ''), 'FP')
    def test_049(self): self.assertEqual(dutycd2pos('AA', ''), 'AH')
