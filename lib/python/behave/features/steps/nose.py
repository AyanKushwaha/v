import os
from subprocess import call

@given(u'unittests')
def unitests(context):
    """
    Given unittests
    """
    pass

@then(u'verify nose tests')
def verify_nose_test(context):
    """
    Then verify nose tests
    """
    nose_path = os.path.expandvars('$CARMSYSTEMROOT/bin/test_nose.sh')
    ret = call(nose_path)
    assert not ret, 'Nose tests failed.'

