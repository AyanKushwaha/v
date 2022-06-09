

"""
Some simple tools that makes it easier to create "dynamic" Cfh forms (without
forms file).

#   class DemoBox(BasicBox):
#       def __init__(self, title):
#           BasicBox.__init__(self, title)
#           self.l1 = self.c_label('a label', loc=(0, 0))
#           self.i1 = self.c_string('a string', loc=(0, 10))
#           self.done = self.Done(self)
#           self.cancel = self.Cancel(self)
#           self.build()
#
#   d = DemoBox('Demo')
#   if d.run() == Cfh.Ok:
#       BasicDialog('You pressed OK')
#   else:
#       BasicDialog('You pressed Cancel')
"""

import weakref
import Cfh
import Cui


__all__ = ['BasicBox', 'RaveBox', 'BasicDialog', 'ErrorDialog',
    'InfoDialog', 'QuestionDialog', 'WarningDialog', 'f_area']


# BasicBox ==============================================================={{{1
class BasicBox(Cfh.Box):
    """Base class for dialogs/boxes."""
    def __init__(self, title, name=None):
        Cfh.Box.__init__(self, _def_or_gen(name, 'BOX'), title)

    def run(self):
        """Run the event loop and return the value."""
        self.show(True)
        return self.loop()

    # Factory methods for Entry, Img and Op components -------------------{{{3
    def c_string(self, value=None, maxlength=None, dim=None, loc=None,
            name=None):
        if maxlength is None:
            if value is None:
                maxlength = 0
            else:
                maxlength = len(str(value))
        return Cfh.String(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                maxlength, value)

    def c_filename(self, value=None, maxlength=None, dim=None, loc=None,
            name=None):
        if maxlength is None:
            if value is None:
                maxlength = 0
            else:
                maxlength = len(str(value))
        return Cfh.FileName(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                maxlength, value)

    def c_pathname(self, value=None, maxlength=None, max_components=0,
            min_components=0, dim=None, loc=None, name=None):
        return Cfh.PathName(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                maxlength, value,  min_components, max_components)

    def c_number(self, value=None, allow_negative=True, dim=None, loc=None,
            name=None):
        return Cfh.Number(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value, allow_negative)

    def c_date(self, value=-1, dim=None, loc=None, name=None):
        return Cfh.Date(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value)

    def c_datetime(self, value=-1, dim=None, loc=None, name=None):
        return Cfh.DateTime(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value)

    def c_clock(self, value=0, dim=None, loc=None, name=None):
        return Cfh.Clock(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value)

    def c_duration(self, value=0, allow_negative=False, dim=None, loc=None,
            name=None):
        return Cfh.Duration(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value, allow_negative)

    def c_toggle(self, value=False, dim=None, loc=None, name=None):
        return Cfh.Toggle(self, _def_or_gen(name, 'ENTRY'), f_area(loc, dim),
                value)

    def c_label(self, value, dim=None, loc=None, name=None):
        return Cfh.Label(self, _def_or_gen(name, 'IMG'), f_area(loc, dim),
                value)

    def c_separator(self, length, vertical=False, dim=None, loc=None,
            name=None):
        return Cfh.Separator(self, _def_or_gen(name, 'IMG'), f_area(loc, dim),
                length, vertical)

    # Convenience classes for buttons ------------------------------------{{{3
    class Done(Cfh.Done):
        def __init__(self, parent, text=None, mnemonic=None, dim=None,
                loc=None,
                name='OK'):
            # Using weakref, to get values from parent use: self.parent().value
            self.parent = weakref.ref(parent)
            if text is None:
                text = 'OK'
            if mnemonic is None:
                mnemonic = '_O'
            Cfh.Done.__init__(self, self.parent(), name, f_area(loc, dim),
                    text, mnemonic)

    class Cancel(Cfh.Cancel):
        def __init__(self, parent, text=None, mnemonic=None, dim=None,
                loc=None, name='CANCEL'):
            self.parent = weakref.ref(parent)
            if text is None:
                text = 'Cancel'
            if mnemonic is None:
                mnemonic = '_C'
            Cfh.Cancel.__init__(self, self.parent(), name, f_area(loc, dim),
                    text, mnemonic)

    class Reset(Cfh.Reset):
        def __init__(self, parent, text=None, mnemonic=None, dim=None,
                loc=None, name='RESET'):
            self.parent = weakref.ref(parent)
            if text is None:
                text = 'Reset'
            if mnemonic is None:
                mnemonic = '_R'
            Cfh.Reset.__init__(self, self.parent(), name, f_area(loc, dim),
                    text, mnemonic)

    class Function(Cfh.Function):
        def __init__(self, parent, text=None, mnemonic=None, check=False,
                is_default_button=False, return_value=0, dim=None, loc=None,
                name='BUTTON'):
            self.parent = weakref.ref(parent)
            Cfh.Function.__init__(self, self.parent(), name, f_area(loc, dim),
                    text, mnemonic, check, is_default_button, return_value)


# RaveBox ================================================================{{{1
class RaveBox(BasicBox):
    """Base class for a Box where the default values are calculated on current
    object using a Rave variable:

    # Example of an input field where the initial value is the start country of
    # a leg:
    ...
    self.a_string = self.r_string('leg.%start_country%')
    ...
    """
    def r_string(self, rave_var, maxlength=None, dim=None, loc=None,
            name='R_ENTRY'):
        value = self._CuiGet('String', rave_var)
        return self.c_string(value=value, maxlength=maxlength, dim=dim,
                loc=loc, name=name)
    
    def r_date(self, rave_var, dim=None, loc=None, name='R_ENTRY'):
        value = self._CuiGet('Abstime', rave_var)
        return self.c_date(value=value, dim=dim, loc=loc, name=name)
    
    def r_datetime(self, rave_var, dim=None, loc=None, name='R_ENTRY'):
        value = self._CuiGet('Abstime', rave_var)
        return self.c_datetime(value=value, dim=dim, loc=loc, name=name)

    def r_clock(self, rave_var, dim=None, loc=None, name='R_ENTRY'):
        value = self._CuiGet('Abstime', rave_var)
        return self.c_clock(value=value, dim=dim, loc=loc, name=name)
    
    def r_duration(self, rave_var, allow_negative=False, dim=None, loc=None,
            name='R_ENTRY'):
        value = self._CuiGet('Reltime', rave_var)
        return self.c_duration(value=value, allow_negative=allow_negative,
                dim=dim, loc=loc, name=name)
    
    def r_toggle(self, rave_var, dim=None, loc=None, name='R_ENTRY'):
        value = self._CuiGet('Bool', rave_var)
        return self.c_toggle(value=value, dim=dim, loc=loc, name=name)

    def r_number(self, rave_var, allow_negative=True, dim=None, loc=None,
            name='R_ENTRY'):
        value = self._CuiGet('Int', rave_var)
        return self.c_number(value=value, allow_negative=allow_negative,
                dim=dim, loc=loc, name=name)

    def _CuiGet(self, type_, rave_var):
        """Return evaluated Rave value."""
        return getattr(Cui, 'CuiCrcEval' + type_)(Cui.gpc_info,
                Cui.CuiWhichArea, 'object', rave_var)


# Basic dialogs =========================================================={{{1

# BasicDialog ------------------------------------------------------------{{{2
class BasicDialog(BasicBox):
    """Simple dialog with one main text (in bold) and some additional
    (optional) rows and an 'OK' button. An optional icon can be given."""
    def __init__(self, text, *additional, **k):
        BasicBox.__init__(self, title=k.get('title', text),
                name=k.get('name'))
        icon = k.get('icon')
        startrow = startcol = 0
        if not icon is None:
            self.icon = self.c_label(icon, loc=(0, 0), dim=(2, 2))
            startrow += 1
            startcol = 3
        self.banner = self.c_label(text, loc=(startrow, startcol))
        self.banner.setStyle(Cfh.CfhSLabelBanner)
        for i in xrange(len(additional)):
            setattr(self, 'label%s' % i, self.c_label(additional[i], 
                loc=(startrow + 1 + i, startcol)))
        self.ok_button = self.Done(self)
        self.build()


# ErrorDialog ------------------------------------------------------------{{{2
class ErrorDialog(BasicDialog):
    def __init__(self, *a, **k):
        k['icon'] = 'xm_error.pm'
        BasicDialog.__init__(self, *a, **k)


# InfoDialog -------------------------------------------------------------{{{2
class InfoDialog(BasicDialog):
    def __init__(self, *a, **k):
        k['icon'] = 'xm_information.pm'
        BasicDialog.__init__(self, *a, **k)


# WarningDialog ----------------------------------------------------------{{{2
class WarningDialog(BasicDialog):
    def __init__(self, *a, **k):
        k['icon'] = 'xm_warning.pm'
        BasicDialog.__init__(self, *a, **k)


# QuestionDialog ---------------------------------------------------------{{{2
class QuestionDialog(BasicDialog):
    def __init__(self, *a, **k):
        k['icon'] = 'xm_question.pm'
        BasicDialog.__init__(self, *a, **k)


# Help classes and functions ============================================={{{1

# _NumGenerator ----------------------------------------------------------{{{2
class _NumGenerator:
    def __init__(self, start_value=0):
        self.count = start_value 

    def __call__(self):
        x = self.count
        self.count += 1
        return x


# _num_generator ---------------------------------------------------------{{{2
_num_generator = _NumGenerator()


# _def_or_gen ------------------------------------------------------------{{{2
def _def_or_gen(name, default):
    if name is None:
        return "%s%s" % (default, _num_generator())
    return name


# f_area -----------------------------------------------------------------{{{2
def f_area(loc=None, dim=None):
    """Factory method for Area() objects."""
    if dim is None:
        if loc is None:
            return Cfh.Area()
        else:
            return Cfh.Area(Cfh.Loc(*loc))
    else:
        if loc is None:
            return Cfh.Area(Cfh.Dim(*dim))
        else:
            return Cfh.Area(Cfh.Dim(*dim), Cfh.Loc(*loc))


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    x = BasicDialog('HELO', 'Hello world!', title='HEJ!')
    x.run()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
