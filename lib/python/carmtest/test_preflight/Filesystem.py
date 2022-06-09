'''
Created on 21 Dec 2011

@author henrikal
'''

from carmtest.framework import *

import os,stat

class preflight_001_Filesystem(TestFixture):
    """
    Tests that the CMS environment is configured correctly.
    """

    def __init__(self):
        self.carmusr = os.getenv("CARMUSR")

    def test_001_carmsys_symlinks(self):
        assert self.is_path_to_carmsys(os.path.join(self.carmusr, 'current_carmsys_cct'))
        assert self.is_path_to_carmsys(os.path.join(self.carmusr, 'current_carmsys_cas'))
        assert self.is_path_to_carmsys(os.path.join(self.carmusr, 'current_carmsys_cmp'))
        assert self.is_path_to_carmsys(os.path.join(self.carmusr, 'current_carmsys_bid'), sys_type='bid')

    def test_002_check_exec_flags(self):
        assert self.is_file_executable(os.path.join(self.carmusr, 'bin/launcher/manpower'))
        assert self.is_file_executable(os.path.join(self.carmusr, 'bin/launcher/tableeditor'))
        assert self.is_file_executable(os.path.join(self.carmusr, 'bin/launcher/wave'))

    def test_003_check_carmtmps(self):
        assert self.is_path_to_carmtmp(os.path.join(self.carmusr, 'current_carmtmp'))
        assert self.is_path_to_carmtmp(os.path.join(self.carmusr, 'current_carmtmp_cas'))
        assert self.is_path_to_carmtmp(os.path.join(self.carmusr, 'current_carmtmp_cct'))
        assert self.is_path_to_carmtmp(os.path.join(self.carmusr, 'current_carmtmp_cmp'))

    def is_path_to_carmsys(self, path, sys_type=None):
        if not (os.path.islink(path) or os.path.isdir(path)):
            raise(Exception("%s is neither link or dir" % (path)))
        if sys_type == 'bid':
            # Improvement?: implement a check to see if some expected bid file exists,
            # e.g. interbids-release-*.zip
            pass
        else:
            carmsys_file = os.path.join(path, 'CONFIG')
            if not (os.path.exists(carmsys_file) and os.path.isfile(carmsys_file)):
                raise(Exception("%s does not seem like a valid CARMSYS" % (path)) )
        return True

    def is_path_to_carmtmp(self, path):
        if not (os.path.islink(path) or os.path.isdir(path)):
            raise(Exception("%s is neither link or dir" % (path)))
        if not self.check_group(path):
            raise(Exception("Writeable flag not set or incorrect group on %s" % (path)))
        return True

    def is_file_executable(self, path):
        if not os.path.isfile(path):
            raise(Exception("%s is not a file" % (path)))
        if not os.access(path, os.X_OK):
            raise(Exception("%s has no executable flag set" % (path)))
        return True

    def check_group(self, path):
        #gid = os.getgid()
        groups = os.getgroups()
        s = os.stat(path)
        mode_for_path = s[stat.ST_MODE]
        group_for_path = s[stat.ST_GID]
        return (mode_for_path & stat.S_IWGRP) and (group_for_path in groups)
