#######################################################

# rave.py
# -----------------------------------------------------
# #
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
Rave Context handling.

Most calls to the rave api should be done using
an instance of a Context class or a subclass of it.

"""
import carmensystems.rave.api as R
from application import application
if application=="Matador":
    import carmstd.matador.rave as rave
else:
    import carmstd.studio.rave as rave

class Context:
    def __init__(self, buffer="sp_crew",area=None):
        """
        buffer: 'plan', 'window', 'object' or an existing Rave context.
        area:    Needed when buffer is 'window' or 'object'. Not used for matador.

        Note: When the buffer is 'plan', 'window' or 'object' a global
              definition in Studio is set by the __init__ method.
              Therefore only one class instance of that kind may exist.
        Note: Many Cui functions (e.g. CuiCrcEval) reset the global
              definition in Studio. After a call of such a function the
              "reInit" method must be called. 
        """
        self.context = rave.Context(buffer,area)   

    def eval(self,*args):
        """
        As eval in the Rave api, but in the defined context.
        args: Rave api code
        Return: tuple
        """
        return self.context.eval(*args)

    def simpleEvalSingleExpr(self,expr,iter="leg_set",filter=None,sort=None):
        """
        Creates a list of values for the defined set of objects.
        'expr'is a rave expression.
        'iter' is an iterator.

        filter: A rave expression or a tulple of rave expression
        sort: A rave expression or a tuple of rave expressions
        
        """
        return self.context.simpleEvalSingleExpr(expr,iter,filter,sort)

    def getCrrIdentifiers(self,filter="true",sort="true",iter="iterators.trip_set" ):
        """
        Returns a list of crr identifier strings
        Only valid for studio
        """
        return self.context.getCrrIdentifiers(filter,sort,iter) 
    
    def getLegIdentifiers(self,filter="TRUE",sort ="TRUE", iter="iterators.leg_set"):
        """
        Return a list of leg identifier strings
        """
        return self.context.getLegIdentifiers(filter,sort,iter) 

    def getCrewIdentifiers(self,filter="TRUE",sort ="TRUE", iter="iterators.roster_set"):
        """
        Return a list of crew identifiers
        """
        return self.context.getCrewIdentifiers(filter,sort,iter)

    def getCurrentLegIdentifier(self):
        """
        Returns the leg_id of the leg under the mouse pointer
        """
        return rave.getCurrentLegIdentifier()

    def getCurrentTripIdentifier(self):
        """
        Returns the trip id of the leg under the mouse pointer
        """
        return rave.getCurrentTripIdentifier()

        
