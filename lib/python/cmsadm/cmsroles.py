

"""
Functions to maintain the users_$SITE.xml files.
"""

# Read notes below for suggested usage.

import os
import shutil
import subprocess 
import sys

from tempfile import mkstemp
from optparse import OptionParser
from xml.dom.minidom import parse
from utils.edifact import latin1_to_edifact

__all__ = ['CMSUserHandler', 'useradd', 'usermod', 'userdel', 'userlist', 'rolelist', 'CMSRoleError']
__version__ = '$Revision$'

default_role_file = 'roles.xml'
default_user_file = 'users_$SITE.xml'
default_encoding = 'latin_1'


# classes ================================================================{{{1

# CMSRoleError -----------------------------------------------------------{{{2
class CMSRoleError(Exception):
    """ Signals usage or option errors. """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# ConfigFile -------------------------------------------------------------{{{2
class ConfigFile:
    """ Base class for reading and manipulating XML config file. """
    def __init__(self, f):
        try:
            self.dom = parse(f)
        except Exception, e:
            # Add some extra info to make it easier to locate syntax errors.
            raise CMSRoleError("XML parsing error in file %s - %s." % (f, e))
        self._data = None

    # Note that the attribute self.data is defined in subclasses.

    def __contains__(self, name):
        """ Check if data contains name. """
        return name in self.data

    def __getitem__(self, key):
        """ Return the XML node for a user/role. """
        return self.data[key]

    def __iter__(self):
        """ Loop over data (dictionary). """
        return iter(self.data)

    def __str__(self):
        """ Return file name. """
        return str(self.file)

    def reload(self):
        """ Force a reload by resetting self._data. """
        self._data = None

    def toXML(self):
        """ Return document as XML. """
        # small fix to add an extra newline between comment and root element
        # [acosta:07/184@00:17] This did not work with minidom, any other suggestions?
        #self.dom.insertBefore(self.dom.createTextNode('\nAPA\n'), self.dom.firstChild)

        # small fix to add extra newline after last record
        self.dom.documentElement.appendChild(self.dom.createTextNode('\n'))

        output = self.dom.toxml(encoding="iso-8859-1")
        # [acosta:07/185@12:18] Another fix to make prettier output
        return '>\n<'.join(output.split('><'))

    def write(self):
        """ Write resulting XML document to file. """
        # BZ 32389 - make a backup copy first and move the modified file if
        # everything went alright.
        fd, fn = mkstemp(dir=os.environ['CARMTMP'])
        try:
            f = open(fn, "w")
            f.write(self.toXML())
            f.close()
            shutil.copyfile(fn, self.file)
            os.unlink(fn)
        except Exception, e:
            # Add some extra info to make it easier to locate syntax errors.
            raise CMSRoleError("Problems writing to file %s - %s." % (self.file, e))

    # These functions have to be defined in subclasses
    def add(self, *a, **k): raise NotImplementedError
    def mod(self, *a, **k): raise NotImplementedError
    def delete(self, *a, **k): raise NotImplementedError
    def getData(self): raise NotImplementedError

    def _check_env(self, *envvar):
        """ Check if the environment variables given by envvar exist. """
        missing = []
        for env in envvar:
            if not env in os.environ:
                missing.append(env)
        if missing:
            if len(missing) > 1:
                raise CMSRoleError("The environment vars %s are not defined." % (missing))
            else:
                raise CMSRoleError("The environment %s is not defined." % (missing))

    def _clear_ws(self, node):
        """ Removes textnodes containing only white space. """
        prevnode = node.previousSibling
        if prevnode.nodeType == node.TEXT_NODE:
            # Remove adjacent (uninteresting) textnode
            if str(prevnode.data).strip() == '':
                prevnode.parentNode.removeChild(prevnode)

    def _reformat(self, node):
        """
        Reformat an element by removing interspaced white space, and then
        fill in white space to give nice layout.
        """
        # first remove white space ..
        # use list comprehension to avoid unwanted side effects
        for n in [x for x in node.childNodes]:
            if n.nodeType == node.TEXT_NODE:
                if str(n.data).strip() == '':
                    n.parentNode.removeChild(n)
        # ... then put the white space back again :-)
        for n in [x for x in node.childNodes]:
            if n.nodeType == node.ELEMENT_NODE:
                n.parentNode.insertBefore(self.dom.createTextNode('\n' + 6 * ' '), n)
        node.appendChild(self.dom.createTextNode('\n' + 4 * ' '))


# RoleFile ---------------------------------------------------------------{{{2
class RoleFile(ConfigFile):
    """ Manipulate the file 'roles.xml'. """
    def __init__(self, f):
        if f is None:
            self._check_env('CARMUSR', 'SITE')
            self.file = os.path.expandvars(os.path.join('$CARMUSR', 'etc', default_role_file))
        else:
            self.file = f
        if not os.access(self.file, os.F_OK):
            x = open(self.file, "w")
            print >>x, "<roles>\n</roles>\n"
            x.close()
        ConfigFile.__init__(self, self.file)

    def getData(self):
        """ Fill in internal dictionary of users -> nodes. """
        if self._data is None:
            self._data = {}
            for roles in self.dom.getElementsByTagName('roles'):
                for role in roles.getElementsByTagName('role'):
                    if role.hasAttribute('name'):
                        self._data[str(role.getAttribute('name'))] = role
        return self._data
    data = property(getData)

    def ls(self, *roles, **opts):
        """ list roles. """
        if len(roles) > 0:
            if 'long' in opts and opts['long']:
                return (str(RoleFormatter(role, self)) for role in roles)
            else:
                return (role for role in roles if role in self)
        else:
            if 'long' in opts and opts['long']:
                return (str(RoleFormatter(x, self)) for x in self)
            else:
                return iter(self)


# UserFile ---------------------------------------------------------------{{{2
class UserFile(ConfigFile):
    """ Manipulate the file 'users_$SITE.xml'. """
    def __init__(self, f):
        if f is None:
            self._check_env('CARMUSR', 'SITE')
            self.file = os.path.expandvars(os.path.join('$CARMUSR', 'etc', default_user_file))
        else:
            self.file = f
        if not os.access(self.file, os.F_OK):
            x = open(self.file, "w")
            print >>x, "<users>\n</users>\n"
            x.close()
        ConfigFile.__init__(self, self.file)

    def getData(self):
        """ Fill in internal dictionary of users -> nodes. """
        if self._data is None:
            self._data = {}
            for users in self.dom.getElementsByTagName('users'):
                for user in users.getElementsByTagName('user'):
                    if user.hasAttribute('name'):
                        self._data[str(user.getAttribute('name'))] = user
        return self._data
    data = property(getData)

    def add(self, login, comment=None, roles=None, fullname=None):
        """ Add user to the CMS system. """
        users = self.dom.getElementsByTagName('users')[0]
        nl = users.appendChild(self.dom.createTextNode('\n' + 4 * ' '))
        self._clear_ws(nl)

        node = users.appendChild(self.dom.createElement('user'))
        node.setAttribute('name', login)
        if not comment is None:
            c = node.appendChild(self.dom.createElement('comment'))
            c.appendChild(self.dom.createTextNode(comment))
        if not fullname is None:
            node.setAttribute('fullname', latin1_to_edifact(fullname, 'UNOB'))
        for role in roles:
            r = node.appendChild(self.dom.createElement('role'))
            r.appendChild(self.dom.createTextNode(role))
        self._reformat(node)

        users.appendChild(node)
        self.reload()

    def delete(self, login):
        node = self.data[login]
        self._clear_ws(node)
        node.parentNode.removeChild(node)
        self.reload()

    def mod(self, login, comment=None, roles=None, fullname=None):
        node = self.data[login]
        if not comment is None:
            for old_comment in node.getElementsByTagName('comment'):
                node.removeChild(old_comment)
            c = node.appendChild(self.dom.createElement('comment'))
            c.appendChild(self.dom.createTextNode(comment))
        if not fullname is None:
            node.setAttribute('fullname', latin1_to_edifact(fullname, 'UNOB'))
        if not roles is None:
            for old_role in node.getElementsByTagName('role'):
                node.removeChild(old_role)
            for role in roles:
                r = node.appendChild(self.dom.createElement('role'))
                r.appendChild(self.dom.createTextNode(role))
        self._reformat(node)

    def ls(self, *users, **opts):
        """ list logins. """
        if len(users) > 0:
            return (str(UserFormatter(user, self)) for user in users if self.is_eligible(user, opts))
        else:
            if 'long' in opts and opts['long']:
                return (str(UserFormatter(x, self)) for x in self if self.is_eligible(x, opts))
            else:
                return (x for x in self if self.is_eligible(x, opts))

    def is_eligible(self, user, opts):
        """ Check if the user has the role that makes him/her eligible for
        presentation. """
        if user in self:
            user = self[user]
        else:
            return False
        if 'roles' in opts and opts['roles'] is not None:
            userroles = get_text(user, 'role')
            for role in opts['roles']:
                if role in userroles:
                    return True
            return False
        return True


# CMSUserHandler ---------------------------------------------------------{{{2
class CMSUserHandler:
    """
    Uses RoleFile and UserFile objects to check legalities and to invoke the
    correct methods in these classes.
    """
    def __init__(self, rolefile=None, userfile=None):
        self.rolefile = RoleFile(rolefile)
        self.userfile = UserFile(userfile)

    def add(self, login, *a, **k):
        """ add user """
        if login in self.userfile:
            raise CMSRoleError("The user '%s' is already defined in '%s' (can't be added)." % (login, self.userfile))
        self.__op('add', login, *a, **k)

    def mod(self, login, *a, **k):
        """ modify user """
        if not login in self.userfile:
            raise CMSRoleError("The user '%s' is not defined in '%s' (can't be modified)." % (login, self.userfile))
        self.__op('mod', login, *a, **k)

    def delete(self, login, **k):
        """ remove user """
        if not login in self.userfile:
            raise CMSRoleError("The user '%s' is not defined in '%s'." % (login, self.userfile))
        self.userfile.delete(login)

    def toXML(self):
        """ return XML formatted document """
        return self.userfile.toXML()

    def write(self):
        """ write result to file """
        return self.userfile.write()

    def __is_system_user(self, name):
        """ Check if user is an Operating System user. """
        try:
            retcode = subprocess.Popen(['getent', 'passwd', name], stdout=open("/dev/null", "w")).wait()
            if retcode:
                raise subprocess.CalledProcessError(retcode, "Command %s returned non-zero exit status." % ('getent'))
            return True
        except:
            return False

    def __get_fullname(self, name):
        """ Return the gecos field from the passwd entry. """
        try:
            output = subprocess.Popen(['getent', 'passwd', name], stdout=subprocess.PIPE).communicate()[0]
            gecos = output.split(':')[4]
            # [acosta:07/185@13:31] Apparently the gecos field can be subdivided...
            return gecos.rstrip(',')
        except:
            return None

    def __op(self, op, login, comment=None, roles=(), fullname=None, useGecos=False, relaxOSUser=False, **k):
        """ Used by add and mod to do the real work. """
        if roles is None or len(roles) == 0:
            raise CMSRoleError("No role specified.")
        for role in roles:
            if not role in self.rolefile:
                raise CMSRoleError("The role '%s' is not defined in '%s'." % (role, self.rolefile))
        if not relaxOSUser:
            if not self.__is_system_user(login):
                raise CMSRoleError("The user '%s' does not exist as an Operating System user." % (login))
        if fullname is None and useGecos:
            fullname = self.__get_fullname(login)
        getattr(self.userfile, op)(login=login, comment=comment, roles=roles, fullname=fullname)


# RoleFormatter ----------------------------------------------------------{{{2
class RoleFormatter:
    """ For formatting lists of roles on the CMS system. """

    width = 15

    def __init__(self, role, caller):
        self.role = role
        self.caller = caller

    def __str__(self):
        node = self.caller[self.role]
        comments = get_text(node, 'comment')
        rule_sets = get_text(node, 'rule_set')
        parameter_files = get_text(node, 'parameter_file')
        applications = get_text(node, 'application')
        L = [' - %-*s : %s' % (self.width, "name", self.role)]
        if len(comments) > 0:
            L.append('   %-*s : %s' % (self.width, 'comment', ', '.join(x for x in comments)))
        if len(rule_sets) > 0:
            L.append('   %-*s : %s' % (self.width, 'rule_set', ', '.join(x for x in rule_sets)))
        if len(parameter_files) > 0:
            L.append('   %-*s : %s' % (self.width, 'parameter_file', ', '.join(x for x in parameter_files)))
        if len(applications) > 0:
            L.append('   %-*s : %s' % (self.width, 'application', ', '.join(x for x in applications)))
        return '\n'.join(L)


# UserFormatter ----------------------------------------------------------{{{2
class UserFormatter:
    """ For formatting lists of users on the CMS system. """

    width = 10

    def __init__(self, user, caller):
        self.user = user
        self.caller = caller

    def __str__(self):
        node = self.caller[self.user]
        fullname = str(node.getAttribute('fullname').encode('latin_1'))
        comments = get_text(node, 'comment')
        roles = get_text(node, 'role')
        L = [' - %-*s : %s' % (self.width, "name", self.user)]
        if not fullname is None:
            L.append('   %-*s : %s' % (self.width, "fullname", fullname))
        if len(comments) > 0:
            L.append('   %-*s : %s' % (self.width, 'comment', ', '.join(x for x in comments)))
        if len(roles) > 0:
            L.append('   %-*s : %s' % (self.width, 'roles', ', '.join(x for x in roles)))
        return '\n'.join(L)


# functions =============================================================={{{1

# cms_optparser ----------------------------------------------------------{{{2
def cms_optparser(opt):
    """ Return instance of OptionParser tailored for the cmsadduser script. """

    def split_roles(option, opt_str, value, parser):
        """ Callback to optparser that splits role string into tuple. """
        parser.values.roles = value.split(',')

    if opt == 'add':
        description = "Administer a new user login on the CMS system."
    elif opt == 'mod':
        description = "Modify a user's login information on the CMS system."
    elif opt == 'delete':
        description = "Delete a user's login from the CMS system."
    elif opt == 'userlist':
        description = "List users on the CMS system."
    elif opt == 'rolelist':
        description = "List roles on the CMS system."

    if opt == 'userlist':
        usage = "usage: %prog [options] [login [login ...]]"
    elif opt == 'rolelist':
        usage = "usage: %prog [options] [role [role ...]]"
    elif opt == 'add':
        usage = "usage: %prog -R role[,role...] [options] login"
    else:
        usage = "usage: %prog [options] login"

    parser = OptionParser(usage=usage, version="%%prog %s" % (__version__), description=description)

    if opt in ('userlist', 'rolelist'):
        parser.add_option("-l", "--long", 
            action="store_true", dest="long", default=False, 
            help="Gives a fuller listing."
        )
    else:
        parser.add_option("-n", "--no-commit", 
            action="store_true", dest="nocommit", default=False, 
            help="Print the result of the changes to stdout instead of writing to the file."
        )

    if opt in ('add', 'mod', 'userlist'):
        parser.add_option("-R", "--roles", 
            action="callback",
            callback=split_roles,
            type="string",
            nargs=1,
            help="One or more comma-separated roles defined in roles.xml.",
            metavar="role[,role...]")

    if opt in ('add', 'mod'):
        parser.add_option("-f", "--fullname",
            dest="fullname",
            help="Full name of the user.",
            metavar="fullname")
        parser.add_option("-c", "--comment",
            dest="comment",
            help="Add this comment to the user record.",
            metavar="comment")
        parser.add_option("-G", "--gecos",
            action="store_true",
            dest="useGecos",
            default=False,
            help="If the -f flag was not given, get the full name from the gecos field of the authority system.")
        parser.add_option("-x", "--relax-checks",
            action="store_true", dest="relaxOSUser", default=False,
            help="Don't check if the user exists as an OS user.")

    if opt in ('add', 'mod', 'delete', 'userlist'):
        parser.add_option("-u", "--userfile",
            dest="userfile",
            help="Use this file instead of the default '%s'." % (default_user_file),
            metavar="userfile")
    if opt in ('add', 'mod', 'delete', 'rolelist'):
        parser.add_option("-r", "--rolefile",
            dest="rolefile",
            help="Get available roles from this file instead of the default '%s'." % (default_role_file),
            metavar="rolefile")

    return parser


# useradd ----------------------------------------------------------------{{{2
def useradd(*a, **k):
    uh = CMSUserHandler(userfile=k.get('userfile', None), rolefile=k.get('rolefile', None))
    uh.add(*a, **k)
    if 'nocommit' in k and k['nocommit']:
        print uh.toXML()
    else:
        uh.write()


# usermod ----------------------------------------------------------------{{{2
def usermod(*a, **k):
    uh = CMSUserHandler(userfile=k.get('userfile', None), rolefile=k.get('rolefile', None))
    uh.mod(*a, **k)
    if 'nocommit' in k and k['nocommit']:
        print uh.toXML()
    else:
        uh.write()


# userdel ----------------------------------------------------------------{{{2
def userdel(*a, **k):
    uh = CMSUserHandler(userfile=k.get('userfile', None), rolefile=k.get('rolefile', None))
    uh.delete(*a, **k)
    if 'nocommit' in k and k['nocommit']:
        print uh.toXML()
    else:
        uh.write()


# userlist ---------------------------------------------------------------{{{2
def userlist(*a, **k):
    uf = UserFile(k.get('userfile', None))
    for x in uf.ls(*a, **k):
        print x


# rolelist ---------------------------------------------------------------{{{2
def rolelist(*a, **k):
    rf = RoleFile(k.get('rolefile', None))
    for x in rf.ls(*a, **k):
        print x


# get_text ---------------------------------------------------------------{{{2
def get_text(node, tag):
    """ Get text elements within a node, return as list. """
    L = []
    for x in node.getElementsByTagName(tag):
        for c in x.childNodes:
            L.append(str(c.data.decode(default_encoding)).strip())
    return L


# main ==================================================================={{{1
if __name__ == '__main__':
    # run unit tests ?
    rolelist('Administrator', 'Planner', rolefile='r.xml', long=False)
    pass


# notes =================================================================={{{1

# This is an example of programmatic usage:

# uh = CMSUserHandler(rolefile='r.xml', userfile='u.xml')
# uh.add('acosta', roles=('Tracker',), fullname="Fredrik Acosta", comment="on vacation")
# uh.add('stefan', roles=('Tracker',), useGecos=True)
# uh.delete('lenab')
# uh.delete('hakan')
# uh.delete('rojemo')
# uh.mod('acosta', comment="on leave", roles=('Administrator','Planner'), useGecos=True)
# print uh.toXML()


# [acosta:07/183@23:04] First version.
# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
