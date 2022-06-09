import pwd
import os
import sys

# Assume ther is a custom CTF class
from steps.ctf_custom import CTFCustom

import Cui

def before_all(context):
    context.bug_display = context.config.userdata.getbool("bug_display", False)
    context.display = context.config.userdata.getbool("display", False)
    context.verbose = context.config.userdata.getbool("verbose", False)
    context.verbose_cmds = [] # Prepare for extra messages in the end

def before_feature(context, feature):
    # Used e.g. to load correct rule set, start each feature from scratch
    context.application = ''

def before_scenario(context, scenario):
    context.is_first_when = True

    # Make sure to clean up before the scenario is run
    Cui.CuiUnloadPlans(Cui.gpc_info, Cui.CUI_SILENT)

    # Create scenario specific ctf file for test data
    ctf_path = os.path.expandvars('$CARMDATA/INTX_FILES')
    prefix = 'ctf_%s_' % os.path.basename(scenario.filename).split('.')[0]
    #print('ctf_path: %s' % ctf_path)

    feature_name = scenario.filename.split('/')[-1].split('.')[0]

    # Replace any character not fit for a plan name with '_'
    scenario_name = scenario.name
    for ch in ['\\','`','*','_','{','}','[',']','(',')','>','#','+','-','.',',','!','$','\'',' ']:
        scenario_name = scenario_name.replace(ch, "_")
    user_name = pwd.getpwuid(os.getuid()).pw_name
    context.localplan = '%s/%s/%s' % (user_name, feature_name, scenario_name)
    context.subplan = '%s/%s' % (context.localplan, 'Default')
    context.ctf = CTFCustom(ctf_path, prefix, context.localplan, context.subplan, context.display)


class NullDevice():
    def write(self, s):
        pass

def before_step(context, step):
    # If this is the first 'when' step then load ctf data into Studio
    if step.step_type.lower() == 'when' and context.is_first_when:
        #print 'Step is first when: ', step
        # Suppress some error output about illegal connection string
        old_stdout = sys.stdout
        sys.stdout = NullDevice()
        old_stderr = sys.stderr
        sys.stderr = NullDevice()
        context.ctf.create_and_load_plan(context.application)
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        context.is_first_when = False

def after_step(context, step):
    context.step_duration = step.duration

def after_feature(context, feature):
    pass

def after_all(context):
    """ When running Studio without display, you cannot show e.g. failing reports
    Therefor these commans are saved and gathered here at the end. It is assumed that
    all are tuples on these formats:
    ('<name of failed feature>', 'browser', '<html-file 1>' '<html-file 2>', )
    or
    ('<name of failed feature>', '!browser', '<unix command>')

    The created file will be run by the test_beahave.py script
    """
    if not context.verbose_cmds:
        return
    fd = open(os.path.expandvars('$CARMTMP/behave/verbose.py'), 'w')
    # print(fd.name)

    fd.write('import os\n')
    fd.write('import subprocess\n')
    fd.write('import webbrowser\n')
    fd.write('def run():\n')

    for v_cmd in context.verbose_cmds:
        fd.write('    print "Feature failed: %s\\n"\n' % (v_cmd[0].encode()))
        if v_cmd[1] == 'browser':
            fd.write('    webbrowser.open_new("%s")\n' % v_cmd[2][0])
            fd.write('    webbrowser.open("%s")\n' % v_cmd[2][1])
        else:
            fd.write('    subprocess.popen(%s)\n' % v_cmd[2])

    fd.close()

