
# -*- coding: latin-1 -*-
# changelog {{{2
# [acosta:06/313@15:08] Removed unnecessary import
# [acosta:07/057@14:44] Revised, added header-info record and end-record to follow new spec.
# }}}

"""
Norwegian salary system.
Flat file format.
"""

from salary.fmt import SAP

class NO_FLAT(SAP):
    """ Utilizes common SAP format """
    pass

# EOF
