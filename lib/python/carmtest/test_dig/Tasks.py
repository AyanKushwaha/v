__C = None
def _C():
    from utils import ServiceConfig
    global __C
    if __C == None: __C = ServiceConfig.ServiceConfig()
    return __C