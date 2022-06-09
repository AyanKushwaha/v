

"""
Modifying/extending lists of activities.

* Rave evaluation (or Table Manager search) produces list of activities.
* If an activity is of a specific kind (triggered by a callback), then
  modify/extend the list.
"""

import warnings


default_modifier = lambda x: [x]
warnings.filterwarnings('ignore', r'Rave.*not available.*')


try:
    import utils.rave as rave

    class ExtEntry(rave.Entry):
        """This variant of Entry will not iterate the original Rave iteration list,
        but instead a modified version of the same list. The modification call-back
        function is specified as 'modifier'."""
        def __init__(self, modifier=default_modifier):
            rave.Entry.__init__(self)
            self.__modifier = modifier

        def get_modifier(self):
            return self.__modifier

        def chain(self, name=None):
            """Return modified iteration."""
            return ext(rave.Entry.chain(self, name), self.get_modifier())


    class ExtRaveIterator(rave.RaveIterator):
        """Extended version of RaveIterator that allows the FOLLOWING iteration to
        be modified."""
        def __init__(self, iterator=None, fields={}, nextlevels=None,
                modifier=default_modifier, entry=ExtEntry):
            rave.RaveIterator.__init__(self, iterator, fields, nextlevels)
            self._modifier = modifier
            self._entry = entry

        def copy(self):
            """Needed because of the clumsy design of RaveIterator."""
            ri = rave.RaveIterator.copy(self)
            ri._modifier = self._modifier
            ri._entry = self._entry
            return ri

        def create_entry(self):
            """Return ExtEntry object instead of the default Entry."""
            return self._entry(self._modifier)
except:
    warnings.warn("Rave is not available - 'ExtEntry' and 'ExtRaveIterator' cannot be used.")

def ext(l, modifier=default_modifier):
    """Extend list, modifier should return list or iterable."""
    L = []
    for activity in l:
        L.extend(modifier(activity))
    return L


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
