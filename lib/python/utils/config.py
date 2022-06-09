import utils.ServiceConfig as ServiceConfig

# This is so that when we reload the file, we get a new service config
# on the next call to get_default_service_config
try:
    __default_config
except:
    __default_config = None
if __default_config is not None:
    __default_config = None

def get_default_service_config(reload=False):
    '''
    Returns a ServiceConfig object corresponding to the default configuration files.
    This method will return the same object on consecutive calls so that the hit to parse
    the configuration is only taken once.
    '''
    global __default_config
    if reload or __default_config is None:
        __default_config = ServiceConfig.ServiceConfig()
    return __default_config
