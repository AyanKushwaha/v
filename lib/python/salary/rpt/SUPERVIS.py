
# changelog {{{2
# [acosta:07/220@13:58] First modular email report.
# [acosta:07/277@12:37] Renamed to SUPERVIS.py because of length constraints.
# }}}

"""
Interface 44.2 Inst. Allowance
"""

from salary.rpt import EmailReport


class DK(EmailReport):
    pass


class NO(EmailReport):
    pass


class SE(EmailReport):
    pass


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
