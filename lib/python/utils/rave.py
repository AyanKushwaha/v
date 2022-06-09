
# changelog {{{2
# [acosta:06/262@08:36] First version
# [acosta:07/031@14:00] Refactoring, using UserList
# }}}

"""
This module contains utilities for the Rave API.
"""

# imports ================================================================{{{1
import carmensystems.rave.api as rave
from UserList import UserList
from Variable import Variable


# exports ================================================================{{{1
__all__ = ['RaveIterator', 'RaveIteratorClassic', 'RaveEvaluator', 'MiniEval']


# classes ================================================================{{{1

# Entry ------------------------------------------------------------------{{{2
class Entry:
    """
    A container to hold fields from Rave search.
    The field '__chain' must not be set, it contains a pointer to next
    level entry list.
    """
    def __init__(self):
        self.__chain = {} 

    def __setitem__(self, var, value):
        """Transformation from dictionary access to field access."""
        self.__dict__[var] = value

    def __str__(self):
        """Return a string with values of the record's fields:
          <Entry var1="value1" var2="value2" ...>
        """
        return "<%s " % (self.__class__.__name__) + ' '.join(['%s="%s"' % (x, self.__dict__[x]) for x in self.__dict__.keys() if not x.startswith('_')]) + ">"

    __repr__ = __str__

    def __iter__(self):
        """Cannot be used when this level contains multiple sub-levels. In that
        case 'chain()' has to be used, or any of the sub-level iterators will
        be returned (not predictable)."""
        return iter(self.chain())

    def chain(self, name=None):
        """Return iterable sub-level. The parameter 'name' is the name that was
        used in the RaveIterator.link() command and is optional for iterators
        with only one sub-level."""
        if name is None:
            return self.__chain.values()[0]
        else:
            return self.__chain[name]

    def setchain(self, name, o):
        """Used internally by RaveIterator."""
        self.__chain[name] = o


# RaveIterator -----------------------------------------------------------{{{2
class RaveIterator(UserList):
    """
    The RaveIterator class was developed to be able to handle results from rave
    searchs. For usage see the example below and look in the module
    'test_utils.py'.

    Note: no evaluation of the Rave variables is performed until 'eval(...)' is
    called.

    INITIALIZATION:
        myIter = RaveIterator(iterator, [fields, [nextlevels]])
            iterator -> times/iter from carmensystems.rave.api
            fields (optional) -> mapping or class that has a field named 'fields'
            nextlevels (optional) -> mapping to next level(s)

    OPTIONAL FIELDS:
    Use of these fields is discouraged.
       'fields'      - a dictionary that contains fieldnames and Rave variables,
                       (use fields definition when creating object instead)
       'nextlevels'  - mapping of next levels in the iteration
                       (use links() to create links instead)

    OTHER FIELDS:
    Use of these fields is discouraged.
        'data'       - Used internally, do not touch!

    METHODS:
        'chain()' -or- "chain('name_of_next_level_chain')"
                         - Iterate over next coming level(s)
        'eval(context)'  - Evaluate the complete Rave expression.
        'iter()'         - For convenience, wraps 'carmensystems.rave.api.iter()'
        'times()'        - For convenience, wraps 'carmensystems.rave.api.times()'
        'link(dict|RaveIterator())'
                         - connect this iteration to a lower level iteration.

    The iterator supports the most (if not all) the methods of a list.

    EXAMPLES:
        For examples, see bottom of this file.
    """

    # For convenience only
    iter = rave.iter
    times = rave.times
    rulefailure = rave.rulefailure
    constraint_eval = rave.constraint_eval
    selected = rave.selected

    def __init__(self, iterator=None, fields={}, nextlevels=None):
        """
        Reset result_set list
        """
        UserList.__init__(self)
        self.iterator = iterator
        if isinstance(fields, dict):
            self.fields = fields
        else:
            self.fields = fields.fields

        if nextlevels is None:
            self.nextlevels = None
        elif isinstance(nextlevels, dict):
            self.nextlevels = nextlevels
        else:
            self.nextlevels = {'next': nextlevels}

    def __call__(self, results):
        """
        This function recurses until a class with no 'nextlevel' is found
        (newobj(r[i] below).
        """
        for r in results:
            if hasattr(self, 'nextlevels') and self.nextlevels is not None:
                k = self.nextlevels.keys()
                # First position is discarded together with all "nextlevels"
                e = self.__makeEntry(r[1 + len(k):])
                i = 1
                for level in k:
                    newobj = self.nextlevels[level].copy()
                    # recurse
                    newobj(r[i])
                    e.setchain(level, newobj)
                    i += 1
                self.append(e)
            else:
                # No other levels, discard first position (index)
                if hasattr(r[0], 'failtext'):
                    # rulefailure() or constraint_eval()
                    for rc in r:
                        self.append(rc)
                else:
                    self.append(self.__makeEntry(r[1:]))

    def copy(self):
        """
        Makes a (shallow) copy of the object itself, the relevant fields
        are copied to the new instance.
        """
        raveIterator = RaveIterator(self.iterator, self.fields, self.nextlevels)
        raveIterator.__class__ = self.__class__
        return raveIterator

    def create_entry(self):
        """
        Can be overridden for cases when one needs a more complex Entry()
        object
        """
        return Entry()

    def eval(self, context=None):
        """
        The method 'eval()' has to be called by the end user.  No values are
        fetched until this method is called.

        If there is a sub-level, then this levels argument will be in 
        position 2.
        """
        if self.iterator is None:
            # Simulate iteration by inserting dummy object first
            if context is None:
                results = ((0,) + rave.eval(*self.fields.values()),)
            elif hasattr(context, 'eval'):
                results = ((0,) + context.eval(*self.fields.values()),)
            else:
                results = ((0,) + rave.eval(context, *self.fields.values()),)
        else:
            if context is None:
                results, = rave.eval(self.getcmd())
            elif hasattr(context, 'eval'):
                results, = context.eval(self.getcmd())
            else:
                results, = rave.eval(context, self.getcmd())
        instance = self.copy()
        instance(results)
        return instance

    def getcmd(self):
        """ Recurses thru levels and collects iteration info """
        if hasattr(self, 'nextlevels') and self.nextlevels is not None:
            cmds = [level.getcmd() for level in self.nextlevels.values()]
            cmds.extend(self.fields.values())
            cmd = rave.foreach(self.iterator, *cmds)
        else:
            cmd = rave.foreach(self.iterator, *self.fields.values())
        return cmd

    def link(self, *a, **k):
        """ Connect this instance with a next-level RaveIterator instance """
        if a:
            if isinstance(a[0], dict):
                self.nextlevels = a[0]
            else:
                self.nextlevels = {'next': a[0]}
        if k:
            if hasattr(self, 'nextlevels') and self.nextlevels is None:
                self.nextlevels = k
            else:
                self.nextlevels.update(k)
        return self

    def __rshift__(self, other):
        """
        For the '>>' operator, can be used like this:
        MyIterator >> NextLevelObject >> {'crew', crewIter, 'delays': delayIter}
        """
        if isinstance(other, dict):
            self.nextlevels = other
        else:
            self.nextlevels = {'next': other}
        return other

    __lshift__ = link

    def __repr__(self):
        """ 'YAML light' representation """
        r = ['--- !%s' % (_strclass(self.__class__))]
        if hasattr(self, "iterator") and self.iterator:
            r.append('iterator:   %s' % (self.iterator))
        if hasattr(self, "fields") and self.fields:
            r.append('fields:     %s' % (str(self.fields)))
        if hasattr(self, "nextlevels") and self.nextlevels:
            r.append('nextlevels: %s' % (str(self.nextlevels)))
        if hasattr(self, "context") and self.context:
            r.append('context:    %s' % (self.context))
        if hasattr(self, "data") and self.data:
            r.append('data:')
            for d in self.data:
                r.append('    - %s' % (d))
        return '\n'.join(r)

    def __str__(self):
        return '<%s with id %ld>' % (_strclass(self.__class__), id(self))

    # overridden methods from UserList -----------------------------------{{{3
    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        newobj = self.copy()
        newobj.data[:] = self.data[i:j]
        return newobj

    def __add__(self, other):
        newobj = self.copy()
        if isinstance(other, UserList):
            newobj.data = self.data + other.data
        elif isinstance(other, type(self.data)):
            newobj.data = self.data + other
        else:
            newobj.data = self.data + list(other)
        return newobj

    def __radd__(self, other):
        newobj = self.copy()
        if isinstance(other, UserList):
            newobj.data = other.data + self.data
        elif isinstance(other, type(self.data)):
            newobj.data = other + self.data
        else:
            newobj.data = list(other) + self.data
        return newobj

    def __mul__(self, n):
        newobj = self.copy()
        newobj.data = self.data * n
        return newobj

    __rmul__ = __mul__

    # private methods ----------------------------------------------------{{{3
    def __makeEntry(self, x): 
        """ 
        Internal function that fills the fields in an entry object with the
        returned Rave values.
        """
        e = self.create_entry()
        k = self.fields.keys()
        i = 0
        for value in x:
            e[k[i]] = value
            i += 1
        return e


# RaveIteratorClassic ----------------------------------------------------{{{2
class RaveIteratorClassic(RaveIterator):
    """
    Implements the RaveIterator with the old paradigm, i.e. when user wants
    to subclass RaveIterator.

    The subclass must define the following fields:
       'fields'     - mapping of fields and rave values (see above).
       'iterator'   - a rave iter function, or the alias 'RaveIterator.iter()'.
       'context'    - only mandatory for top-level objects (where the iteration
                      starts)
       'nextlevels' - mapping with next iteration chain objects {'name': RaveIterator}.
    """
    data = []
    def __init__(self):
        self.data = []

    def copy(self):
        instance = RaveIteratorClassic()
        if hasattr(self, 'fields'):
            instance.fields = self.fields
        if hasattr(self, 'nextlevels'):
            instance.nextlevels = self.nextlevels
        return instance

    def eval(self, context=None):
        if context is None:
            return RaveIterator.eval(self, self.context)
        else:
            return RaveIterator.eval(self, context)
            

# RaveEvaluator ----------------------------------------------------------{{{2
class RaveEvaluator(object):
    """
    Interface supplying convenience methods to populate with
      rave evaluation values as class and instance attributes,
      optionally transformed to other format than returned by the Rave API.
    
    Will evaluate several rave expressions
      in one Rave API call, which is a performance advantage.
        
    Transforms must take a value as a single argument, 
        and return the transformed value.
      
    Intended to be inherited by classes that want to use the interface.
    
    For example:
        from AbsDate import AbsDate
        class RaveUser(RaveBase,RaveEvaluator):
            RaveEvaluator.rEvalCls(setuptime="now", setupdate=("now",AbsDate))
            def __init__(self):
                self.rEvalObj(instdatestr=("now",AbsDate,str,lower))
        print RaveUser.setuptime,"/",RaveUser.setupdate
        ru = RaveUser()
        print ru.setuptime,"/",ru.setupdate,"/",ru.instdatestr
        ==>
        01FEB2007 10:03 / 01FEB2007
        01FEB2007 10:03 / 01FEB2007 / 01feb2007
    """
    
    @staticmethod
    def rEvalList(context, expr_list):
        expressions = []
        transforms = None
        for i,expr in enumerate(expr_list):
            if isinstance(expr,str):
                expressions.append(expr)
            else:
                expressions.append(expr[0])
                for transform in expr[1:]:
                    if transforms is None: transforms = []
                    transforms.append((i,transform))
        if context: 
            values = list(rave.eval(context, *expressions))
        else:
            values = list(rave.eval(*expressions))
        if transforms:
            voidyvoids = []
            for i,transform in transforms:
                if transform == 'voidy':
                    if values[i] is None:
                        voidyvoids += [i]
                elif i not in voidyvoids:
                    values[i] = transform(values[i])
        return values

    @staticmethod
    def rEvalDict(context=None, **fields):
        return dict(zip(fields.keys(),
                        RaveEvaluator.rEvalList(context, fields.values())
                        )
                    )

    @classmethod
    def rEvalCls(cls, **fields):
        for k,v in RaveEvaluator.rEvalDict(context=None, **fields).iteritems():
            setattr(cls, k, v) 
       
    def rEvalObj(self, **fields):
        if not self.__obj_is_initialized:
            self.rEvalInit()
            self.__obj_is_initialized = True
        self.__dict__.update(RaveEvaluator.rEvalDict(self.__evalContext, **fields))
            
    def rEval(self, *expr_args):
        if not self.__obj_is_initialized:
            self.rEvalInit()
            self.__obj_is_initialized = True
        return RaveEvaluator.rEvalList(self.__evalContext, expr_args)
       
    def __init__(self, area=None, mode=None, id=None, **fields):
        self.__obj_is_initialized = False
        if area is None:
            self.__evalContext =  None
        else:
            import Cui
            if mode == Cui.LegMode:
                self.__evalContext = rave.selected('levels.leg') 
            elif mode == Cui.CrrMode:
                self.__evalContext = rave.selected('levels.trip') 
            else:
                self.__evalContext = rave.selected('levels.chain') 
            self.__evalArea = area
            self.__evalMode = mode
            self.__evalId   = id
            
        if fields:
            self.rEvalObj(**fields)
            
    def __str__(self):
        s = "<%s:" % self.__class__.__name__
        for key in sorted(self.__dict__):
            if not key.startswith("_"):
                s += " %s=%s" % (key,self.__dict__[key])
        s += ">"
        return s
    
    def rEvalInit(self):
        if self.__evalContext is not None:
            import Cui
            if self.__evalMode is not None \
            and self.__evalId is not None:
                Cui.CuiSetSelectionObject(Cui.gpc_info, 
                                          self.__evalArea,
                                          self.__evalMode,
                                          str(self.__evalId))
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
                                        self.__evalArea,
                                        "OBJECT")

    # test/demo method ---------------------------------------------------{{{3
    @classmethod
    def test(cls):
        """
        Demonstration of the features of this interface.
        Sample output:
            
        RaveEvaluator.test():
           class variables:
              nowtm   <type 'str'> = 17JUN2007 10:02
              cphtm   <type 'str'> = CPH: 17JUN2007 12:02
           instance variables:
              crew id <type 'str'> = 37812
                 name <type 'str'> = AABEL
              now     <class 'BSIRAP.AbsTime'> = 17JUN2007 10:02
              nowdate <class 'BSIRAP.AbsDate'> = 17JUN2007
        """
        import Cui
        from AbsDate import AbsDate
        
        # Evaluate as class variables.
        cls.rEvalCls(
                #  Value of 'now' keyword, as a string.
                nowtm=("now",str),
                #  Local time in CPH, as a string: "CPH: <time>".
                cphtm=('station_localtime("CPH",now)',str,lambda t: "CPH: "+t))

        # Evaluate as instance variables.
        obj = RaveEvaluator(Cui.CuiArea0, Cui.CrewMode, "37812",
                  # Crew name, if valid in default context, else None
                  crewname="crew.%login_name%",
                  )
        obj.rEvalObj(
                # Value of 'now' keyword, in native form (AbsTime).
                now="now",
                # Value of 'now' keyword, transformed to AbsDate.
                nowdate=("now",AbsDate),
                # Crew id, if valid in default context, else None
                crewid="crew.%id%")
        print """RaveEvaluator.test():
           class variables:
              nowtm   %s = %s
              cphtm   %s = %s
           instance variables:
              crew id %s = %s
                 name %s = %s
              now     %s = %s
              nowdate %s = %s""" % (type(cls.nowtm),    cls.nowtm, # or obj.nowtm, or obj.__class__.nowtm
                                    type(cls.cphtm),    cls.cphtm, # or obj.cphtm, or obj.__class__.cphtm
                                    type(obj.crewid),   obj.crewid,
                                    type(obj.crewname), obj.crewname,
                                    type(obj.now),      obj.now,
                                    type(obj.nowdate),  obj.nowdate)
        import string
        print "now =",obj.rEval('fundamental.%now%')[0]
        print "now lower =",obj.rEval(('fundamental.%now%',str,string.lower))[0]


# MiniEval ---------------------------------------------------------------{{{2
class MiniEval:
    """
    Simple evaluations, several values wanted on single object.

    Example: 
    leg = MiniEval({
        'code': 'leg.%code%, 
        'start_station': 'leg.%start_station%,
        'end_station': 'leg.%end_station%,
        }).eval(rave.selected(rave.Level.atom()))
    """
    def __init__(self, fields, entrycls=Entry):
        self.fields = fields
        self.entrycls = entrycls

    def eval(self, context=None):
        """Evaluate and return object."""
        if context is None:
            results = rave.eval(*self.fields.values())
        elif hasattr(context, 'eval'):
            results = context.eval(*self.fields.values())
        else:
            results = rave.eval(context, *self.fields.values())
        e = self.entrycls()
        k = self.fields.keys()
        for i in xrange(len(results)):
            e[k[i]] = results[i]
        return e


# functions =============================================================={{{1

# _strclass --------------------------------------------------------------{{{2
def _strclass(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)


# Examples ==============================================================={{{1
# Example 1 --------------------------------------------------------------{{{2
#class B01:
#    def keys(self):
#        return [k for k in self.__dict__.keys() if not iscallable(k)]
#
#    def values(self):
#        return [v for (k, v) in self.__dict__.iteritems() if not iscallable(k)]
#
#    def __getitem__(self, x):
#        return self.__dict__[x]
#
#class Test1(B01):
#    sn = 'crew.%surname%'
#    gn = 'crwe.%firstname%'
#
#
#t = Test1()
#print "keys", t.keys()
#print "values", t.values()
#
#class A01:
#    def eval(self, context):
#        results, = rave.eval(context, self.getcmd())
#        self(results)
#
#    def getcmd(self):
#        if hasattr(self, 'nextlevels'):
#            cmds = [nextLevel.getcmd() for nextLevel in self.nextlevels.values()]
#            cmds.extend(self.fields.values())

# Example 2 --------------------------------------------------------------{{{2

#        class MyCrew(RaveIterator):
#            fields = {
#                'id': 'crew.%id%',
#                'gn': 'crew.%firstname%',
#                'sn': 'crew.%surname%',
#            }
#            iterator = RaveIterator.iter('iterators.leg_set',
#                    where='fundamental.%is_roster%')
#
#        class MyLegs(RaveIterator):
#            context = 'sp_crew'
#            fields = {
#                'flight': 'leg.%flight_name%',
#                'std': 'leg.%activity_scheduled_start_time_UTC%',
#            }
#            nextlevels = {'crew': MyCrew()}
#            iterator = RaveIterator.iter('iterators.unique_leg_set',
#                        where='leg.%%is_flight_duty%% and leg.%%udor%% = %s' % (AbsTime("14May2006")),
#                        sort_by='leg.%flight_name%')
#
#        legs = MyLegs().eval()
#        for leg in legs:
#            print "Flight: %s - STD %s" % (leg.flight, leg.std)
#            print "There are %d crew on this flight" % (len(leg.chain('crew')))
#            for crew in leg.chain('crew'):
#                print "Crew ID: %s - Name: %s, %s" % (crew.id, crew.sn, crew.gn)

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof

