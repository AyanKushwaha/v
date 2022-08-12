# This is the readme file for the Behave/Gherkin setup
# Please send any comments to Henrik dot Mohr at Jeppesen dot com

Make sure you have the Jeppesen Start-up package installed on
Linux. Either stand alone, or as part of an existing Carmusr.

Run the clone script:
cd new_carmsystem
<path_to_start_up_package_system>/bin/test_clone.py

This will now copy needed files and example tests and verify your
system, e.g.:
- Make sure to have the Python package for Behave installed on Linux
- Install the behave start scripts with execution permissions:
    - this is the main Carmusr framework for automated testing
    - the scripts assume to run in a (fairly) normal
      environment/user 
- Copy default test data (needed for example tests)
- Copy all behave directories with example tests and implementations
- Copy nose test directories with example tests and implementations
- Verify that needed Rave variables are available

Now you should be able to run:
bin/test_behave.py -h

Start by making sure you have compiled rules, if you run on an OTS
Carmusr, you may run:
bin/test_behave.py -c -n

Edit the file carmusr/lib/python/behave/features/util_custom.py
with you favorite values.

Run your first test:
bin/test_behave.py -i ex_leg

Some example tests assume certain available bases, rule set names and
Rave code that may have to be updated to match the current installation.

Feature files demo_1 and demo_2 are based on Pairing (OTS) and may not
run under Rostering. They may be removed.

If you are updating with a new version of the start-up package, there
may be files that have changed names (e.g. rave.py -> rave_util.py)
wich may leave you with multiple step definitions. Move any custom
code from rave.py to rave_util.py and then remove rave.py.

------------

Tips & Tricks:
use: print('string to output') # from Behave code
use: assert False, 'Controlled failure to stop executuion' # when debugging

--steps-catlog
--------------
the command:  bin/test_behave.py --steps-catalog -i notest
will give you a list of all available steps, however, it will be with
regexp notation: Given (?P<a_another>a|another) "(?P<activity>[a-z]*)"

To make it easier to understand, it is possible to write a function comment
to the matching python function with an example of a proper step.
You may also add plain comments by using 5 spaces.
Best practice is also to only match python function to exactly one
step and have them call _common_function():

@given(u'%(a_another)s "%(activity)s"' % util.matching_patterns)
def create_activity(context, activity, a_another='unused'):
    """
    Given a "leg"
     More comments
     These lines begin with 5 spaces
    """
    _create_activity(context, activity=activity)

bin/test_steps.py
----------------
This script will verify that there are examples to all Gherkin match
functions. And that there are features testing all example steps
(e.g. in ex_ files).

use_step_matcher('re')
---------------------
When using re with (), it will always produce a parameter
which is passed as the first argument to the following python function,e.g.
@when(u'I load (rule set|ruleset) "%(rule_set)s"' % util.matching_patterns)
def load_rule_set(context, unused_rule_set, rule_set)

if unhandled you will get errors like:
 TypeError: load_rule_set() got multiple values for keyword argument 'rule_set'

tags:
-----
It is possible to tag features and scenarios to more easily filter
which tests to run, e.g. use @opt for optimzation jobs:

Feature: Optimization Peformance
  @opt
  Scenario: run an opt job and verify performance

Use tags with the start script:
Run bin/test_behave.py --tags opt to only run tests with tag opt

Use @opt @demo to set multiple tags
Run bin/test_behave.py --tags opt,demo to run all with either opt OR
demo tag
Run bin/test_behave.py --tags opt --tags demo to run tests with both
opt AND demo tags set
Run bin/test_behave.py --tags=-opt to run tests without opt tag set

You may e.g. use @prop, @jet, @rocket for slow, medium and fast tests
or @always, @checkin, @nightly

/HM
