

"""
Test of Rave evaluation on Report Server
"""


import carmensystems.rave.api as rave


default_dest = [('default', {})]


def generate(arg):
    (a, k) = arg
    L = []
    for value in rave.eval('sp_crew', *a):
        L.append({
            'content': str(value), 
            'content-type': "text/plain", 
            'destination': default_dest
        })
    return L, False


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
