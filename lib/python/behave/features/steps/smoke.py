import time

import Cui
import Gui


@given(u'smoke test')
def verify_studio_display(context):
    """
    Given smoke test
    """
    assert context.display, 'Cannot run smoke tests on virtual display, use -D'

@when(u'I start DWS')
def start_dws(context):
    """
    Given I start DWS
    """
    context.verify_str = 'DWS'
    Cui.CuiStartDevelopersWorkspace()
    time.sleep(5)

@when(u'I start Batch Manager')
def start_batch_manager(context):
    """
    Given I start Batch Manager
    """
    context.verify_str = 'Batch Manager'
    try:
        Cui.CuiStartBatchViewer(Cui.gpc_info)
    except Cui.CancelException as e:
        # Will throw exception when batch deamon not running
        print('Cancel Exception from start Batch Manager (no batch deamon?): %s' % e)
    time.sleep(5)

@then(u'I have to verify manually')
def verify_manually(context):
    """
    Then I have to verify manually
    """
    verify_str = context.verify_str
    gui = verify_str.replace(' ', '_')
    msg = 'Please verify that %s has started and appears on the screen' % verify_str
    ret = Gui.GuiYesNo('BEHAVE_VERIFY_%s' % gui, msg)
    assert ret, 'User could not verify start of %s' % verify_str


@then(u'all\'s well')
def all_is_well(context):
    """
    Then all's well
     Useful when there is no real test at the end
    """
    pass
