#######################################################

# rave.py
# -----------------------------------------------------
# Matador Application
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
Rave Context handling.

Most calls to the rave api should be done using
an instance of a Context class or a subclass of it.

"""
class Context(object):
    """
    Context class is not used in Matador.
    The class is simply a container class that is used by the
    carmstd.rave module.
    """
    def __init__(self, buffer="sp_crew",area=None):
        self._buffer = buffer.lower()

    def _getContextId(self):
        return self._buffer    

    def eval(self,*args):
        """
        As eval in the Rave api, but in the defined context.
        args: Rave api code
        Return: tuple
        """
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
    
    

