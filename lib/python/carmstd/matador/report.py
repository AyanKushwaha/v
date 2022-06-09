#######################################################

# report.py
# -----------------------------------------------------
# Matador Application
#
# Created:    2005-12-02
# By:         Carmen
#######################################################
"""
This module contains functionality for creating crg reports
in python.
"""

def saveReport(name,fullPath,format,area=None,scope=None):
    """
    Saves a report in a specified format.
    """
    if format!="ascii":
        raise ValueError("Unsupported report format in Matador")
    MatadorScript.generate_pdl_report(name,fullPath)
