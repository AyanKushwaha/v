from behave import *


@then(u'the step duration shall be "{about}" {target}s')
def validate_step_duration(context, about, target):
    """
    Then the step duration shall be "about30" 0.6s
    """
    about = about.encode().lower()
    if about in ('about', 'about5'):
        about_value = 5
    else:
        about_value = int(about[5:])

    target_min, target_max = value_to_targets(target.encode(), about_value)
    actual = float(context.step_duration)
    actual_in_range = target_min <= actual and actual <= target_max

    assert actual_in_range, 'The step duration was %s (%s->%s)' % \
        (actual, target_min, target_max)

def value_to_targets(value, about_value):
    """
    '0.6' -> 0.56999, 0.63, ie +/- 5%
    """
    value = float(value)
    min_value = (1.00-about_value/100.0) * value
    max_value = (1.00+about_value/100.0) * value
    return min_value, max_value
