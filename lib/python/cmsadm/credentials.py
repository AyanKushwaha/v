# [acosta:06/122@07:42] Written as module to enforce singularity

import getpass
import os

#- Credentials -----------------------------------------------------------{{{2

"""
This module will try to find the current user's credentials.
The current, limited implementation uses environment CARMROLE.
"""

id = "nobody"
group = "nobody"
role = "nobody"


def getGroup():
    """ Return group """
    global group
    return group

def getId():
    """ Return loginid """
    global id
    return id

def getRole():
    """ Return user's role """
    global role
    return role

""" Get credentials from system """
_id = getpass.getuser()
if _id:
    id = _id

_role = os.environ.get("CARMROLE")
if _role:
    role = _role

_group = os.environ.get("CARMGROUP")
if _group:
    group = _group

# eof
