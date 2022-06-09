'''
Created on 7 Jun 2012

@author henrikal
'''

from carmtest.framework import *

import subprocess

class preflight_001_Commands(TestFixture):
    """
    Tests that commands / programs used by the CMS system are installed.
    """

    @REQUIRE("NotStudio")
    def test_001_check_haproxy(self):
        subprocess.check_call(["haproxy", "-v"])
