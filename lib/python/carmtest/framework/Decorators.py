'''
Created on Feb 11, 2010

@author: rickard
'''


# Lent from Fredrik Acosta's code
def TODO(func):
    """
    unittest test method decorator that ignores exceptions raised by test
   
    Used to annotate test methods for code that may not be written yet.
    Ignores failures in the annotated test method; fails if the text
    unexpectedly succeeds.
    """
    def wrapper(*args, **kw):
        try:
            func(*args, **kw)
            succeeded = True
        except:
            succeeded = False
        assert succeeded is False, "%s marked TODO but passed" % func.__name__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def SKIP(func):
    """
    unittest test method decorator that skips a test
    """
    def wrapper(*args, **kw):
        return
    wrapper._skip = True
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return func

def REQUIRE(*prereq):
    """
    Specifies prerequisites for a test.
    """
    if len(prereq) == 1 and hasattr(prereq[0], 'func_code'):
        def wrapper(*args, **kw):
            assert False, "Test for '%s.%s': No prerequisite specified" % (prereq[0].__module__,prereq[0].__name__)
        return wrapper
    else:
        def decorator(func):
            if hasattr(func,'_prerequisite'):
                func._prerequisite += list(prereq)
                return func
            else:
                if func.__name__ != "__init__":
                    def wrapper(*a,**kw):
                        if len(a) > 0 and hasattr(a[0], 'hasPrerequisites'):
                            assert a[0].hasPrerequisites(func.__name__), "Test for '%s.%s': Prerequisites not met" % (func.__module__,func.__name__)
                            func(*a, **kw)
                else:
                    wrapper = func
                wrapper._prerequisite = list(prereq)
                wrapper.__name__ = func.__name__
                wrapper.__doc__ = func.__doc__
                return wrapper
        return decorator

