

"""
Create XML file with block-time and duty-time statistics per crew member.
"""

# ../../utils/datadump.py

import utils.datadump as datadump
from report_sources.report_server.rs_if import RSv2_report, argfix


@argfix
@RSv2_report()
def generate(directory):
    """The argument 'directory' will tell in which output directory the
    generated XML file will be stored."""
    return datadump.dump_bt_dt(directory)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
