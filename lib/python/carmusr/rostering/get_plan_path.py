"""
Usage, see comment at function get_path()
"""

import os

import Cui
import Variable
import carmensystems.rave.api as rave
from carmensystems.studio.private.teaming.carmstd import log

def get_and_create_path_to_export(basePath):
    '''
    Create and return a slash-separated path below basePath following the current plan. 
    Ie basePath + plan/path/, see also _get_open_plan_path()
    Returns None if not successful
    '''
    if basePath is None:
        return None
    
    if not basePath.endswith("/"):
        basePath = basePath + "/"

    subPath = get_open_plan_path()

    path = basePath + subPath + "/"
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            log.debug("Created: " + path)
        except OSError:
            log.debug("Failed to create: " + path)
            path = None
    log.debug("ExportPath: " + path)
    return path


def get_open_plan_path():
    '''
    Returns the slash-separated path to the current plan.
    Returns the empty string if no plan is loaded.

    # With no open plan
    >>> _get_open_plan_path()
    ''

    # With an open local plan
    >>> _get_open_plan_path()
    'Apr2007/FD-340/PROD_Dated_1'

    # With an open sub-plan
    >>> _get_open_plan_path()
    'Apr2007/FD-340/PROD_Dated_1/99.INITIAL'

    # With an open solution
    >>> _get_open_plan_path()
    'Apr2007/FD-340/PROD_Dated_1/99.INITIAL/Solution_2'
    '''

    lp_path = _get_local_plan_path()
    if not lp_path:
        return lp_path

    sp_path = _get_sub_plan_path()
    if not sp_path:
        return lp_path

    solution = _get_solution()
    if not solution:
        return sp_path
    else:
        return os.path.join(sp_path, solution)


def _get_local_plan_path():
    path_var = Variable.Variable("")
    Cui.CuiGetLocalPlanPath(Cui.gpc_info, path_var)
    return path_var.value


def _get_sub_plan_path():
    path_var = Variable.Variable("")
    Cui.CuiGetSubPlanPath(Cui.gpc_info, path_var)
    return path_var.value


def _get_solution():
    return rave.eval('global_solution_name')[0]

