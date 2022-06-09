# File: <NiceToHaveIQ>/lib/python/nth/studio/report_generation.py
#
"""
Some functions for generation of PRT reports.

@author Stefan Hammar

Copied from NiceToHaveIQ in March 2012. 

"""

import tempfile
import os
import sys
import traceback

import Crs
import Cui
import Csl
import carmensystems.publisher.api as p
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator

def format_check_and_fix(format):
    if not format: 
        return None
    if type(format) == type(p.PDF):
        return {p.TXT:"TXT", p.HTML:"HTML", p.PDF:"PDF"}[format]
    
    format = format.upper()
    if format not in ("TXT", "PDF", "HTML"):
        raise ValueError('Only the formats "TXT", "PDF", "HTML" are supported')
       
    return format    

def source_fix(source=None):
    """
    Returns, if possible, source definitions accepted by Studio functions 
    resp. low-level-prt functions given any prt report source definition.
    None as argument means that sys.argv[1]/sys.argv[0] is used as source.
    """
    if source == None:
        source = sys.argv[1] + "/" + sys.argv[0]

    if source[-3:] != ".py":
        source = "/".join(source.split(".")) + ".py"

    if source.find("nth/studio/prt") >= 0: # for reports in nth
        source = "nth_reports" + source.split("nth/studio/prt")[-1]
    else:
        source = source.split("report_sources/")[-1]     
    msource = "report_sources." + ".".join(source.split("/"))[:-3]
    
    try:
        exec("import %s" % msource)  # test to import the module.
    except ImportError:
        raise ImportError("There is no module named '%s'" % msource)
    
    return source, msource
    
    
def display_prt_report(gpc_info=Cui.gpc_info,
                       area=Cui.CuiNoArea,
                       scope="None",
                       source=None,
                       flags=0,
                       rpt_args="",
                       format=None): 
    """
    Similar to CuiCrgDisplayTypesetReport. 
    Differences: 
       * you can define HTML/PDF/TXT as format (as string or integer). 
         If you specify None, "" or 0 the resource "preferences.PRTReportFormat" 
         is considered.
       * if you don't specify source, sys.argv[1]/sys.argv[0] is used 
       * the arguments are named and have default values
       * both Studio and Rave format for rpt_args are accepted
       * the source could be a module name or a file name.
       
    Limitations:
       * The report definition module must be in a directory below
         "$CARMUSR/lib/python/report_sources", due to limitations
         in the used function "CuiCrgDisplayTypesetReport"
       * Flags are ignored for the format "TXT".

    Exceptions: A NameError exception is raised if the specified report 
                definition does not exist.
    """
    
    format = format_check_and_fix(format)            
    
    if isinstance(rpt_args, dict): 
        rpt_args = " ".join(["%s=%s" % (k, v) for k, v in rpt_args.items()])

    saved_sys_argv = sys.argv[:]
    
    source, msource = source_fix(source)
    
    if format == "TXT":
        fd, fn = tempfile.mkstemp(suffix=".txt")
        p.generateReport(msource,
                         fn, p.TXT, rpt_args,
                         CuiContextLocator(area, scope))
        Csl.Csl().evalExpr('csl_show_file("%s","%s")' % 
                           (source.split("/")[-1], fn))
        os.unlink(fn)
        os.close(fd) 
    else:
        # Note: In later versions of Studio "CuiCrgDisplayTypesetReport" supports 
        #       a 7th argument defining the format as "HTML" or "PDF".
        if format:
            sf = Crs.CrsGetModuleResource("preferences", Crs.CrsSearchModuleDef,
                                          "PRTReportFormat")
            Crs.CrsSetModuleResource("preferences", "PRTReportFormat",
                                     format, "")
        try:
            Cui.CuiCrgDisplayTypesetReport(gpc_info, area,
                                           scope, source,
                                           flags, rpt_args)
        except:
            print traceback.format_exc()
            
        if format:
            Crs.CrsSetModuleResource("preferences", "PRTReportFormat", sf, "")

    sys.argv[:] = saved_sys_argv

def get_report_module():
    """
    Imports the "current" PRT module. 
    Uses sys.argv[0] and sys.argv[1] to figure out the module name. 
    "sys.argv" gets correct when any of the following is used:
    * "Run" button of the "Python Code Manager" in the "Special/Scripts" menu
    * "Run" button of the "Python Code Manager..." in the "Admin Tools" menu
    * The command "Run in Studio" in "DWS" / "Python IDE".
    
    Returns (module object, dirname, filename)
    """
    file_name = sys.argv[0]
    dir_name = os.path.split(sys.argv[1])[-1]
    if dir_name == "prt": # Report in NTH
        dir_name = "nth_reports"
    me = __import__("report_sources.%s.%s" % (dir_name, file_name[:-3]),
                    globals(), locals(), ["_"])
    
    return me, dir_name, file_name

def reload_report_def():
    """
    Reloads the current PRT module. 
    Uses "get_report_module"

    Returns (dirname, filename) 

    """

    me, dir_name, file_name = get_report_module()
    reload(me)
    
    return (dir_name, file_name)


def reload_and_display_report(format=None):
    """
    This functions is supposed to be called in the self testing part
    of files defining PRT reports.
                        
    @param format: defines the format of the report.
                   TXT, HTML, PDF or None (use the preference). 
    @type format: string or integer
    """
    reload_report_def()
    display_prt_report(format=format)

if __name__ == "__main__":
    display_prt_report(source="report_sources.hidden.retiming")
    
