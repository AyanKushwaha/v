'''
Created on Feb 15, 2010

@author: rickard
'''
import Csl
from String import String
csl = Csl.Csl()
import os

rpcsrv = None
def rpc_server_field():
    csl.setString("rpc_server_field", String(rpc_server()))
    
def rpc_server():
    global rpcsrv
    if rpcsrv == None:
        try:
            rpcsrv = load_rpc()
        except:
            import traceback
            traceback.print_exc()
            rpcsrv = "(Error)"
    return rpcsrv

def load_rpc():
    import carmensystems.studio.private.RaveServer as RaveServer
    import os
    try:
        host = os.environ["HOST"]
    except:
        host = ""
    return "%s:%d" % (host, RaveServer.WS.get_port_number(6705))

