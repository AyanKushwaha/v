"""
Module for actions that can be applied to plans.
"""

import os

import Cui
import Variable
import Errlog
import Crs
import carmensystems.rave.api as rave
from __main__ import exception as StudioException  # @UnresolvedImport


def open_plan(plan_path, confirm=True, silent=False, force=False):
    '''
    Opens a plan by it's slash-separated path.

    # Opens a local plan
    >>> open_plan('AAA/BBB/CCC')

    # Opens a sub-plan
    >>> open_plan('AAA/BBB/CCC/DDD')

    # Opens a specific solution
    >>> open_plan('AAA/BBB/CCC/DDD/best_solution')
    '''

    split_name = plan_path.split('/')
    if len(split_name) < 3 or len(split_name) > 5:
        raise ValueError('Invalid plan name: %s' % plan_path)

    flags = _get_cui_flags(confirm, silent, force)

    lp_name = '/'.join(split_name[:3])
    if len(split_name) == 3:
        Cui.CuiOpenLocalPlan(Cui.gpc_info, lp_name, flags)
        return

    sp_name = '/'.join(split_name[:4])
    if len(split_name) == 4:
        Cui.CuiOpenSubPlan(Cui.gpc_info, lp_name, sp_name, flags)
        return

    solution = split_name[4]
    Cui.CuiLoadSolution(Cui.gpc_info, lp_name, sp_name, solution, flags)


def save_local_plan(save_as=None, confirm=False, silent=True, force=True):
    """
    Saves the current local plan.

    @param save_as: If given, a path to which the plan should be saved.

    # Saves the current local plan
    >>> save_local_plan()

    # Saves the current sub-plan to a new name
    >>> save_local_plan('A/NEW/NAME')

    """
    flags = _get_cui_flags(confirm, silent, force)
    Cui.CuiSaveLocalPlan(Cui.gpc_info, save_as, flags)


def save_subplan(save_as=None, confirm=False, silent=True, force=True):
    """
    Saves the current sub-plan.

    # Saves the current sub-plan
    >>> save_subplan()

    # Saves the current sub-plan to a new name
    >>> save_subplan('new_name')

    # This works
    >>> save_subplan('the/current/localplan/new_name')

    # But this raises a ValueError
    >>> save_subplan('a/new/localplan/new_name')

    @param save_as: If given, a path to which the plan should be saved.
                    Can either be an atomic name

    """
    flags = _get_cui_flags(confirm, silent, force)

    if not save_as:
        save_as = 0
    else:
        split_name = save_as.split('/')
        if len(split_name) not in (1, 4):
            raise ValueError('Invalid sub-plan path: %s' % save_as)

        if len(split_name) == 4:
            lp_path = _get_local_plan_path()
            if '/'.join(split_name[:3]) != lp_path:
                err = ('Sub-plan path %s is not relative to '
                       'current local plan %s' % (save_as, lp_path))
                raise ValueError(err)
            save_as = split_name[3]

    Cui.CuiSaveSubPlan(Cui.gpc_info, save_as, flags)


def save_plans(confirm=False, silent=True, force=True):
    """
    Saves the current local and sub-plan.
    """
    flags = _get_cui_flags(confirm, silent, force)
    Cui.CuiSavePlans(Cui.gpc_info, flags)


def get_plan_path():
    '''
    Returns the slash-separated path to the current plan.

    Returns the empty string if no plan is loaded.

    # With no open plan
    >>> get_plan_path()
    ''

    # With an open local plan
    >>> get_plan_path()
    'Apr2007/FD-340/PROD_Dated_1'

    # With an open sub-plan
    >>> get_plan_path()
    'Apr2007/FD-340/PROD_Dated_1/99.INITIAL'

    # With an open solution
    >>> get_plan_path()
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


def _get_cui_flags(confirm=True, silent=False, force=False):
    flags = 0
    if not confirm:
        flags |= 1
    if silent:
        flags |= 2
    if force:
        flags |= 4
    return flags


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


def set_sp_comment(comment):
    """
    Set sub-plan comment.

    @param comment: Comment to set in the sub-plan"
    @type comment: str
    """
    Cui.CuiSetSubPlanComment(Cui.gpc_info, comment)


def local_plan_is_loaded():
    """Checks whether a local plan is loaded.

    @return: True if a local plan is loaded, False otherwise.
    @rtype: bool
    """
    try:
        get_current_local_plan()
    except ValueError:
        return False
    return True


def sub_plan_is_loaded():
    """Checks whether a sub-plan is loaded.

    @return: True if a sub-plan is loaded, False otherwise.
    @rtype: bool
    """
    try:
        get_current_sub_plan()
    except ValueError:
        return False
    return True


def get_current_local_plan():
    """
    Returns a local plan instance of the
    currently loaded local plan

    @return: The currently loaded Local Plan
    @rtype: LocalPlan
    """
    localplan_path = Variable.Variable("")
    Cui.CuiGetLocalPlanPath(Cui.gpc_info, localplan_path)
    if localplan_path.value == '':
        raise ValueError("No local plan loaded")

    return LocalPlan(localplan_path.value)


def get_current_sub_plan():
    """
    Returns a sub-plan instance of the
    currently loaded sub-plan

    @return: The currently loaded sub-plan.
    @rtype: SubPlan
    """
    sub_plan = Variable.Variable("")
    Cui.CuiGetSubPlanName(Cui.gpc_info, sub_plan)
    if sub_plan.value == '':
        raise ValueError("No sub-plan loaded")
    return SubPlan(sub_plan.value, get_current_local_plan())


class LocalPlan(object):
    """
    Local plan class for working with local plans.
    Holds the local plan attributes and contains
    methods for loading and saving plans.
    """
    def __init__(self, file_path):
        """
        Create a LocalPlan object

        @type file_path: string
        @param file_path: Path relative to the directory defined by the CRS resource LocalPlanPath
        """
        self.file_path = file_path

    def is_current(self):
        """
        Checks whether the local plan is in memory.

        @return: True if the local plan is in memory
        @rtype: Bool
        """
        try:
            return get_current_local_plan() == self
        except ValueError:  # Raised if no local plan is loaded
            return False

    def get_file_name(self):
        """
        Get the name of the local plan in the LocalPlan object.

        @return: File name of the Local plan
        @rtype: string
        """
        return os.path.basename(self.file_path)

    def get_file_path(self):
        """
        Returns the file path of the local plan relative to
        the directory defined by the CRS resource LocalPlanPath

        @return: File path to the Local Plan
        @rtype: string
        """
        return self.file_path

    def get_abs_path(self):
        """
        Get the absolute path of the Local Plan file.

        @return: Absolute path to the local plan file
        @rtype: string
        """
        lp_directory = Crs.CrsGetModuleResource("config",
                                                Crs.CrsSearchModuleDef,
                                                "LocalPlanPath")
        return os.path.join(lp_directory, self.file_path)

    def get_etab_path(self):
        """
        Get the etab path for local plan etables.
        The path returned is absolute. The plan needs to be loaded
        before invoking this method, otherwise a ValueError is raised.

        @return: File path to the local plan etables
        @rtype: string
        """
        if not self.is_current():
            raise ValueError('Local plan is not loaded.')

        var = Variable.Variable("")
        Cui.CuiGetLocalPlanEtabLocalPath(Cui.gpc_info, var)
        return var.value

    def load(self):
        """
        Load the local plan
        """
        Cui.CuiOpenLocalPlan(Cui.gpc_info, self.file_path)

    def unload(self):
        """
        Unloads a local plan from memory.
        If a sub-plan is loaded the plan is
        unloaded as well
        """
        Cui.CuiUnloadPlans(Cui.gpc_info, Cui.CUI_SILENT)

    def save(self):
        """
        Saves the LocalPlan with same name.

        @raise ValueError: if the local plan is not loaded
        """
        if not (self == get_current_local_plan()):
            raise ValueError("The local plan is not loaded, "
                             "and hence can it not be saved!")
        self.save_as(self.file_path)

    def save_as(self, file_path):
        """
        Saves the the LocalPlan as filePath

        @param file_path: Path relative to the directory
                         defined by the Crs resource LocalPlanPath
        @type file_path: string
        @raise ValueError: if the plan is not loaded
        """
        if not (self == get_current_local_plan()):
            raise ValueError("The local plan is not loaded, "
                             "and hence can it not be saved!")
        self.file_path = file_path

        flags = (Cui.CUI_SAVE_DONT_CONFIRM | Cui.CUI_SAVE_SILENT |
                 Cui.CUI_SAVE_FORCE | Cui.CUI_SAVE_SKIP_SP)
        if file_path is None:
            Cui.CuiSavePlans(Cui.gpc_info, flags)
        else:
            Cui.CuiSaveLocalPlan(Cui.gpc_info, file_path, flags)

    def __eq__(self, other):
        """
        Compare two local plans
        Plans are considered to be equal if the file path is equal.

        @param other: The relative path of the local plan that should be compared
        @type other: LocalPlan
        """
        return (isinstance(other, LocalPlan) and
                self.get_file_path() == other.get_file_path())


class SubPlan(object):
    """
    Class for sub-plans.
    Holds attributes for a sub-plan and contains methods
    for performing sub-plan operations.

    Ex.
    SubPlan('BASE',LocalPlan('$CARMUSR/LOCAL_PLAN/PLANNING-AREA/OLD_VERSION/ALL_BASES'))
    SubPlan.load()
    SubPlan.save_as('BASE',LocalPlan('$CARMUSR/LOCAL_PLAN/PLANNING-AREA/NEW_VERSION/ALL_BASES'))
    SubPlan.load_crew('CrewTable.etab')
    SubPlan.save()
    """

    @classmethod
    def from_file_path(cls, file_path):
        """Creates a SubPlan object from a file path

        This is a convenient non-default constructor. Instead of
        writing::

          sp = SubPlan('sp_name', LocalPlan('planning_area/version/base'))

        you can instead use::

          sp = SubPlan.from_file_path('planning_area/version/base/sp_name')

        @param file_path: Path to the sub-plan relative to LOCAL_PLAN
        @type file_path: string

        @return: A SubPlan object with the path given as argument
        @rtype: SubPlan
        """
        lp_path, sp_file_name = os.path.split(file_path)
        local_plan = LocalPlan(lp_path)
        return cls(sp_file_name, local_plan)

    def __init__(self, file_name, localplan):
        """
        Create a SubPlan object. The object holds the name of the sub-plan
        and a LocalPlan object to the corresponding local plan.

        The method does not load the sub-plan into memory. Use load() for that.
        @param file_name: Name of the sub-plan
        @type file_name: string
        @param localplan: The local plan where the sub-plan resides
        @type localplan: LocalPlan

        @raise TypeError: If local plan does not have the type LocalPlan.
        """
        self.file_name = file_name
        if not isinstance(localplan, LocalPlan):
            raise TypeError("local plan must be LocalPlan instance")
        self.localplan = localplan

    def get_file_name(self):
        """
        Get the name of the sub-plan.

        @return: file_name
        @rtype: string
        """
        return self.file_name

    def get_file_path(self):
        """
        Get the file path to the sub-plan.

        @return: file path relative to directory defined by\
                 the Crs resource LocalPlanPath
        @rtype: string
        """
        return os.path.join(self.localplan.get_file_path(), self.file_name)

    def get_abs_path(self):
        """
        Returns the absolute path of the sub-plan file specified in the
        sub-plan object.

        @return: Absolute path to the sub-plan file
        @rtype: string
        """
        return os.path.join(self.localplan.get_abs_path(), self.file_name)

    def get_etab_path(self):
        """
        Return the etab path for sub-plan local etables.
        The method requires that the sub-plan is loaded into
        memory, otherwise a ValueError is raised.

        @return: Path to the sub-plan etables (SpLocal)
        @rtype: string
        """
        if not self.is_current():
            raise ValueError('Sub-plan is not loaded.')

        var = Variable.Variable("")
        Cui.CuiGetSubPlanEtabLocalPath(Cui.gpc_info, var)
        return var.value

    def get_local_plan(self):
        """
        Return a LocalPlan object for the local plan the is used
        for the sub-plan.

        @return: Local plan associated with the sub-plan object
        @rtype: LocalPlan
        """
        return self.localplan

    def load(self):
        """
        Load the sub-plan into memory.
        Loads the plan silent without confirmations.
        """
        flags = (Cui.CUI_OPEN_PLAN_SILENT | Cui.CUI_OPEN_PLAN_DONT_CONFIRM |
                 Cui.CUI_OPEN_PLAN_FORCE)
        Cui.CuiOpenSubPlan(Cui.gpc_info, self.localplan.get_file_path(),
                           self.get_file_path(), flags)

    def load_solution(self, solution):
        """
        Load a solution of a sub-plan into memory.
        Loads the solution silent without confirmation.

        @param solution: Name of the solution to load, e.g. Solution_1
        @type solution: String.
        """
        flags = (Cui.CUI_LOAD_SOLUTION_DONT_CONFIRM |
                 Cui.CUI_LOAD_SOLUTION_SILENT |
                 Cui.CUI_LOAD_SOLUTION_FORCE)
        try:
            Cui.CuiLoadSolution(Cui.gpc_info, self.localplan.get_file_path(),
                                self.get_file_path(), solution, flags)
        except StudioException, exc:
            byp1 = {"TYPE": "NOTICE",
                    "ID": "",
                    "button": "OK"}
            Cui.CuiBypassWrapper("CuiProcessInteraction",
                                 Cui.CuiProcessInteraction,
                                 (byp1, "NOTICE", ""))
            raise exc

    def load_best_solution(self):
        """
        Loads the best solution to the sub-plan
        Best solution is defined by the link best_solution

        The sub-plan is loaded silent without confirmations.
        """
        self.load_solution('best_solution')

    def load_last_solution(self):
        """
        Loads the last solution of a sub-plan.
        The last solution is the solution with the highest
        number.
        """
        solution_nr = 0
        while(os.path.exists(os.path.join(self.get_abs_path(),
                                          'APC_FILES',
                                          "Solution_%s" % str(solution_nr + 1)))):
            solution_nr += 1
        if solution_nr == 0:
            raise ValueError("No solution exists, or bad path to the sub-plan")
        self.load_solution("Solution_%s" % str(solution_nr))

    def load_as_environment(self):
        """
        Loads the specified plan into memory as environment.
        """
        flags = (Cui.CUI_LOAD_SOLUTION_DONT_CONFIRM |
                 Cui.CUI_LOAD_SOLUTION_SILENT |
                 Cui.CUI_LOAD_SOLUTION_FORCE)
        Cui.CuiLoadEnvSubPlan(Cui.gpc_info, self.localplan.get_file_path(),
                              self.get_file_path(), flags)

    def is_current(self):
        """
        Checks whether the sub-plan is in memory.

        @return: True if the sub-plan is in memory
        @rtype: Bool
        """
        try:
            return self == get_current_sub_plan()
        except ValueError:
            return False

    def load_crew(self, file_name):
        """
        Loads a crew plan into the sub-plan

        @param file_name: Name of crew table to load.
                         Can be specified as either path or name.
        @type file_name: string
        @raise ValueError: if the plan is not loaded
        """
        if self.is_current():
            parts = file_name.split(os.sep)
            if len(parts) == 1:
                file_name = file_name
            else:
                file_name = parts[-1]
            Cui.CuiLoadCrewPlan(Cui.gpc_info, file_name, "")
        else:
            raise ValueError("The sub-plan is not loaded, "
                             "and hence can it not be saved!")

    def save(self):
        """
        Saves the SubPlan with same name.

        @raise ValueError: if the plan is not loaded
        """
        self.save_as(self.file_name)

    def save_as(self, file_name, localplan=None):
        """
        Saves the current sub-plan under a new name.

        @param file_name: Name of the new sub-plan
        @type file_name: String
        @param localplan: The local plan under which the sub-plan should be saved
        @type localplan: LocalPlan
        @raise ValueError: if the plan is not loaded
        """
        if not localplan:
            localplan = self.get_local_plan()
        if not self.is_current():
            raise ValueError("The sub-plan is not loaded, "
                             "and hence can it not be saved!")
        self.file_name = file_name

        if not localplan == self.localplan:  # Save plan in a new local plan
            self.localplan = localplan
            flags = (Cui.CUI_MOVE_SP_TO_NEW_LP_DEFAULT |
                     Cui.CUI_MOVE_SP_TO_NEW_LP_SILENT)
            tname = Variable.Variable(self.get_file_path())
            Cui.CuiMoveSubPlan(Cui.gpc_info, tname, 0, 0, flags)
        else:  # Save plan in the same local plan
            if not file_name:
                Cui.CuiSaveSubPlan(Cui.gpc_info, 0, 7)
            else:
                Errlog.log("Saving sp: %s" % file_name)
                tname = Variable.Variable(file_name)
                Cui.CuiSaveSubPlan(Cui.gpc_info, tname, 7)

    def remove(self):
        """
        Removes the current sub-plan
        """
        if self.is_current():
            Cui.CuiUnloadPlans(Cui.gpc_info, 1)

        if os.path.isdir(self.get_abs_path()):
            os.system("rm -rf %s" % self.get_abs_path())

    def exist(self):
        """
        Returns true if sub-plan exist in file tree

        """
        return os.path.isdir(self.get_abs_path())

    def __eq__(self, other):
        """
        Compare two sub-plans
        Plans are considered to be equal if the file path is equal.

        @param other: The relative path of the sub-plan that should be compared
        @type other: SubPlan

        @return: True if SubPlans are equal
        @rtype: Bool
        """
        return (isinstance(other, SubPlan) and
                self.get_file_path() == other.get_file_path())
