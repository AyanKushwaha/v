

"""
Set up logging for cio.
"""

import logging

__console = logging.StreamHandler()
__console.setFormatter(logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s'))
__rootlogger = logging.getLogger('')


if len(__rootlogger.handlers) == 0:
    __rootlogger.addHandler(__console)


log = logging.getLogger('cio')


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
