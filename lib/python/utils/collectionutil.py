

"""
Generic collections.
"""

# imports ================================================================{{{1
from UserDict import DictMixin


# exports ================================================================{{{1
__all__ = ['KeyValue']


# classes ================================================================{{{1

# KeyValue ---------------------------------------------------------------{{{2
class KeyValue(DictMixin):
    """
    This class imitates a traditional mapping, but instead the key - value
    pairs are stored in a list, thus keeping the order of input.

    The class supports all methods of a dictionary.  The class can be 
    instantiated in many different ways:

       # With a tuple
       x = KeyValue(('key1', 'value1'))

       # With a dictionary, note that internal order will not be kept!
       x = KeyValue({'key': 'value'})

       # With multiple arguments, where each argument is a tuple
       x = KeyValue(('keyA', 'valueA'), ('keyB', 'valueB'))

       # With a list of tuples
       kvp = [ ('keyA', 'valueA'), ('keyB', 'valueB') ]
       x = KeyValue(kvp)

    The KeyValue object can be manipulated in many, many ways, e.g.:
       x['keyC'] = 'valueC'
       x(keyD='valueD')
    """

    def __init__(self, *a, **na):
        """ The initialization step tries to be as flexible as possible. """
        self.data = []
        self(*a, **na)

    def __call__(self, *a, **na):
        for items in a:
            if isinstance(items, dict):
                self.update(items)
            elif isinstance(items[0], (tuple, list)):
                for item in items:
                    try:
                        self[item[0]] = item[1]
                    except:
                        pass
            else:
                try:
                    self[items[0]] = items[1]
                except:
                    raise
        if na:
            self.update(na)
        return self

    def __contains__(self, key):
        return key in [k for (k, v) in self.data]

    def __delitem__(self, key):
        self.data = [(k, v) for (k, v) in self.data if k != key]

    def __getitem__(self, key):
        return dict(self.data)[key]

    def __setitem__(self, key, value):
        if key in self:
            for i in xrange(len(self.data)):
                if self.data[i][0] == key:
                    self.data[i] = (key, value)
        else:
            self.data.append((key, value))

    def __iter__(self):
        return iter(self.keys())

    def iteritems(self):
        return iter(self.data)

    def keys(self):
        return [k for (k, v) in self.data]

    def copy(self):
        newObj = self.__class__()
        newObj.data = self.data[:]
        return newObj


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
