'''
Created on 16 feb 2010

@author: rickard
'''

from carmtest.framework import *
import os


class data_001_Accumulator(DaveTestFixture):
    """
    Tests accumulator
    """
    
    @REQUIRE("ExtensiveTestsEnabled")
    @REQUIRE("NotMigrated")
    def __init__(self):
        pass
    
    def test_001_accumulator(self):
        os.system(os.getenv("CARMUSR")+"/bin/accumulators/accumulator.sh")
        pass

    def test_002_accumulator(self):
        logdirectory = os.getenv("CARMUSR") + "/tmp_cct/logfiles/"
        filelist = os.listdir(logdirectory)
        filelist = filter(lambda x: not os.path.isdir(x), filelist) # filter out directories
        partial_file_name = "accumulator"
        filelist = filter(lambda x: x.find(partial_file_name) > -1, filelist) # Removes the files that don't match the partial file name from the list

        filelist.sort(key=lambda x: x[1])
        filelist.reverse()

        errors = 0
        accumulator_strings = 0
        logfile = open(logdirectory + filelist[0])
        for line in logfile.readlines():
            if "error" in line:
                errors += 1
            if "Accumulator.savePlan: Saving plan..." in line or "Accumulator.start:: done. Exiting..." in line:
                accumulator_strings += 1

        if errors:
            self.fail("%s error(s) found in logfile" % errors)
        elif accumulator_strings >= 2:
            pass
        else:
            self.fail("No \"error\" found in logfile but \"Accumulator.start:: done\" was not found")
        logfile = None
