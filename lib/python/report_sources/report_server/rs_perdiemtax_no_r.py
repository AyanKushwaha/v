

"""
Per Diem Tax (NO) Release.
Currently a no-op. 

(In the future this should be handled the same way as convertible crew, using
accounts.)
"""

from report_sources.report_server.rs_if import argfix, add_reportprefix
import salary.run as run


@argfix
@add_reportprefix
def generate(*a, **k):
    """Currently a no-op."""
    # return run.autorelease(run.RunData(extsys="NO", runtype="PERDIEMTAX"))
    return [], False

