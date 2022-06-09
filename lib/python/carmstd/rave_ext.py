'''
Extensions to the :carmsys_rave:'carmensystems.rave.api' library

:date: Feb 18, 2010
:organization: Jeppesen Systems AB
'''

import types

import Cui
from carmensystems.studio.reports.CuiContextLocator import CuiContextLocator
import carmensystems.rave.api as rave
import Localization as L


def eval_(bag, identifier):
    '''
    A "baggy" version of :carmsys_rave:'carmensystems.rave.api.eval'

    'rave_ext.eval_(bag, id)' is almost exactly the same as calling
    'getattr(bag, id)', except it expands dotted identifiers.

    It is very useful in those (arguably rare) cases where we
    only have access to the name of the rave
    variable / iterator / function at run-time.

    Examples
    --------

    .. python::

      # Note that bag.trip.start_hb is a callable, so we need the
      # extra parentheses to obtain the value.
      lp_name = rave_ext.eval_(bag, 'global_lp_name')()

      # A more interesting example.
      trip_iterator = rave_ext.eval_(bag, 'iterators.trip_set')()
      for trip_bag in trip_iterator:
          trip_start = trip_bag.trip.start_hb()

      # Obtaining the value from (dynamically named) functions
      # is arguably the most useful. It is used in the rave
      # testing framework.
      def get_rave_function_value(bag, func_id, *args):
          func = rave_ext.eval_(bag, func_id)
          return func(*args)

    :param bag: The bag to perform evaluations over
    :param identifier: An identifier in dotted format (without %)
    '''
    ret = bag
    for component in identifier.split('.'):
        ret = getattr(ret, component)
    return ret


def get_leg_identifiers(bag, where="TRUE", sort_by="TRUE"):
    """
    Returns the list of leg identifiers in a bag.

    For explanation of the parameters 'where' and 'sort_by', see
    :carmsys_rave:'carmensystems.rave.api.iter'

    :return: list of leg identifiers (leg_identifier)
    """
    leg_list = []
    for leg in bag.iterators.leg_set(where=where, sort_by=sort_by):
        leg_list.append(leg.leg_identifier())
    return leg_list


def get_trip_identifiers(bag, where="TRUE", sort_by="TRUE"):
    """
    Returns the list of trip identifiers in a bag.

    For explanation of the parameters 'where' and 'sort_by', see
    :carmsys_rave:'carmensystems.rave.api.iter'

    :return: list of trip identifiers (crr_identifier)
    """
    trip_list = []
    for trip in bag.iterators.trip_set(where=where, sort_by=sort_by):
        trip_list.append(trip.crr_identifier())
    return trip_list


def split_identifier(rave_identifier):
    '''
    Splits a rave identifier into a '(<module>, <name>)' pair.
    If the rave_identifier is not dotted, the returned value
    of <module> is '_topmodule'.

    The function does not check whether the identifier
    is syntactically valid or exists.


    Examples
    --------

    .. python::

      >>> split_identifier('trip_rules_exp.max_duty_time')
      ('trip_rules_exp', 'max_duty_time')
      >>> split_identifier('%map_rudob_len_97_crr%')
      ('_topmodule', '%map_rudob_len_97_crr%')

    :param rave_identifier: A rave identifier
    :type rave_identifier: str
    '''
    split_name = rave_identifier.split('.', 1)
    if len(split_name) == 1:
        module = '_topmodule'
        name = split_name[0]
    else:
        module, name = split_name

    return module, name


def explore_roster(computable, area, crew_id):

    CuiContextLocator(area,
                      'object',
                      Cui.CrewMode,
                      crew_id).reinstate()
    _explore(computable)


def explore_leg(computable, area, leg_identifier):
    '''
    Starts rave explorer for the computable on the object
    given by 'area' and 'leg_identifier'.

    The computable can either be a string, in which case
    it is assumed to be a rave expression, or any of the
    types

    - :carmsys_rave:'carmensystems.rave.api.Rule'
    - :carmsys_rave:'carmensystems.rave.api.Variable'
    - :carmsys_rave:'carmensystems.rave.api.Keyword'

    :param computable: The computable to explore
    :param area: The area where the object exists
    :param leg_identifier: The leg identifier to explore
    '''

    # Setup context for Rave Explorer
    CuiContextLocator(area,
                      'object',
                      Cui.LegMode,
                      str(leg_identifier)).reinstate()

    _explore(computable)


def _explore(computable):
    '''
    Starts rave explorer on the computable, using default_context.

    :param computable: See 'explore_leg'
    '''
    if isinstance(computable, rave.Rule):
        explore_type = L.MSGR('Rule')
        name_field = 'RULE_NAME'
        module, name = split_identifier(computable.name())
    elif isinstance(computable, rave.Variable):
        explore_type = L.MSGR('Variable')
        name_field = 'VARIABLE_NAME'
        module, name = split_identifier(computable.name())
        name = name.strip('%')  # The form cannot handle the percentage signs
    elif isinstance(computable, rave.Keyword):
        explore_type = L.MSGR('Keyword')
        name_field = 'KEYWORD'
        module, name = split_identifier(computable.name())
    elif isinstance(computable, types.StringTypes):
        explore_type = L.MSGR('Expression')
        name_field = 'EXPRESSION'
        module = '_topmodule'
        name = computable
    else:
        raise TypeError('Invalid type: %s' % type(computable))

    # Order here matters because the module determines which
    # rules and variables are available.
    byp = [('FORM', 'RaveExplorer'),
           ('EXPLORE_TYPE', explore_type),
           ('ONE_ALL', L.MSGR('Current')),
           ('VARIABLE_MODULE', module),
           (name_field, name)]

    Cui.CuiStartRaveExplorer(byp, Cui.gpc_info, 0)
