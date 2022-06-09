#

#
"""Utilities for data based on lookups from rave, like rosters, trips, legs.
"""


class DataClass:
    """Base class for classes that holds data populated from rave, like trips.
    """
    def __str__(self):
        """ Returns a string repr of all data objects of the instance, for debug.
        """
        datastrlist = []
        for (name, val) in self.__dict__.iteritems():
            if type(val) in (list, tuple):
                datastrlist2=[]
                for (nr, item) in enumerate(val):
                    datastrlist2.append('### %s %s %s'%(name, nr, item))
                datastrlist.append('%s\n'%("".join(datastrlist2)))
            elif not callable(val):
                datastrlist.append('%s:%s\n'%(name, val))
        return "\n###\n" + "".join(datastrlist) + "\n###\n"
