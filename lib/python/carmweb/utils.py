import os
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.expandvars("$CARMUSR/data/web")))

def template(name, vars):
    """
    Render a jinja2 template.
    @param vars: a dict with variables, e.g. locals()
    """
    tmpl = env.get_template(name)
    #print tmpl
    val = tmpl.render(**vars)
    #print val
    return val.encode('utf-8')
    
def webpage(func):
    """
    Annotation to specify that a function is a web page (GET)
    Function should take one argument, which is the request.
    """
    func.__web = True
    return func
    
def xmlrpc(func):
    """
    Annotation to specify that a function is exposed as a XML-RPC function
    """
    func.__xmlrpc = True
    return func