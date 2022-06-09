#
#$Header: /opt/Carmen/CVS/sk_cms_user/bin/testing/perf_tools/common.py,v 1.2 2009/09/17 09:01:36 adg349 Exp $
#
__version__ = "$Revision: 1.2 $"
"""
common.py
Module for doing:
common class for wrapping an object
@date:17Sep2009
@author: Per Groenberg (pergr)
@org: Jeppesen Systems AB
"""

class WrapObject(object):
    def __getattribute__(self, name):
        if name == "_child":
            return object.__getattribute__(self, "_child")
        return getattr(object.__getattribute__(self, "_child"), name)

    def __getitem__(self, item):
        return object.__getattribute__(self, "_child")[item]
    
    def __iter__(self):
        return self._child.__iter__()
    
    def next(self):
        return self._child.next()
    
    def __str__(self):
        return str(object.__getattribute__(self, "_child"))
