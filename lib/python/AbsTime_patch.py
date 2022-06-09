# ####
# AbsTime_patch.py
"""
AbsTime_patch
=============
    v1.2 2012-02-15 - added Leap Year tests, patch _actually_ reverts when there
                      is an error 

    This module contains a modification to AbsTime behaviour.
    It is implemented as a Monkey Patch. See the following Wikipedia entry for
    a reason to why the terminology: U{http://en.wikipedia.org/wiki/Monkey_patch}
    
    BACKGROUND
    ----------
    The AbsTime.AbsTime class contains a method called 'addmonths' that
    increases or decreases an AbsTime instance with N months.
    
    Unfortunately, this can lead to situations where the resulting dates
    are invalid:
    
    2010-10-31 - 4 months => 2010-06-31.
    
    The class has flags that optionally implements correct behaviour. The 
    AbsTime man page (unfortunately missing from CMS1) says:
    
    AbsTime AbsTime::addmonths (int n, unsigned flag = INVALID_EXCEPTION) const
    Add some months.
    
    Parameters:
        - n Number of months to add
        - flag the behaviour when the result would be invalid. 
          
        It can be one of these constants:
    
        - NEXT_VALID_DAY: use the next valid day
        - PREV_VALID_DAY: use the previous valid day
        - INVALID_EXCEPTION: use an exception (default)
          
    Exceptions:
        - RangeError,if the result is out of range.
        - InvalidArgument,if an unknown flag is used.
    
    
    MODIFIED BEHAVIOUR
    ------------------
    
    The modified behaviour of the AbsTime.AbsTime class will follow the logic in
    the following module: U{http://labix.org/python-dateutil}
    
    "...adding one month will never cross the month boundary. "
     
    This means that the act of adding one month to a date is *different*
    from the act of adding 30 days to a date. It now will behave like this:
    
    C{AbsTime.AbsTime.addmonths(n)}
    
    Add 'n' *calendar* months to the date represented by AbsTime.AbsTime.
    
        - 2010-01-31 + 1 => 2010-02-28
        - 2010-01-31 + 2 => 2010-03-31
        - 2010-03-30 - 1 => 2010-02-28
        - 2010-03-30 - 2 => 2010-01-30
    
    If you need to add a proper positive or negative amount of *DAYS* then do
    so by using the 'adddays' method.
    
    IMPLEMENTATION DETAILS
    ----------------------
    
    The class AbsTime in the module AbsTime is modified, so that any call to
    
    C{AbsTime.AbsTime.addmonths(n)}
    
    is transparently converted to this call:
    
    C{AbsTime.AbsTime.addmonths(n, AbsTime.PREV_VALID_DAY)}
    
    This is done by dynamically replacing the AbsTime.AbsTime.addmonth method
    with a new one at Studio start up time:
    
    C{import mod
    def newmeth(): ...
    mod.class.meth_orig = mod.class.meth
    mod.class.meth = newmeth}
    
    This has to be done at startup, when the AbsTime module is first imported,
    so the best way to do this is in CARMUSR/lib/python/StudioCustom.py
    
    U{import AbsTime
    import AbsTime_patch}

"""

# First we import the module with class that we want to modify.
# and check if we need to change it.

import AbsTime

def log(msg):
    # function to hook into better logging eventually
    print msg

try:
    __test_date = AbsTime.AbsTime(2010,1,31,0,0).addmonths(1)
except RuntimeError, e:
    if 'RangeError' not in e.args[0]:
        # This is not the error we are looking for,
        # raise the exception
        raise
    else:
        # This is the error we are looking for, so
        # we need to modify the AbsTime.AbsTime class

        def ___new_method(self, n, flag=AbsTime.PREV_VALID_DAY):
            # We return the new AbsTime by calling
            # the original method, with PREV_VALID_DAY
            return AbsTime.AbsTime.addmonths_orig(self, n, flag)

        # We are now modifying the class
        log('#################\n' \
            '### AbsTime.AbsTime.addmonths Monkey Patch to be applied!!\n' \
            '### version 1.2 - 2012-02-15 by Dario Lopez-Kasten, Jeppesen')

        # Keep old reference to method
        log('### 1. saving old method')
        AbsTime.AbsTime.addmonths_orig = AbsTime.AbsTime.addmonths

        # Do the Monkey Patch
        log('### 2. Applying patch')
        AbsTime.AbsTime.addmonths = ___new_method

        # Time to test
        log('### 3. Testing if patch works')
        __patch_OK = True
        try:
            # Test 1
            __testdate = AbsTime.AbsTime(2010,1,31,0,0).addmonths(1)
            __patch_works = (__testdate == AbsTime.AbsTime(2010,2,28,0,0))
            log('### TEST: 2010-01-31 + 1 month = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 2 - with flag PREV_VALID_DAY
            __testdate = AbsTime.AbsTime(2010,1,31,0,0).addmonths(1, AbsTime.PREV_VALID_DAY)
            __patch_works = (__testdate == AbsTime.AbsTime(2010,2,28,0,0))
            log('### TEST: 2010-01-31 + 1 month [flag PREV_VALID_DAY] = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 3 - with flag NEXT_VALID_DAY
            __testdate = AbsTime.AbsTime(2010,1,31,0,0).addmonths(1, AbsTime.NEXT_VALID_DAY)
            __patch_works = (__testdate == AbsTime.AbsTime(2010,3,1,0,0))
            log('### TEST: 2010-01-31 + 1 month [flag NEXT_VALID_DAY] = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 4 - with flag INVALID_EXCEPTION
            # Special case, provoke the error we are trying to avoid.
            # Fail if not excepted 
            try:
                __testdate = AbsTime.AbsTime(2010,1,31,0,0).addmonths(1, AbsTime.INVALID_EXCEPTION)
            except RuntimeError, e:
                if 'RangeError' in e.args[0]:
                    __patch_works = True
                else:
                    __patch_works = False
                log('### TEST: 2010-01-31 + 1 month [flag INVALID_EXCEPTION] = N/A ==> Status: %s'%(('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
                
        except RuntimeError, e:
            if 'RangeError' in e.args[0]:
                # We need to modify the AbsTime.AbsTime class
                __patch_works = False
                log('### ERROR: Patch did not work. See above results.')
                __patch_OK = False
            else:
                # Anything else has to be raised
                raise

        # Test Leap Years
        log('### 4. Testing if patch works with leap years (2012)')
        try:
            # Test 1
            __testdate = AbsTime.AbsTime(2012,1,31,0,0).addmonths(1)
            __patch_works = (__testdate == AbsTime.AbsTime(2012,2,29,0,0))
            log('### TEST: 2012-01-31 + 1 month = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 2 - with flag PREV_VALID_DAY
            __testdate = AbsTime.AbsTime(2012,1,31,0,0).addmonths(1, AbsTime.PREV_VALID_DAY)
            __patch_works = (__testdate == AbsTime.AbsTime(2012,2,29,0,0))
            log('### TEST: 2012-01-31 + 1 month [flag PREV_VALID_DAY] = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 3 - with flag NEXT_VALID_DAY
            __testdate = AbsTime.AbsTime(2012,1,31,0,0).addmonths(1, AbsTime.NEXT_VALID_DAY)
            __patch_works = (__testdate == AbsTime.AbsTime(2012,3,1,0,0))
            log('### TEST: 2012-01-31 + 1 month [flag NEXT_VALID_DAY] = %s ==> Status: %s'%(__testdate, ('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
            
            # Test 4 - with flag INVALID_EXCEPTION
            # Special case, provoke the error we are trying to avoid.
            # Fail if not excepted 
            try:
                __testdate = AbsTime.AbsTime(2012,1,31,0,0).addmonths(1, AbsTime.INVALID_EXCEPTION)
            except RuntimeError, e:
                if 'RangeError' in e.args[0]:
                    __patch_works = True
                else:
                    __patch_works = False
                log('### TEST: 2012-01-31 + 1 month [flag INVALID_EXCEPTION] = N/A ==> Status: %s'%(('FAIL', 'OK')[__patch_works]))
            if not __patch_works: __patch_OK = False
        except RuntimeError, e:
            if 'RangeError' in e.args[0]:
                # We need to modify the AbsTime.AbsTime class
                __patch_works = False
                log('### ERROR: Patch did not work. See above results.')
                __patch_OK = False
            else:
                # Anything else has to be raised
                raise
                
        if __patch_OK:
            log('### OK: Tests passed. Patch application successful!!')
        else:
            log('### ERROR: Patch application failed, reverting patch.')
            AbsTime.AbsTime.addmonths = AbsTime.AbsTime.addmonths_orig
            log('###  -> Patch reverted, original behaviour in place')

        log('### 5. Done!')
        log('#################')

