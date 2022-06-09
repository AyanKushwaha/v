
# changelog {{{2
# [acosta:06/313@15:04] Removed unnecessary import
# [acosta:07/057@13:24] The spec of Danish salary records has changed.
# }}}

"""
Danish salary system.
Flat-file format.
"""

from salary.fmt import SAP

class DK_FLAT(SAP):
    """ Utilizes common SAP format """
    pass

# EOF
