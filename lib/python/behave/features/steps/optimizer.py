import os
import Cui
import shutil

from behave import use_step_matcher

use_step_matcher('parse')


@when(u'I fake the pairing optimizer')
def fake_jcp_optimizer(context):
    """
    When I fake the pairing optimizer
      While developing or debugging, we do not want to wait for the actual opt run to finish.
    """
    apc_sp_name = 'optimization'
    context.sp_dir = apc_sp_name
    opt_run_path = os.path.expandvars('$CARMDATA/LOCAL_PLAN/%s/%s/APC_FILES/optrun.xml' % \
                                          (context.lp_dir, context.sp_dir))

    if not os.path.exists(os.path.dirname(opt_run_path)):
        os.makedirs(os.path.dirname(opt_run_path))

    shutil.copy(os.path.expandvars('$CARMDATA/fake_optrun.xml'), opt_run_path)

@when(u'I run the pairing optimizer')
def start_jcp_optimizer(context):
    """
    When I run the pairing optimizer
     Start pairing opt job locally and make Studio wait for it
    """

    Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrrMode,
                          Cui.CuiShowAll)

    apc_sp_name = 'optimization'
    param_map = [("FORM", "START_APC"),
                 ("RESET", ""),
                 ("APC_SP_NAME", apc_sp_name),
                 ("APC_COMMENT", 'Automatic Test'),
                 ("LEG_SRC", "Window 1"),
                 ("RESTART", "No"),
                 ("WHICH_OPTIMIZER", "Crew Pairing Optimizer")]

    param_map.append(("OK", ""))

    Cui.CuiStartOptimizer(param_map, Cui.gpc_info, Cui.CUI_START_OPTIMIZER_LOCAL | Cui.CUI_START_OPTIMIZER_SYNCHRONOUS)


    # Remember opt name for next step
    context.sp_dir = apc_sp_name


@then(u'performance shall be about {target}')
def validate_performance(context, target):
    """
    Then performance shall be about 3:11
     'about' means +-5% (or +-5 seconds for really short runs)
    """
    target, target_min, target_max, data_type = value_to_targets(target.encode())

    actual = get_opt_value(context, data_type)
    actual_in_range = target_min <= actual and actual <= target_max

    assert actual_in_range, 'The Execution time was %s (%s->%s)' % \
        (seconds_to_string(actual), seconds_to_string(target_min), seconds_to_string(target_max))

@then(u'the "{element}" shall be about {value}')
def validate_element_value(context, element, value):
    """
    Then the "TOTAL cost" shall be about 663836
     'about' means +-5%
    """

    # Assume prop name attribute
    # Assume data type int
    element = element.encode()
    target, target_min, target_max, data_type = value_to_targets(value)

    actual = get_opt_value(context, data_type, element)
    actual_in_range = target_min <= actual and actual <= target_max
    
    assert actual_in_range, 'The element %s was %s (%s->%s)' % \
        (element, actual, target_min, target_max)

@then(u'the last solution shall have the following results')
def validate_restults_table(context):
    """
    Then the last solution shall have the following results
    | element     | value   |
    | performance | 0:03:11 |
    | TOTAL cost  | 663836  |
     the values are turned into +-5% intervals
    """

    # Verify that all columns can be handled
    optimization_columns = ('element', 'value')
    for column in context.table.headings:
        assert column in optimization_columns, 'Cannot handle column %s, use: %s' % (column, ", ".join(optimization_columns))
    
    actuals = []
    for row in context.table:
        element = row[context.table.get_column_index('element')].encode()
        value = row[context.table.get_column_index('value')].encode()

        target, target_min, target_max, data_type = value_to_targets(value)

        _element =  element == 'performance' and 'Elapsed' or element
        actual = get_opt_value(context, data_type, _element)
        
        actual_in_range = target_min <= actual and actual <= target_max
        if not actual_in_range:
            if data_type == 'reltime':
                actual = seconds_to_string(actual)
                target_min = seconds_to_string(target_min)
                target_max = seconds_to_string(target_max)
            actuals.append((element, actual, target_min, target_max))

    if actuals:
        assert_msg = 'Errors from result table:'
        for err in actuals:
            assert_msg += '\n  The element %s was %s (%s->%s)' % err
        assert False, assert_msg




def get_opt_value(context, data_type, element='Elapsed'):
    """
    assume lines like:
    <prop name="Elapsed time" type="Reltime">0:00:01<prop name="Execution time" type="Reltime">0:00:01</prop>
    or
    <prop name="TOTAL cost" type="Int">608046<prop name=" APC total rule cost" type="Int">608046
    """
    target_lines = find_lines_in_optrun(context, element)
    actuals = []
    for line in target_lines:
        for prop in line.split('<'):
            if prop.find(element) > -1:
                # prop = 'prop name="TOTAL cost" type="Int">608046'
                if data_type == 'int':
                    actual_int = int(prop.split('>')[-1])
                    actuals.append(actual_int)
                elif data_type == 'reltime':
                    actual_reltime = line.split('>')[-2].split('<')[0]
                    actual_reltime = value_to_targets(actual_reltime)[0]
                    actuals.append(actual_reltime)
                else:
                    assert False, 'Cannot handle data_type %s, use int or reltime' % data_type
                
    actual = actuals[-1] # Assume last solution from sorted file is 'best'
    return actual


    ix = 0
    for line in target_lines:
        ix += 1

    actual = max(actuals.values())
    



def find_lines_in_optrun(context, target_element):
    ret = []

    opt_run_path = os.path.expandvars('$CARMDATA/LOCAL_PLAN/%s/%s/APC_FILES/optrun.xml' % \
                                          (context.lp_dir, context.sp_dir))
    
    with open(opt_run_path, 'r') as opt_run:
        for line in opt_run:
            if line.find(target_element)>-1:
                # Each solution will have one entry each for target_element
                ret.append(line)
    if ret:
        return  ret
    else:
        assert False, 'Could not find %s in optrun.xml file:\n  %s' % (target_element, opt_run_path)

def value_to_targets(value):
    # '0:00:16' -> 16, 11, 21, ie +/- 5% (or +/-5seconds)
    # '663804' -> 663804, 630613, 696994, ie +/- 5% (or +/-5units)
    minutes = 0
    hours = 0
    data_type = 'int'

    # The value could be a reltime, ints are treated as seconds
    value_split = value.split(':')
    seconds = int(value_split[-1])
    if len(value_split) > 1:
        data_type = 'reltime'
        minutes = int(value_split[-2])
        if len(value_split) > 2:
            hours = int(value_split[-3])

    ret = 3600*hours + 60*minutes + seconds
    ret_min = min(int(ret*0.95), ret-5)
    ret_max = max(int(ret*1.05), ret+5)
    
    return (ret, ret_min, ret_max, data_type)

def seconds_to_string(time):
    # 16 > '0:00:16'
    hours = time / 3600
    minutes = (time % 3600) / 60
    seconds = (time % 60)

    if hours:
        ret = '%d:%02d:%02d' % (hours, minutes, seconds)
    else:
        ret = '%02d:%02d' % (minutes, seconds)
    return ret
