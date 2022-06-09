
# -*- coding: latin-1 -*-
# [acosta:06/313@15:05] Redesign, added coding.

"""
Danish salary system.
HTML format.
"""

from salary.fmt import HTMLFormatter

class DK_HTML(HTMLFormatter):
    class Headings:
        admcode   = 'Slag'
        amount    = 'Beløb'
        extartid  = 'Slag'
        extperkey = 'Extperkey'
        extsys    = 'Lønkontor'
        firstdate = 'Første dato'
        lastdate  = 'Sidste dato'
        note      = 'Bemærkning'
        runid     = 'Løbenummer'
        starttime = 'Dato før køring'
        selector  = 'Udvalg'
        total     = 'Samlet'

# EOF
