'''
Functions for handling external tables.
From OTS by Retiming project in Feb 2012. 
'''

import os
import shutil

import Cui
import Variable
import Crs
import carmensystems.rave.api as rave
from carmensystems.mave import etab

from carmstd import plan


def load(session, etab_path, copy_from=None, forceSp=False):
    """
    Extends the carmensystems.mave.etab.load function to expand relative
    paths through 'get_ideal_absolute_etab_path'.
    Also allows copying a table from fallback location before load if
    needed.

    Examples
    --------

    .. python::
        >>> crew_info_table = load(session, 'crew.%crew_info_table%')

    :param session: A mave session object
    :param etab_path: A path to an external table. See 'get_ideal_absolute_etab_path' for more info.
    :param copy_from: Path to copy from if table not found.
    :param forceSp: force the adding of 'SpLocal' to the search path
    """

    etab_path = os.path.expandvars(etab_path)  # Resolve environment variables
    if not etab_path:
        raise ValueError('Path is empty')

    if etab_path[0] == '/':
        return etab.load(session, etab_path)
    else:
        etab_full_path = get_ideal_absolute_etab_path(etab_path, forceSp)

        if not (os.path.exists(etab_full_path)) and copy_from is not None:
            shutil.copy(copy_from, etab_full_path)
            # log.info("%s copied to %s" % (copy_from, etab_full_path))
            table = etab.load(session, etab_full_path)
            table.clear()
            table.save()
            return table
        return etab.load(session, etab_full_path)

class EtableNotFoundException(Exception):
    '''
    Raised by "get_existing_absolute_etab_path" if no external table was found matching
    the etable_path given.
    '''
    pass


def get_ideal_absolute_etab_path(etab_path, forceSp=False):
    """
    The function returns the paths with the highest precedence,
    independently of whether the table exists or not

    For convenience, if the etab_path contains a percentage sign (%),
    it is interpreted as a rave variable and will be evaluated prior
    to searching. This is the most common, and recommended, use pattern
    since the location of external tables are often rave parameters.

    Examples
    --------

    .. python::
        >>> get_ideal_absolute_etab_path('SpLocal/coterminals.etab')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        # Using a rave variable (recommended!)
        >>> get_ideal_absolute_etab_path('leg.%coterminals_table%')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        # When sub-plan doesn't contain fallback.etab
        >>> get_ideal_absolute_etab_path('SpLocal/fallback.etab')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/fallback.etab

    :param etab_path: Relative path to an external table
    :type etab_path: str

    :returns: Absolute path to the external table
    :rtype: str
    """
    etab_path = get_validate_path(etab_path, forceSp)
    etab_candidates = _get_etab_candidates(etab_path)
    return etab_candidates[0]


def get_existing_absolute_etab_path(etab_path):
    """
    The function will return the path to the first *existing* table
    which matches the relative etab_path given

    For convenience, if the etab_path contains a percentage sign (%),
    it is interpreted as a rave variable and will be evaluated prior
    to searching. This is the most common, and recommended, use pattern
    since the location of external tables are often rave parameters.

    Raises an 'EtableNotFoundException' if no file is found.

    Examples
    --------

    .. python::
        >>> get_existing_absolute_etab_path('SpLocal/coterminals.etab')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        # Using a rave variable (recommended!)
        >>> get_existing_absolute_etab_path('leg.%coterminals_table%')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        # When the table cannot be found anywhere
        >>> get_existing_absolute_etab_path('not_found.etab')
        Traceback (most recent call last):
          ...
        carmstd.etab_ext.EtableNotFoundException: Couldn't find file not_found.etab

    :param etab_path: Relative path to an external table
    :type etab_path: str

    :returns: Absolute path to the external table
    :rtype: str
    """
    etab_path = get_validate_path(etab_path)
    abs_path = rave.search_etable_identifier(etab_path)
    if not abs_path:
        raise EtableNotFoundException("Couldn't find file %s" % etab_path)

    return abs_path


def get_validate_path(etab_path, forceSp=False):
    if not etab_path:
        raise ValueError('Path is empty')

    # path should not start from root
    if etab_path[0] == '/':
        raise ValueError('Not a relative path: %s' % etab_path)

    if '%' in etab_path:
        # Assume it is a rave variable and ask rave for it,
        # raises an exception if not found
        etab_path = rave.eval(etab_path)[0]

    if forceSp and not etab_path.startswith('SpLocal'):
        etab_path = 'SpLocal/' + etab_path

    return etab_path


def get_relative_path(table_path):
    """
    Given an absolute path to an external table, returns the relative path
    (as used by rave).

    Examples
    --------

    .. python::
        >>> expanded_path = get_ideal_absolute_etab_path('SpLocal/coterminals.etab')

        >>> print expanded_path
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        >>> get_relative_path(expanded_path)
        SpLocal/coterminals.etab
    """
    if not table_path or table_path[0] != '/':
        raise ValueError('Not an absolute path: %s' % table_path)

    # We need to run all paths through realpath to resolve symbolic
    # links.
    table_path = os.path.realpath(table_path)
    if plan.sub_plan_is_loaded():
        splocal_path = os.path.realpath(get_splocal_path())
    else:
        splocal_path = None

    if plan.local_plan_is_loaded():
        lplocal_path = os.path.realpath(get_lplocal_path())
    else:
        lplocal_path = None

    rave_path = None
    if splocal_path and table_path.startswith(splocal_path):
        prefixlen = len(splocal_path) - len('SpLocal')
        rave_path = table_path[prefixlen:]
    elif lplocal_path and table_path.startswith(lplocal_path):
        prefixlen = len(lplocal_path) - len('LpLocal')
        rave_path = 'LpLocal/' + table_path[len(lplocal_path):]
    else:
        for search_path in _get_etab_search_path():
            search_path = os.path.realpath(search_path)
            if table_path.startswith(search_path):
                # Add one for the trailing slash
                prefixlen = len(search_path) + 1
                rave_path = table_path[prefixlen:]
    if rave_path:
        return rave_path
    else:
        raise ValueError('Could not resolve %s '
                         'to a relative path' % table_path)


def _get_etab_search_path():
    '''
    Parses the resource ``default.default.CRC_ETAB_PATH``, returning it
    as a list of directories. Also includes SpLocal and LpLocal shadow
    directories.
    
    :rtype: `list`
    '''
    etab_path_string = Crs.CrsGetAppModuleResource("default",
                                                   Crs.CrsSearchAppExact, 
                                                   "default",
                                                   Crs.CrsSearchModuleExact, 
                                                   "CRC_ETAB_PATH")
    # Split the string into a list
    etab_path_split = etab_path_string.split(";")
    etab_search_path = []
    # Remove the prefix "file:" if it exists
    for i in etab_path_split:
        if i.startswith("file:"):
            etab_search_path.append(i[5:])
        else:
            etab_search_path.append(i)
    return etab_search_path


def _get_etab_candidates(etab_path):
    '''
    Returns a list of candidate absolute paths to the given
    relative path in decreasing order of preference. 
    
    :rtype: `list`
    '''
    
    etab_search_path = _get_etab_search_path()
    
    if etab_path.startswith('SpLocal') and plan.sub_plan_is_loaded():
        # Strip the last SpLocal component from the path
        splocal_path = get_splocal_path()[:-len('/SpLocal')]
        etab_search_path.insert(0, splocal_path)

    if etab_path.startswith('LpLocal') and plan.local_plan_is_loaded():
        # Strip the last LpLocal component from the path
        lplocal_path = get_lplocal_path()[:-len('/LpLocal')]
        etab_search_path.insert(0, lplocal_path)

    etab_candidates = [os.path.join(dir_, etab_path) for dir_ in etab_search_path]
    return etab_candidates

class EtableNotFoundException(Exception):
    '''
    Raised by `expand_etab_path` if no external table was found matching
    the etable_path given.
    '''
    pass

def expand_etab_path(etab_path, use_fallback = False):
    """
    Resolves a relative path to an external table to an absolute path.

    By setting ``use_fallback`` to ``True``, the function will return
    the path to the first *existing* table which matches the relative
    etab_path given. If set to ``False`` (default), the function returns
    the paths with the highest precedence, independently of whether
    the table exists or not.
    
    For convenience, if the etab_path contains a percentage sign (%), 
    it is interpreted as a rave variable and will be evaluated prior
    to searching. This is the most common, and recommended, use pattern
    since the location of external tables are often rave parameters.
    
    Raises an `EtableNotFoundException` if no file is found when
    use_fallback is set to ``True``.

    Examples
    --------
    
    .. python::
        >>> expand_etab_path('SpLocal/coterminals.etab')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab
        
        # Using a rave variable (recommended!)
        >>> expand_etab_path('leg.%coterminals_table%')
        /tmp/SpShadow_wqMNcC/etable/SpLocal/coterminals.etab

        # When sub-plan doesn't contain fallback.etab, but use_fallback is set to False
        >>> expand_etab_path('SpLocal/fallback.etab', use_fallback = False)
        
        # Same example with use_fallback set to True
        >>> expand_etab_path('SpLocal/fallback.etab', use_fallback = True)
        <$CARMUSR>/crc/etable/SpLocal/fallback.etab
        
        # When the table cannot be found anywhere
        >>> expand_etab_path('not_found.etab', use_fallback = True)
        Traceback (most recent call last):
          ...
        carmstd.etab_ext.EtableNotFoundException: Couldn't find file not_found.etab

    :param etab_path: Relative path to an external table    
    :type etab_path: `str`

    :returns: Absolute path to the external table
    :rtype: `str`
    """
    
    if not etab_path:
        raise ValueError('Invalid argument %s' % etab_path)
    
    # If the path is absolute, we simply return it
    if etab_path[0] == '/':
        return etab_path
    
    if '%' in etab_path:
        # Assume it is a rave variable and ask rave for it, 
        # raises an exception if not found
        etab_path = rave.eval(etab_path)[0]

    etab_candidates = _get_etab_candidates(etab_path)

    if not use_fallback:
        return etab_candidates[0]
    else:
        first_existing_candidate = None
        for etab_candidate in etab_candidates:
            if os.path.exists(etab_candidate):
                first_existing_candidate = etab_candidate
                break
        if first_existing_candidate:
            return first_existing_candidate
        else:
            raise EtableNotFoundException("Couldn't find file %s" % etab_path) 

def get_splocal_path():
    ''' 
    Returns the absolute path to SpLocal for the currently loaded sub-plan.
    
    Note that the only safe way (in a multi-user environment) of altering 
    the contents of SpLocal in an existing sub-plan is to first load the
    sub-plan into memory. Otherwise you risk editing a sub-plan which
    is already loaded by another user.

    See also `expand_etab_path`

    Example
    -------
    
    .. python::
        # With a sub-plan loaded
        >>> etab_ext.get_splocal_path()
        /tmp/SpShadow_wqMNcC/etable/SpLocal

        # With no sub-plan loaded.
        >>> etab_ext.get_splocal_path()
        Traceback (most recent call last):
          ...
        RuntimeError: No sub-plan loaded

    :return: Absolute path to SpLocal
    :rtype: `str`
    '''
    if not plan.sub_plan_is_loaded():
        raise RuntimeError('No sub-plan loaded')

    var = Variable.Variable("")
    Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, var)
    print var.value
    return var.value

def get_lplocal_path():
    ''' 
    Returns the absolute path to LpLocal for the currently loaded local plan. 

    See `get_splocal_path` for a warning about multi-user environments.
    
    Example
    -------

    .. python::

        # With a local plan loaded. 
        >>> etab_ext.get_lplocal_path()
        /tmp/LpShadow_NnQH3g/etable/LpLocal

        # With no local plan loaded.
        >>> etab_ext.get_lplocal_path()
        Traceback (most recent call last):
          ...
        RuntimeError: No local plan loaded

    :return: Absolute path to LpLocal
    :rtype: `str`
    '''
    if not plan.local_plan_is_loaded():
        raise RuntimeError('No local plan loaded')

    var = Variable.Variable("")
    Cui.CuiGetLocalPlanEtabLocalPath(Cui.gpc_info, var)
    return var.value
