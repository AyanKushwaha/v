#

#

import pwd, os

__version__ = '$Revision$'
__author__ = 'Christoffer Sandberg, JeppesenSystems AB'

# Module wide variable to cache the username
data = {'user_name':None}

def username():
    '''
    Attempts to retrieve the username. If we fail to retrieve the correct username, we will return 'unknown(uid:0123)'
    where uid:<number> is the interal unix id of the user (i.e, id <username> from a command prompt
    If it is imperative to have an absolute correct username even when the pwd service is out, do not use this wrapper
    See also Names.py in lib/python of the CARMSYS
    '''
    
    user_name = data['user_name']
    # If the username is 'unknown', try and look it up again
    if user_name is None or user_name.lower().startswith('unknown'):
        uid = os.getuid()
        try:
            user_name = pwd.getpwuid(uid)[0]
        except KeyError:
            # Ok, for some reason we could not find the username the proper way, try $USER instead
            try:
                user_name = os.environ.get("USER",None)
                if user_name is None or user_name.lower().startswith('unknown'):
                    # Didn't really help much, go with "unknown" for the moment
                    user_name = 'unknown(uid:%s)' %s (str(uid))

            except OSError, KeyError:
                user_name = 'unknown(uid:%s)' %s (str(uid))
        data['user_name'] = user_name
    return user_name

    
