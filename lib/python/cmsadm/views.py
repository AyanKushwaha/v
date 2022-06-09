
# Module that handles security views.
#
# [acosta:06/122@07:53] Moved to module instead of class.
# [acosta:07/128@13:03] Uses TM, also LDAP search strings are changed, to remove
#                       white space.

"""
Views are collections of objects.
Access control is applied to the whole collection, not the single
objects within the view.

If an object (e.g. a table) exists in several views, the user will get
the largest value of rights.

Example:
    Table 'crew' exists in two views, one with read-only rights and the
    other with read-write rights. If the user's role has rights to both
    views, then the user will have read-write rights to the table 'crew'.
"""

import cmsadm.credentials
from tm import TM


#= functions ============================================================={{{1

#- getViews() ------------------------------------------------------------{{{2
def getViews():
    """ Return the views to which the user has at least read access """
    global views
    return views


#- getViewACL(view) ------------------------------------------------------{{{2
def getViewACL(view):
    """ Return access rights linked to a given view """
    global views
    return views[view]


#- getObjectNames(type) --------------------------------------------------{{{2
def getObjectNames(type = 'TABLE'):
    """ Return object names to which user has at least read access """
    global _objectlist
    if _objectlist.has_key(type):
        return _objectlist[type].keys()
    else:
        return []


#- getObjectNamesFor(view, type) -----------------------------------------{{{2
def getObjectNamesFor(view, type = 'TABLE'):
    """
    Return object names from a particular security view, where user has 
    at least read access and where object type is of type 'type'.
    """
    list = []
    object_filter = '(&(cms_view=%s)(cms_object_type=%s))' % (view, type)
    for object in TM.cms_view_objects.search(object_filter):
        list.append(str(object.cms_object_name))
    return list


#- getACL(name, type) ----------------------------------------------------{{{2
def getACL(name, type = 'TABLE'):
    """
    Return a number that corresponds to the user's rights for a given
    object with name 'name' and of type 'type'. (ACL = Access Control List)
    """
    global _objectlist
    if _objectlist.has_key(type):
        td = _objectlist[type]
        if td.has_key(name):
            return td[name]
    return 0


#= main =================================================================={{{1

# This code will be executed once, the first time this module is imported

_objectlist = { 'DUMMY': { 'DUMMY': 0 } }
views = {}

# Search for all views where the user has at least right to read
role_filter = '(&(cms_role=%s)(cms_view_acl>1))' % (cmsadm.credentials.role)
for view in TM.cms_views.search(role_filter):
    view_name = str(view.cms_view)
    view_acl = int(view.cms_view_acl)
    views[view_name] = view_acl

    # Get all objects in a view
    object_filter = '(&(cms_view=%s))' % (view_name)
    for object in TM.cms_view_objects.search(object_filter):
        type = str(object.cms_object_type)
        name = str(object.cms_object_name)
        if _objectlist.has_key(type):
            # If dictionary exists, check if the object with name 'name'
            # has ACL connected.
            td = _objectlist[type]
            if td.has_key(name):
                stored_acl = td[name]
                if view_acl > stored_acl:
                    td[name] = view_acl
            else:
                td[name] = view_acl
        else:
            # Add new dictionary for the object type
            nd = {}
            nd[name] = view_acl
            _objectlist[type] = nd


#= modeline =============================================================={{{1
# vim: set fdm=marker:
# eof
