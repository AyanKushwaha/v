
#
"""
Rave Context handling. Studio version.

Most calls to the rave api should be done using
an instance of a Context class. 
"""

import Cui
import carmensystems.rave.api as R


class StudioContextError(StandardError):
    "Only one instance of Context defining scope and area is allowed"                          
    
class Context:
    """
    """
    forbid_more_than_one_default_context_definition = False   # Could be set to False during development. 
    _default_context_counter = 0
    _default_context_buffers = ("plan","window","object")
    
    def __init__(self, buffer="plan", area=Cui.CuiNoArea):
        """
        buffer: 'plan', 'window', 'object' or an existing Rave context.
        area:    Needed when buffer is 'window' or 'object'

        Note: When the buffer is 'plan', 'window' or 'object' a global
              definition in Studio is set by the __init__ method.
              Therefore only one class instance of that kind may exist.
        Note: Many Cui functions (e.g. CuiCrcEval) reset the global
              definition in Studio. After a call of such a function the
              "reInit" method must be called. 
        """
        self._buffer = buffer.lower()
        self._area = area
        if self._buffer == "object":
            self._id = Cui.CuiCrcEval(Cui.gpc_info,self._area,self._buffer,"leg_identifier").getValue()

    def eval(self,*args):
        """
        As eval in the Rave api, but in the defined context.
        args: Rave api code
        Return: tuple
        """
        self.reInit()
        return R.eval(self._getContextId(),*args)

    def simpleEvalSingleExpr(self,expr,iter="leg_set",filter=None,sort=None):
        """
        Creates a list of values for the defined set of objects.
        'expr'is a rave expression.
        'iter' is an iterator.

        filter: A rave expression or a tulple of rave expression
        sort: A rave expression or a tuple of rave expressions
        
        """
        if not sort:            sort   = "1"   # None
        if type(sort) == tuple: sort = tuple([R.expr(i) for i in sort])
        else:                   sort   = R.expr(sort)  

        if not filter:             filter = "true" # None
        if type(filter) == tuple : filter = tuple([R.expr(i) for i in filter])
        else:                      filter = R.expr(filter) 

        try: 
	    l, = self.eval(R.foreach(R.iter(iter,
                                            where=filter,
                                            sort_by=sort),
                                     R.expr(expr)))
        except R.UsageError:
	    # Here we make a modified call to allow that the expression 
            # has a smaller dependency than the iterator. 
            # It is handy in some cases. E.g. if you want to get one leg 
            # identifier per chain.
            # However we can't replace the first call with this one. 
            # Reason: If you have more than one object in the 
            # iterator bag, the dependency must be identical.
            
            l, = self.eval(R.foreach(R.iter(iter,
                                            where=filter,
                                            sort_by=sort),
                                     R.first(R.Level.atom(),     # To skip the strict dependency demand. 
                                             R.expr(expr))))
        
        if not l: return []
        return [object[1] for object in l]

    def getCrrIdentifiers(self,filter="true",sort="true",iter="iterators.trip_set" ):
        """
        Returns a list of crr identifier strings
        """
        o = self.simpleEvalSingleExpr("default(crr_identifier,0)",iter,filter)
        return [str(object) for object in o if object != 0]
        
    def getLegIdentifiers(self,filter="TRUE",sort ="TRUE", iter="iterators.leg_set"):
        """
        Return a list of leg identifier strings
        """
        o = self.simpleEvalSingleExpr("leg_identifier",iter,filter)
        return [str(object) for object in o]

    def getCrewIdentifiers(self,filter="TRUE",sort ="TRUE", iter="iterators.roster_set"):
        """
        Return a list of crew identifiers
        """
        o = self.simpleEvalSingleExpr('default(crr_crew_id,"VOID")',iter,filter)
        return [object for object in o if object != "VOID"]

    def reInit(self):
        """
        Must be called if a Cui function that reset the global settings
        used for defining the active set of objects has been called.
        Could cause a crash if scope is "object" and that object does not
        exists any longer.
        """
        if self._buffer in Context._default_context_buffers:
            if self._buffer == "object":
                Cui.CuiSetSelectionObject(Cui.gpc_info,self._area,Cui.LegMode,self._id)
            Context._setDefaultContext(self._buffer, self._area)

    # Private part
    def __del__(self):
        if self._buffer in Context._default_context_buffers:
            Context._default_context_counter -= 1

    def _getContextId(self):
        if self._buffer in Context._default_context_buffers:
            return "default_context"
        else:
            return self._buffer
            
    def _setDefaultContext(scope,area):
        try: Cui.CuiCrgSetDefaultContext(Cui.gpc_info, area, scope)
        except AttributeError: 
            if scope.lower() == "object":
                Cui.CuiCrcEval(Cui.gpc_info,area,scope,"flight_number")
            else:
                Cui.CuiCrcEval(Cui.gpc_info,area,scope,"1")
                
    _setDefaultContext = staticmethod(_setDefaultContext)


def getCurrentLegIdentifier():
    """
    Returns the leg id of the leg under the mouse pointer
    """
    return Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiWhichArea,
                          "object", "leg_identifier")

def getCurrentTripIdentifier():
    """
    Returns the trip id of the leg under the mouse pointer
    """
    return Cui.CuiCrcEval(Cui.gpc_info, Cui.CuiWhichArea,
                          "object", "crr_identifier")

