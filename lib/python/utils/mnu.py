
# [acosta:08/126@13:22] Created.

"""
OO interface to Gui.

Gui - Python interface to Studio menu package and GUI primitives.  

Possible use: to create dynamic menu structures.
"""

# GuiStubs (testing only) ================================================{{{1
class GuiStubs(object):
    """For testing only..."""
    POT_UNKNOWN, POT_DO, POT_REPEAT, POT_UNDO, POT_REDO = tuple(range(5))
    OPA_UNKNOWN, OPA_OPAQUE, OPA_TRANS, OPA_BYPASS = tuple(range(4))
    _funcs = ('GuiAddMenu', 'GuiSetCursorItem', 'GuiAddMenuButton',
            'GuiAddMenuCascade', 'GuiAddMenuCommand', 'GuiAddMenuMonitor',
            'GuiAddMenuToggle', 'GuiAddMenuSeparator', 'GuiAddMenuTitle',
            'GuiSensitizeMenues', 'GuiDelMenuItem', 'GuiClearMenu',
            'GuiRealizeMenue', 'GuiClearAllMenues', 'GuiRealizeAllMenues',
            'GuiCreateMenuMenu', 'GuiGetContextSensitivity',
            'GuiSetContextSensitivity')

    class _stub:
        def __init__(self, func):
            self.func = func
        def __call__(self, *a, **k):
            print "%s(*%s, **%s)" % (self.func, a, k)

    def __getattr__(self, key):
        if key in self._funcs:
            return self._stub(key)
        else:
            return object.__getattribute__(self, key)


# imports ================================================================{{{1
# For debug change 'import Gui' to 'Gui=GuiStubs()'
import Gui
#Gui=GuiStubs()
import Csl


# exports ================================================================{{{1
__all__ = ['pythoneval', 'CSLEval', 'Button', 'Command', 'Monitor', 'Title',
    'Separator', 'Toggle', 'Menu', 'Listener', 'ContextSensitivity',
    'all_menus', 'clear', 'realize', 'sensitize', 'delete', 'destroy',
    'set_cursor']


# globals ================================================================{{{1
csl = Csl.Csl()


# Decorators ============================================================={{{1

# pythoneval -------------------------------------------------------------{{{2
def pythoneval(func):
    """Wrap content in 'PythonEvalExpr("...")'"""
    def wrapper(*a, **k):
        return """PythonEvalExpr("%s()")""" % func(*a, **k)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__ = func.__dict__
    return wrapper


# Menu registry =========================================================={{{1

# Registry ---------------------------------------------------------------{{{2
class Registry(dict):
    """Keep a registry where object id is mapped to object."""
    def __getattr__(self, key):
        return self[key]

    def register(self, obj):
        self[str(obj)] = obj

    def unregister(self, obj):
        del self[str(obj)]

    @pythoneval
    def refresh(self, obj):
        return "%s.reg.%s" % (self.__module__, obj)


# reg --------------------------------------------------------------------{{{2
# One and only instance of Registry
reg = Registry()


# positive_id ------------------------------------------------------------{{{2
def positive_id(obj):
    """Return id(obj) as a non-negative integer. On some platforms (RH10) the
    id() function can be negative."""
    r = id(obj)
    if r < 0:
        # Cannot use sys.maxint. Try first with 32 bits then with 64.
        r32 = r + (1L << 32)
        if r32 < 0:
            r64 = r + (1L << 64)
            assert r64 >= 0 # Cannot handle addresses larger than 64bits.
            return r64
        return r32
    return r


# Help / Base classes ===================================================={{{1

# Base -------------------------------------------------------------------{{{2
class Base(object):
    """Base class for "Menu" objects. Register itself upon instantiation."""
    def __init__(self):
        """Register the menu object with the registry."""
        reg.register(self)

    def __str__(self):
        """Return a string that can be used as an attribute."""
        return "M%x" % positive_id(self)


# Detachable -------------------------------------------------------------{{{2
class Detachable(Base):
    """Base class for a menu item that can be removed."""
    def __init__(self, title='', icon='', identifier=None):
        Base.__init__(self)
        self.icon = icon
        self.title = title
        if identifier is None:
            self.identifier = str(self)
        else:
            self.identifier = identifier
       
    def detach(self, parent):
        delete(parent, icon=self.icon, title=self.title,
                identifier=self.identifier)


# CSLEval ----------------------------------------------------------------{{{2
class CSLEval(object):
    """
    Use with Buttons etc. for calls that needs to be wrapped using CSL.
        E.g.
        Button(title='Debug', action=CSLEval("PrintDebug(gpc_info, 4, 0)"))
    """
    def __init__(self, command):
        self.command = command

    def __call__(self):
        csl.evalExpr(self.command)


# Gui utility classes ===================================================={{{1

# Button -----------------------------------------------------------------{{{2
class Button(Detachable):
    def __init__(self, title='', icon='', tooltip='', mnemonic='', accelerator='',
            action=None, potency=Gui.POT_REDO, opacity=Gui.OPA_OPAQUE,
            identifier=None, sensitive=True, menuMode=''):
        Detachable.__init__(self, title, icon, identifier)
        self.tooltip = tooltip
        self.mnemonic = mnemonic
        self.accelerator = accelerator
        if action is None:
            self.action = self.run
        else:
            self.action = action
        self.potency = potency
        self.opacity = opacity
        self.sensitive = sensitive
        self.menuMode = menuMode

    def __call__(self):
        return self.action()

    def attach(self, parentMenu, after=None):
        if after:
            Gui.GuiSetCursorItem(parentMenu, "", after, "", True)
        Gui.GuiAddMenuButton(parentMenu, self.icon, self.title, self.tooltip,
                self.mnemonic, self.accelerator, reg.refresh(self),
                self.potency, self.opacity, self.identifier, self.sensitive,
                self.menuMode)
        if self.menuMode:
            sensitize(parentMenu)

    def run(self):
        raise NotImplementedError("run() not implemented.")


# Command ----------------------------------------------------------------{{{2
class Command(Detachable):
    def __init__(self, title='', icon='', tooltip='', mnemonic='',
            accelerator='', name='', command='', flags='',
            potency=Gui.POT_REDO, opacity=Gui.OPA_OPAQUE, identifier=None,
            menuMode=''):
        Detachable.__init__(self, title, icon, identifier)
        self.tooltip = tooltip
        self.mnemonic = mnemonic
        self.accelerator = accelerator
        self.command = command
        self.name = name
        self.flags = flags
        self.potency = potency
        self.opacity = opacity
        self.menuMode = menuMode

    def attach(self, parentMenu):
        Gui.GuiAddMenuCommand(parentMenu, self.icon, self.title, self.tooltip,
                self.mnemonic, self.accelerator, self.name, self.command,
                self.flags , self.potency, self.opacity, self.identifier,
                self.menuMode)
        if self.menuMode:
            sensitize(parentMenu)


# Monitor ----------------------------------------------------------------{{{2
class Monitor(Base):
    # WARNING! This does not work right now, see JIRA STUDIO-13159
    def __init__(self, title='', icon='', tooltip='', varname='', length=5,
            height=5, typeTime=None, refresh=None, action=None, tag='',
            potency=Gui.POT_DO, opacity=Gui.OPA_TRANS, identifier=None,
            menuMode=''):
        Detachable.__init__(self, title, icon, identifier)
        self.tooltip = tooltip
        self.varname = varname
        self.length = length
        self.height = height
        self.typeTime = typeTime
        # Refresh called at triggered event
        if not refresh is None:
            self.refresh = refresh
        # Action called when user presses button
        if action is None:
            self.action = self.run
        else:
            self.action = action
        self.tag = tag
        self.potency = potency
        self.opacity = opacity
        self.menuMode = menuMode

    def __call__(self):
        return self.action()

    def attach(self, parentMenu):
        Gui.GuiAddMenuMonitor(parentMenu, self.icon, self.title, self.tooltip,
                self.varname, self.length, self.height, self.typeTime,
                self.make_refresh(), reg.refresh(self), self.tag,
                self.potency, self.opacity, self.identifier, self.menuMode)
        if self.menuMode:
            sensitize(parentMenu)

    def run(self):
        raise NotImplementedError("run() not implemented.")

    def refresh(self):
        raise NotImplementedError("refresh() not implemented.")

    @pythoneval
    def make_refresh(self):
        return "%s.reg.%s.refresh" % (self.__module__, self)


# Title ------------------------------------------------------------------{{{2
class Title(Detachable):
    def __init__(self, title='', icon='', tooltip='', identifier=None, menuMode=''):
        Detachable.__init__(self, title, icon, identifier)
        self.tooltip = tooltip
        self.menuMode = menuMode

    def attach(self, parentMenu):
        Gui.GuiAddMenuTitle(parentMenu, self.icon, self.title, self.tooltip,
                self.identifier, self.menuMode)
        if self.menuMode:
            sensitize(parentMenu)


# Separator --------------------------------------------------------------{{{2
class Separator(Detachable):
    def __init__(self, title='', identifier=None):
        Detachable.__init__(self, title, '', identifier)

    def attach(self, parentMenu):
        Gui.GuiAddMenuSeparator(parentMenu, self.title, self.identifier)


# Toggle -----------------------------------------------------------------{{{2
class Toggle(Detachable):
    # WARNING! This does not work right now, see JIRA STUDIO-13159
    def __init__(self, title='', icon='', iconSelected='', tooltip='',
            varname='', typeTime=None, refresh=None, action=None, tag='',
            potency=Gui.POT_REDO, opacity=Gui.OPA_OPAQUE, identifier=None,
            menuMode=''):
        Detachable.__init__(self, title, icon, identifier)
        self.iconSelected = iconSelected
        self.tooltip = tooltip
        self.varname = varname
        self.typeTime = typeTime
        # Refresh called at triggered event
        if refresh is None:
            self.refresh = self.refresh
        else:
            self.refresh = refresh
        # Action called when user presses button
        if action is None:
            self.action = self.run
        else:
            self.action = action
        self.tag = tag
        self.potency = potency
        self.opacity = opacity
        self.menuMode = menuMode

    def __call__(self):
        return self.action()

    def attach(self, parentMenu):
        Gui.GuiAddMenuToggle(parentMenu, self.icon, self.iconSelected,
                self.title, self.tooltip, self.varname, self.typeTime,
                self.make_refresh(), reg.refresh(self), self.tag,
                self.potency, self.opacity, self.identifier, self.menuMode)
        if self.menuMode:
            sensitize(parentMenu)

    def run(self):
        raise NotImplementedError("run() not implemented.")

    def refresh(self):
        raise NotImplementedError("refresh() not implemented.")

    @pythoneval
    def make_refresh(self):
        return "%s.reg.%s.refresh" % (self.__module__, self)


# Menu -------------------------------------------------------------------{{{2
class Menu(list, Detachable):
    def __init__(self, name, l=(), title='', icon='', tooltip='', mnemonic='',
            accelerator='', identifier=None, sensitive=True, menuMode=''):
        list.__init__(self, l)
        Detachable.__init__(self, title, icon, identifier)
        self.name = name
        self.tooltip = tooltip
        self.mnemonic = mnemonic
        self.accelerator = accelerator
        self.sensitive = sensitive
        self.menuMode = menuMode
        self.create()

    def __call__(self):
        for name in self:
            name.attach(self.name)

    def attach(self, parent):
        Gui.GuiAddMenuCascade(parent, self.icon, self.title, self.tooltip,
                self.mnemonic, self.accelerator, self.name, self.identifier,
                self.sensitive, self.menuMode)
        if self.menuMode:
            sensitize(parent) 

    def create(self, accelerator=None, refresh=None):
        if accelerator is None:
            accelerator = self.accelerator
        if refresh is None:
            refresh = reg.refresh(self)
        Gui.GuiAddMenu(self.name, accelerator, refresh, self.identifier)
        return self

    def clear(self):
        clear(str(self))

    def realize(self):
        realize(str(self))


# Listener ---------------------------------------------------------------{{{2
class Listener(Base):
    def __init__(self, script, typeTime, tag, id):
        Base.__init__(self)
        if script is None:
            self.script = self.run
        else:
            self.script = script
        self.typeTime = typeTime
        self.tag = tag
        self.id = id
        Gui.GuiCreateListener(reg.refresh(self), self.typeTime, self.tag, self.id)

    def __call__(self):
        return self.script()

    def destroy(self):
        Gui.GuiDestroyListener(self.id, self.typeTime)

    def run(self):
        raise NotImplementedError("run() not implemented.")


# ContextSensitivity -----------------------------------------------------{{{2
class ContextSensitivity:
    @staticmethod
    def get():
        return Gui.GuiGetContextSensitivity() == 1

    @staticmethod
    def set(on_off):
        return Gui.GuiSetContextSensitivity(int(bool(on_off)))


# functions =============================================================={{{1

# all_menus --------------------------------------------------------------{{{2
def all_menus():
    return Gui.GuiCreateMenuMenu()


# clear ------------------------------------------------------------------{{{2
def clear(menuName=None):
    if menuName is None:
        return Gui.GuiClearAllMenues()
    else:
        return Gui.GuiClearMenu(menuName)


# realize ----------------------------------------------------------------{{{2
def realize(menuName=None):
    if menuName is None:
        return Gui.GuiRealizeAllMenues()
    else:
        return Gui.GuiRealizeMenue(menuName)


# sensitize --------------------------------------------------------------{{{2
def sensitize(menuName=None):
    return Gui.GuiSensitizeMenues(menuName)


# delete -----------------------------------------------------------------{{{2
def delete(parent, icon='', title='', identifier=''):
    return Gui.GuiDelMenuItem(parent, icon, title, identifier)


# destroy ----------------------------------------------------------------{{{2
def destroy(id, typeTime):
    return Gui.GuiDestroyListener(id, typeTime)


# set_cursor -------------------------------------------------------------{{{2
def set_cursor(parent, title='', icon='', identifier='', after=True):
    return Gui.GuiSetCursorItem(parent, icon, title, identifier, after)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # Testing
    def test():
        print "TESTING"
    m = Menu('SubMenuTest', title="My menu test")
    m.create()
    b1 = Button(title="B1", action=test)
    m.append(b1)
    m()


# API ===================================================================={{{1

# GuiAddMenu -------------------------------------------------------------{{{2
# def GuiAddMenu(menuName, accelerator, refresh, identifier=None, menuMode=None):
#     """adds a new menu to the package. The menuName becomes the menu's name.
#     The accelerator is an optional keyboard short-cut for popping up the menu.
#     The refresh is an optional expression that is evaluated just before the
#     menu is popped up. It can be used to populate the menu with items suitable
#     for the current data at hand. The refresh expression should conform to the
#     interpreter used by the menu system, i.e. Csl. The identifier is used for
#     the online help and for determining which items should be sensitive or not.
#     The menuMode is used to determine which items should be sensitive. The
#     function returns 0 if successful, -1 otherwise."""
#     pass


# GuiSetCursorItem -------------------------------------------------------{{{2
# def GuiSetCursorItem(parentMenu, icon, title, identifier, after):
#     """find a menu item in the specified parentMenu and put a cursor there so
#     that future additions take place just before or after the item. The item is
#     found by compairing the values of the icon, title and identifier arguments
#     against the properties of the menu items. If an item is found the cursor is
#     positioned so that if after is true, then the following additions will take
#     place after the item that was found. If after is false following additions
#     will appear before the found item. The function understands the
#     implications of old and new menu sources, so that it makes a sensible match
#     even if the menu-item doesn't have an identifier or if it has an identifier
#     derived from its icon. The function returns 0 if successful, -1
#     otherwise."""
#     pass


# GuiAddMenuButton -------------------------------------------------------{{{2
# def GuiAddMenuButton(parentMenu, icon, title, tooltip, mnemonic, accelerator,
#         action, potency, opacity, identifier=None, sensitive=True,
#         menuMode=None):
#     """adds a menu-button to the parentMenu. The new button will have icon,
#     title, tooltip, mnemonic and accelerator for visible properties and it will
#     be active if sensitive is true. It will be named identifier and tagged
#     menuMode. The icon, title, tooltip, mnemonic, and accelerator may be None
#     or a empty string but one of icon and title must be defined for the call to
#     make sense. See GuiSetCursorItem for an explanation of identifier and
#     GuiSensitizeMenues for an explanation of menuMode. When the button is
#     clicked the action script-expression will be evaluated by the menu
#     dispatcher. The script is typically a call of a Csl or Python function. For
#     the purpose of maintaining the Command history and Undo-data the executed
#     function will be assumed to have the potency and opacity indicated by those
#     arguments (see below). If action is None or an empty string then nothing
#     will happen when the button is pressed and the Undo states remains
#     unchanged but an error message is logged. The function returns 0 if
#     successful, -1 otherwise."""
#     pass


# GuiAddMenuCascade ------------------------------------------------------{{{2
# def GuiAddMenuCascade(parent_menu, icon, title, tooltip, mnemonic, accelerator,
#         sub_menu, identifier=0, sensitive=True, menuMode=None):
#     """adds a button that opens a sub-menu to the parentMenu. The sub-menu to
#     open is named by the subMenu argument. See GuiAddMenuButton for an
#     explanation of icon, title, tooltip, mnemonic, accelerator, identifier,
#     menuMode and sensitive. The function returns 0 if successful, -1
#     otherwise."""
#     pass


# GuiAddMenuCommand ------------------------------------------------------{{{2
# def GuiAddMenuCommand(parent_menu, icon, title, tooltip, mnemonic, accelerator,
#         name, command, flags, potency, opacity, identifier=None,
#         menuMode=None):
#     """adds a button that executes a Unix shell command to parentMenu. The
#     command is specified by the command argument. See GuiAddMenuButton for an
#     explanation of icon, title, tooltip, mnemonic, accelerator, identifier,
#     sensitive and menuMode The function returns 0 if successful, -1
#     otherwise."""
#
#     Note: if flags then f.prog else f.sh, the flags will be handled by CPS
# flags:
#  'i'; indicate when the process ends (popup)
#  's'; save the logfile (else automatically deleted)
#  'k'; kill sub-process when parent exits
#  'n'; do not kill sub-process when parent terminates without exit, e.g. crash
#  'g'; run in separate process group
#  'u'; can't be killed by user
#  'e'; alert user if process doesn't return 0
#  'h'; hide from user
#  'p'; prevent multiple starts (with same descr), send SIGUSR2 to existing
#       process instead.
#  'q'; silent
#     
#     pass


# GuiAddMenuMonitor ------------------------------------------------------{{{2
# def GuiAddMenuMonitor(parent_menu, icon, title, tooltip, varname, length,
#         height, typeTime, refresh, action, tag, potency, opacity,
#         identifier=None, menuMode=None):
#     """adds a monitor object to the parentMenu. The monitor will be triggered
#     by the specified typeTime event optionally selecting those events marked
#     with tag. The typeTime may be a positive number giving the interval in
#     seconds between each trigger, or it may be one of the special symbols 
# 
#     JobListener         - a background process was finished.
#     ActionListener      - a command was executed, probably from a menu.
#     MotionListener      - the mouse moved in one of the planning views.
#     RefreshListener     - a refresh of the gui is required.
#     PopupListener       - a menu is about to pop-up.
#     LogListener         - an interaction was recorded.
#     MenuEnabledListener - menu accessibility changed.
#     TaggedListener      - a script signalling something (not sent by Studio
#                           internals).
# 
#     specifying the circumstances for triggering the event. When the trigger
#     occurs the monitor will evaluate the refresh expression which is expected
#     to update in the monitor variable. If the user enters data into the monitor
#     it will evaluate the action expression (if action is null or empty the
#     monitor becomes read-only).  The monitor will display the contents of the
#     varname script variable in a window with width and height dimensions. The
#     variable will be a string sized to hold at least (length+1)*height+1
#     characters. The two scripts typically include a reference to varname as
#     their purpose is to refresh it or update the application from it. See
#     GuiAddMenuButton for an explanation of icon, title, tooltip, mnemonic,
#     accelerator, identifier, menuMode, sensitive, potency, and opacity. The
#     function returns 0 if successful, -1 otherwise."""
#     pass


# GuiAddMenuToggle -------------------------------------------------------{{{2
# def GuiAddMenuToggle(parent_menu, icon, iconSelected, title, tooltip, varname,
#         typeTime, refresh, action, tag, potency, opacity, identifier=None,
#         menuMode=None):
#     """adds a monitor object with the look and feel of a toggle-button to the
#     parentMenu. The created variable will be of type long. When the button is
#     pressed the toggle displays the iconSelected image, otherwise it displays
#     the icon image. The title is displayed next to the image. See
#     GuiAddMenuMonitor for an explanation of the other arguments. The function
#     returns 0 if successful, -1 otherwise."""
#     pass


# GuiAddMenuSeparator ----------------------------------------------------{{{2
# def GuiAddMenuSeparator(parent_menu, title, identifier=None):
#     """Add a separator to the named parentMenu. The separator is always a thin
#     line. The title and identifier may be used to refer to the item in drop or
#     position commands. The function returns 0 if successful, -1 otherwise."""
#     pass


# GuiAddMenuTitle --------------------------------------------------------{{{2
# def GuiAddMenuTitle(parent_menu, icon, title, tooltip=None, identifier=None,
#         menuMode=None):
#     """adds a title text or icon to the parentMenu. See GuiAddMenuButton for an
#     explanation of the other arguments. The function returns 0 if successful,
#     -1 otherwise."""
#     pass


# GuiSensitizeMenues -----------------------------------------------------{{{2
# def GuiSensitizeMenues(menuName=None):
#     """Scans the menu called menuName and makes menu items active or inactive
#     depending on what the menu mode of each menu item is evaluated to. Inactive
#     items are displayed "greyed-out" and cannot be invoked by the user. If no
#     menu name is specified, all menues will be sensitized. This function
#     operates on all items in one menu or on all items in all menues."""
#     pass


# GuiDelMenuItem ---------------------------------------------------------{{{2
# def GuiDelMenuItem(parentMenu, icon, title, identifier):
#     """remove a specfied menu item from the parentMenu. See GuiSetCursorItem
#     for an explanation of how items are located."""
#     pass


# GuiClearMenu -----------------------------------------------------------{{{2
# def GuiClearMenu(menuName):
#     """remove all items from a menu."""
#     pass


# GuiRealizeMenue --------------------------------------------------------{{{2
# def GuiRealizeMenue(menuName):
#     """ensures that a menu has been created in the underlying graphics package
#     and is ready to be popped up. Seldom needed in Python programs."""
#     pass


# GuiClearAllMenues ------------------------------------------------------{{{2
# def GuiClearAllMenues():
#     """calls GuiClearMenu for all menus currently in the package."""
#     pass


# GuiRealizeAllMenues ----------------------------------------------------{{{2
# def GuiRealizeAllMenues():
#     """calls GuiRealizeMenue for all menus currently in the package."""
#     pass


# GuiCreateMenuMenu ------------------------------------------------------{{{2
# def GuiCreateMenuMenu():
#     """return a list of strings naming all menus in the package."""
#     pass


# GuiGetContextSensitivity -----------------------------------------------{{{2
# def GuiGetContextSensitivity():
#     """check resource that determine if the context sensitivity of menus is
#     active. The function returns 1 if sensitivity is on, 0 otherwise."""
#     pass


# GuiSetContextSensitivity -----------------------------------------------{{{2
# def GuiSetContextSensitivity(on):
#     """set the resource that determine if the context sensitivity of menus is
#     active. The function returns 0 is successful, -1 otherwise."""
#     pass


# GuiCreateListener ------------------------------------------------------{{{2
# def GuiCreateListener(script, typeTime, tag=None, id=None):
#     """create a listener - a gui object that is triggered by events occurring
#     int the application. The listener is the invisible part of objects like the
#     monitor and toggle objects described earlier. When triggered the listener
#     will invoke script as if that script was run from a menu-button. The
#     typeTime argument determines what triggers the listener and optionally only
#     the events that match the tag. The id argument may be used to give a name
#     to the listener for later use with GuiDestroyListener. The script string
#     may contain %T or %D which will be replaced by the tag and the data members
#     of the message when the notification occurs. In case %T or %D is NULL an
#     empty string is substituted. See GuiAddMenuMonitor for a description of the
#     typeTime and tag. A special case is the JobListener which receives the
#     process description as the tag, and the process id, the exit status and a
#     start/end-flag (encoded as strings) as the data member."""
#     pass


# GuiCallListener --------------------------------------------------------{{{2
# def GuiCallListener(triggerType, tag=None):
#     """call all listeners of the typeTime kind. The optional tag and data
#     arguments (both are strings) are passed in the message sent to the
#     listeners."""
#     pass


# GuiDestroyListener -----------------------------------------------------{{{2
# def GuiDestroyListener(id, typeTime):
#     """Looks up a listener named id of typeTime kind. If that listener is found
#     it is destroyed. The function returns 0 if successful or if no listener is
#     found, -1 otherwise."""
#     pass


# GuiProcessInteraction --------------------------------------------------{{{2
# def GuiProcessInteraction(type, id):
#     """Causes interactions added via GuiAddBypass3 and GuiAddBypass4 to be
#     processed by the dialog specified via the type and id arguments, if that
#     dialog is active. This function is rarely used in scripts but is used when
#     playing a Macro to cause actions in asynchronous dialogs to be processed.
#     Before the function is called some bypass data for the dialogs must have
#     beein created, e.g. via GuiAddBypass4."""
#     pass


# GuiAddBypass4 ----------------------------------------------------------{{{2
# def GuiAddBypass4(type, id, keys, values):
#     """Stores bypass data for the dialog specified by the type and id
#     arguments. The bypass data consists of two lists of strings. For each item
#     in the keys list (which defines what the data is for) there must be a
#     corresponding item in the values list (giving the actual data to use or
#     button to click), e.g.: [ "selection", "button" ][ "some Selection data",
#     "OK" ] The data is consumed by a dialog or other interactor when a planning
#     function is run or when GuiProcessInteraction is run.  This function is
#     rarely used by scripts since bypasses are handled automatically by the
#     CuiBypassWrapper function."""
#     pass


# GuiAddBypass3 ----------------------------------------------------------{{{2
# def GuiAddBypass3(type, id, val):
#     """Obsolete method for adding bypass data. See also CuiBypassWrapper."""
#     pass


# GuiRemoveBypass --------------------------------------------------------{{{2
# def GuiRemoveBypass(type, id, all):
#     """Removes one/all bypasses for a dialog specified by the type and id
#     arguments. If the all flag is true all matching bypasses are removed,
#     otherwise only one bypass is removed. This function is rarely used by
#     scripts since bypasses are handled automatically by the CuiBypassWrapper
#     function."""
#     pass


# GuiClearBypasses -------------------------------------------------------{{{2
# def GuiClearBypasses(asynchToo):
#     """Remove all bypasses. If asynchToo is true the bypasses are cleared from
#     both the synchronous list and the asynchronouslist, otherwise only the
#     synchronous list is cleared. This function is rarely used by scripts since
#     bypasses are handled automatically by the CuiBypassWrapper function."""
#     pass


# GuiChoiceName2ColorCode -------------------------------------------------{{{2
# def GuiChoiceName2ColorCode(name):
#     """returns the color code (for example "#EDEDED") given a concept name (for
#     example "Background")."""
#     pass


# GuiColorName2ColorCode -------------------------------------------------{{{2
# def GuiColorName2ColorCode(name):
#     """returns the color code (for example "#EDEDED") given a name of a color
#     name (for example "LightGray")."""
#     pass


# GuiColorNumber2Name ----------------------------------------------------{{{2
# def GuiColorNumber2Name(index):
#     """returns the name of the color (for example "LightGray") given a color
#     index. The index should be in the range [0, C_MAX_COLORS-1]."""
#     pass


# C_MAX_COLORS -----------------------------------------------------------{{{2
# C_MAX_COLORS
#     """gives the maximum number of colors used by Studio."""


# Undo, Redo and Repeate ================================================={{{1
# The undo-mechanism in Studio keeps a history of executed commands. The history
# is manipulated when the user invokes Undo, Redo or Repeat. The contents of the
# command history depends on the potency and opacity of the executed commands.  

# Potency ----------------------------------------------------------------{{{2
# The potency determines if it is possible to undo, redo or repeat a command.
# Most commands available in Studio has awell defined potency so it is only
# necessary to specify the potency for commands that have no predefined potency,
# e.g. PythonRunFile(). Potency is defined using the following symbols.
# 
# POT_UNKNOWN
#     The command has no predefined potency, without additional information the
#     command will default to POT_DO. 
# POT_DO
#     The command can be executed but it is not possible to undo the effect and
#     it doesn't make sense to repeat the command.
# POT_REPEAT
#     The command can be executed and also repeated but it is not possible to
#     undo the effect.
# POT_UNDO
#     The command can be undone or repeated. 
# POT_REDO
#     The command can be both undone and redone. It is not possible to increase
#     the potency for a predefined command, i.e. if a Studio command has a
#     predefined potency of POT_REDO then the menus may reduce the potency to
#     POT_REPEAT or POT_DO, the menus cannot increase the potency to POT_REDO.

# Opacity ----------------------------------------------------------------{{{2
# The opacity determines if a command is visible on the command history. If it is
# opaque the command is visible to the user if it is transparent the command is
# not visible.
# 
# OPA_UNKNOWN
#     The command has no predefined opacity, without additional information the
#     command will default to OPA_OPAQUE 
# OPA_OPAQUE
#     The command will be visible to the user. 
# OPA_TRANS
#     The command cannote be seen by the user. It is not possible to decrease the
#     opacity for a predefined command, i.e. if a Studio command has a predefined
#     opacity of OPA_TRANS then the menus may reduce the opacity to OPA_OPAQUE.
#     If a Studio command has a predefined opacity of OPA_OPAQUE then the menus
#     cannot increase the opacity to OPA_TRANS. 


# Examples ==============================================================={{{1

# Example 1---------------------------------------------------------------{{{2
# for i in range(0, Gui.C_MAX_COLORS):
#     name = Gui.GuiColorNumber2Name(i)
#     code = Gui.GuiColorName2ColorCode(name)
#     print i, name, code
# 
# prints the following:
# 
# 0 Black #000000 1 White #FFFFFF 2 LightGrey #E2E2E2
#  ... 56 Cerise #BA1459

# Example 2---------------------------------------------------------------{{{2
# import Gui
# 
# Gui.GuiAddMenuButton("FileMenu", "", "DemoButton", "A demo of GuiAddMenuButton",
#         "_Demo", "",
#         'PythonEvalExpr("Cui.CuiSetSubPlanCrewFilterLeg(Cui.gpc_info, 1)")',
#         Gui.POT_REDO, Gui.OPA_OPAQUE, "DemoButton", True, "")
# 
# adds a button to the menu called FileMenu. The button label will be
# "DemoButton" and when activated will execute a function that turns on the leg
# filter in Studio. Since the command modifies the Studio state in way that is
# handled by the Studio undo-mechanism (i.e. CuiSetSubPlanCrewFilterLeg is
# redoable) it is natural to mark the menu item POT_REDO and OPA_OPAQUE, meaning
# that the command is visible to the user and can be undone and redone.  This is
# the way to tell the Studio command manager that although PythonEvalExpr has an
# unknown potency we guarantee that when called with these arguments the effect
# is in fact both undoable and redoable.

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
