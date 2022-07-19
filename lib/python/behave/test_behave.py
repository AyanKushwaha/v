#!/usr/bin/env python

import argparse
import copy
import datetime
import glob
import os
import sys
import shutil
import subprocess

from operator import itemgetter
from tempfile import mkdtemp

# print_sys_def is created by the test_clone.py script if not already present in user
# otherwise, see the print_sys_def.example script for inspiartion
import print_sys_def

def get_parser_args(args=None):
    usage = \
    """
    This is how you start the behave tests
    """
    parser = argparse.ArgumentParser(usage)
    parser.add_argument(
        '-c', '--compile',
        action='store_true',
        help='Compile all rulesets before running tests')
    parser.add_argument(
        '-e', '--etabs',
        action='store_true',
        help='Refresh etables from db before running tests')
    parser.add_argument(
       '--data',
        action='store_true',
        help='Start studio with CARMDATA set to carmdata_behave')
    parser.add_argument(
       '--dry-run',
        action='store_true',
        help='Do everything but actually run the tests')
    parser.add_argument(
        '-i', '--include',
        help='Only include these tests: leg or "leg|core"')
    parser.add_argument(
        '-n', '--notests',
        action='store_true',
        help='Do not run any tests (nor start Studio)')
    parser.add_argument(
        '-S', '--display',
        action='store_true',
        help='Display Studio and run test(s)')
    parser.add_argument(
        '--sandboxsuffix',
        help='Use this as suffix for the sandbox dir name (used by UGE)')
    parser.add_argument(
        '-s', '--showuge',
        help='Show UGE summary: uge_root or last')
    parser.add_argument(
        '--steps-catalog',
        action='store_true',
        help='Show a catalog of all available step definitions')
    parser.add_argument(
        '--tags',
        action='append',
        help="""Only run tests with TAG ............................
        OR: --tags TAG,TAG2 .................................
        AND: --tags TAG --tags TAG2 ..........................
        To exclude a tag: --tags -TAG .......................
        Tests marked with @skip are excluded by default ....
        To run tests marked @skip: --tags skip""")
    parser.add_argument(
        '-u', '--uge',
        type=int,
        help='Run tests in parallel using UGE: #jobs')
    parser.add_argument(
        '--ugesummary',
        help='Create UGE summary: uge_root (used by UGE)')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print more detailed messages')
    parser.add_argument(
        '--junit',
        action='store_true',
        help='Save test results in Junit format')
    ret = parser.parse_args(args)

    return ret


def log(args, message):
    if args and args.verbose:
        print 'LOG: ', message
    return


def create_carm_env(args=None, sandboxsuffix=None, getenv=None, carmdata_behave=False):
    # TODO: Consider r/W access rights when testing somebody elses system
    global system_root
    os.chdir(system_root)

    ret = ''
    # Set the CARMUSR, CARMSYS, CARMDATA, CARMTMP and CARMSYSTEMROOT variables
    cmds = print_sys_def.main(args=['--python', '--test'])

    if getenv:
        # if getenv is set, then only return the would-be-value for that env variable
        for cmd in cmds:
            if cmd.find(getenv) > -1:
                ret = cmd.split('=')[-1][1:-1]
                return ret
        print 'ERROR: Could not find %s in environment' % getenv
        return ret
    else:
        # Set all the env variables
        for cmd in cmds:
            exec(cmd)

    # Create a unique sandbox environment for this set of tests
    carmtmp = os.path.expandvars('$CARMTMP')
    if not os.path.exists(carmtmp):
        # carmtmp_behave is not under hg control, may need to be created first time
        log(args, 'Creating carmtmp_behave dir')
        os.makedirs(carmtmp)
    os.chdir(carmtmp)

    new_sandbox = create_new_sandbox(sandboxsuffix=sandboxsuffix)
    if sandboxsuffix == 'uge':
        # Only create the uge root to place the other roots in
        ret = os.path.basename(new_sandbox)
    else:
        if not carmdata_behave:
            # Set up carmdata structure, link to data
            os.chdir(new_sandbox)
            create_sandbox_carmdata()
            os.environ['CARMDATA'] = '/%s/carmdata' % new_sandbox

        # Set up unique carmtmp structure, copy ruleset
        os.chdir(new_sandbox)
        create_sandbox_carmtmp()
        os.environ['CARMTMP'] = '/%s/carmtmp' % new_sandbox

    # Create log dir for Behave
    os.environ['LOGDIR'] = '%s/behave' % new_sandbox
    os.makedirs(os.path.expandvars('$LOGDIR'))

    if args.tags and "planning" in args.tags:
        os.environ['SK_APP'] = 'Planning'
        os.environ['CARM_PROCESS_NAME'] = 'PlanningStudio'
        log(args, "Running Planning Studio")
    else:
        os.environ['SK_APP'] = 'Tracking'
        os.environ['CARM_PROCESS_NAME'] = 'TrackingStudio'
        log(args, "Running Tracking Studio")

    return ret


def create_new_sandbox(sandboxsuffix=None):
    # Create SANDBOX (sb)
    if sandboxsuffix:
        if sandboxsuffix.find('/') > -1:
            # suffix is already uge path
            _new_sandbox = sandboxsuffix
        else:
            # Make sure all new SANBOXes are named uniquely
            _new_sandbox = 'BEHAVE_SANDBOX_%s_%s' % (os.environ['USER'], sandboxsuffix)
            if sandboxsuffix == 'uge':
                # Create a unique root dir for this set of uge jobs
                _new_sandbox += '_%s' % \
                    datetime.datetime.strftime(datetime.datetime.now(), '%H%M%S')

    else:
        _new_sandbox = 'BEHAVE_SANDBOX_%s' % os.environ['USER']

    # Create the new sandbox
    cwd = os.getcwd() #TODO: Verify for all cases
    prefix = '%s_' % _new_sandbox
    new_sandbox = mkdtemp(prefix=prefix, dir=cwd)
    #print 'new_sandbox: ', new_sandbox

    return new_sandbox


def create_sandbox_carmdata():
    # Create SANDBOX Carmdata
    os.mkdir('carmdata')
    os.chdir('carmdata')
    carmdata_root = os.getcwd()

    # walk through orig behave data
    # for each orig dir crate a sandbox dir, copy all files
    rel_path = ''
    orig_root = ''
    orig_root_len = 0

    for dirPath, subdirList, fileList in os.walk(os.path.expandvars('$CARMDATA')):
        if orig_root:
            rel_path = dirPath[orig_root_len+1:]
            os.chdir(carmdata_root)

            os.makedirs(rel_path)
            os.chdir(rel_path)
        else:
            orig_root = dirPath
            orig_root_len = len(orig_root)

        # This only works when there are only directories in CARMDATA root:
        for fname in fileList:
            shutil.copy(os.path.join(orig_root, rel_path, fname), fname)

    carmtmp = create_carm_env(getenv='CARMTMP')
    carmtmp_etables = os.path.join(carmtmp, 'ETABLES')
    carmdata_etables = os.path.join(carmdata_root, 'ETABLES')
    src_files = os.listdir(carmtmp_etables)
    for file_name in src_files:
        full_file_name = os.path.join(carmtmp_etables, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, carmdata_etables)

    return


def create_sandbox_carmtmp():
    # Create SANDBOX Carmtmp
    new_rules = 'carmtmp/crc/'
    os.makedirs(new_rules)
    os.chdir(new_rules)

    # Copy all compiled rule sets
    orig_carmtmp = os.path.expandvars('$CARMSYSTEMROOT/carmtmp')
    shutil.copytree('%s/crc/rule_set' % orig_carmtmp, 'rule_set')

    return


def clean_sandbox(args):
    # Clean up the users own, older sandbox directories (keeping last 3)
    carmtmp = create_carm_env(getenv='CARMTMP')
    last_sandbox_behave, _ = get_summary_file_name('last')

    if not last_sandbox_behave:
        last_sandbox = 'no_last_sandbox'
    else:
        last_sandbox = last_sandbox_behave.split('/')[0]

    cwd = os.getcwd()
    try:
        os.chdir(carmtmp)
    except OSError as exc:
        if exc.errno in (2,):
            # Directory does not exist
            log(args, '%s:\n  %s' % (exc.strerror, carmtmp))
            return
        else:
            raise

    dir_data = {}
    for _dir in glob.iglob('BEHAVE_SANDBOX_%s_*' % os.environ['USER']):
        token_file = os.path.join(carmtmp,_dir,'.uge_is_running')
        if _dir != last_sandbox and not os.path.isfile(token_file):
            dir_data[_dir] = os.stat(_dir).st_mtime

    sorted_dirs = sorted(dir_data.items(), key=itemgetter(1))

    # Keep last X dirs
    # keep_dirs = 3
    keep_dirs = 0
    for ix in xrange(len(sorted_dirs)-keep_dirs):
        _dir = sorted_dirs[ix][0]
        log(args, 'Removing %s ...' % _dir)
        old_sandbox = os.path.join(carmtmp,_dir)
        try:
            shutil.rmtree(old_sandbox)
        except OSError as exc:
            if exc.errno in (2, 16, 39):
                log(args, exc.strerror)
                _remove = '_REMOVE'
                if old_sandbox.find(_remove) == -1:
                    old_rm_sandbox = old_sandbox + _remove
                    log(args, 'move %s to %s' % (old_sandbox, old_rm_sandbox))
                    shutil.move(old_sandbox, old_rm_sandbox)
            else:
                raise

    os.chdir(cwd)

def start_studio(args):
    log(args, 'Start Studio args: %s' % args)

    # Used to run Studio on original carmdata_behave data
    carmdata_behave = args.data

    # Set up envrionment and create Sandbox
    log(args, 'Creating sandbox environment')
    create_carm_env(args=args, sandboxsuffix=args.sandboxsuffix, carmdata_behave=carmdata_behave)

    cmd_list = [os.path.expandvars('$CARMSYS/bin/studio')]
    behave_str = '-pPythonRunFile("%s/lib/python/behave/behave.py"' % os.environ['CARMUSR']

    if args.display or carmdata_behave:
        behave_str += ',"--display"'
    else:
        cmd_list.append('-d')

    if args.dry_run:
        behave_str += ',"--dry-run"'

    if args.include:
        behave_str += ',"--include","%s"' % args.include

    if args.tags:
        for tag in args.tags:
            behave_str += ',"--tags=%s"' % tag
    # Don't run tests with "skip" tag, unless "skip" tag is specifically set
    if not args.tags or not "skip" in args.tags:
        behave_str += ',"--tags=-skip"'

    if args.steps_catalog:
        behave_str += ',"--steps-catalog"'
    if args.verbose:
        behave_str += ',"--verbose"'
    
    if args.junit:
        behave_str += ',"--junit"'
        behave_str += ',"--junit-directory=%s"' %  os.path.expandvars('$LOGDIR')
       
    # Set up a copy of stdout (the terminal) for the script behave.py to use
    terminal = os.dup(1)
    behave_str += ',"--stdout","%d")' % terminal
    cmd_list.append(behave_str)

    log(args, 'Start Studio cmd list: %s' % cmd_list)

    new_stdout = os.path.expandvars('$LOGDIR/studio.out')
    new_stderr = os.path.expandvars('$LOGDIR/studio.err')
    fdout = open(new_stdout, 'w')
    fderr = open(new_stderr, 'w')
    log(args, 'Starting Studio ...')
    new_env = dict(os.environ)
    subprocess.call(cmd_list,
                    stdout=fdout,
                    stderr=fderr,
                    env=new_env)


def get_all_feature_file_paths(features_path):
        all_feature_files = []
        for root, _subdirs, files in os.walk(features_path):
            all_feature_files.extend([name for name in files if name.endswith('.feature')])
        return all_feature_files

def start_studio_uge(args):
    log(args, 'Start Studio UGE args: %s' % args)
    print "in start_studio_uge"
    uge_root = create_carm_env(args=args, sandboxsuffix='uge')
    if args.include:
        filter_include_list = args.include.split('|')
    else:
        filter_include_list = []

    # Get a list of all tests
    features_path = os.path.expandvars('$CARMUSR/lib/python/behave/features')
    all_features = get_all_feature_file_paths(features_path)
    #print "all features", all_features
    #print "include features", filter_include_list

    log(args, 'Warning :: Not implemented : Cannot handle tags when running uge jobs')

    # Divide all features into 'uge' number of UGE jobs
    number_of_slots = int(args.uge)
    ix = 0
    features = {}
    job_names = ''
    for f in all_features:
        # Make sure it is a proper feature
        if f.endswith('.feature') \
                and (not filter_include_list \
                         or any(filter_include in f for filter_include in filter_include_list)):
            ix += 1
            try:
                features[ix % number_of_slots].append(f[:-8])
                #print "feature %d - %s"  % (ix, features[ix])
            except: # some error, assume list did not exist, so create it with the first element
                features[ix % number_of_slots] = f[:-8]
                #print "feature %d - %s"  % (ix, features[ix % number_of_slots])
            if len(features) == number_of_slots:
                include = '--include "'
                include += '|'.join(features.values())
                include += '"'
                sandboxsuffix = '--sandboxsuffix %s/uge_%s' % (uge_root, ix)
                job_name = 'behave_%s_%s_%s' % (os.environ['USER'],uge_root.split('_')[-1], ix)
                job_names += job_name+','
                junit_str = ""
                if args.junit:
                    junit_str += '--junit'
                verbose_str = ""
                if args.verbose:
                    verbose_str += '-v'
                cmd = 'qsub -N %s -l batch,osversion=RHEL7 -cwd -b y -o $LOGDIR/qsub_behave_%s.out -e $LOGDIR/qsub_behave_%s.err $CARMSYSTEMROOT/lib/python/behave/test_behave.py %s %s %s %s' % \
                    (job_name, ix, ix, sandboxsuffix, include, junit_str,verbose_str)
                #print cmd
                log(args, cmd)
                features.clear()
                # TODO: change to Popen()
                os.system(cmd)


    # Wait for jobs to finish then show result
    job_summary_name = 'behave_%s_%s_summary' % (os.environ['USER'],uge_root.split('_')[-1])
    cmd = 'qsub -hold_jid %s -N %s -l batch,osversion=RHEL7 -cwd -b y -j y -o $LOGDIR/qsub_behave_summary.out -sync y $CARMSYSTEMROOT/lib/python/behave/test_behave.py --ugesummary %s' % \
        (job_names[:-1], job_summary_name, uge_root)
    #print cmd
    log(args, 'Start Studio UGE summary job: %s' % cmd)
    # newpid = os.fork()
    # if newpid == 0:
    child_wait_for_uge(cmd, uge_root)

def child_wait_for_uge(cmd, uge_root):

    # Prepare the summary file
    _, uge_summary_path = get_summary_file_name(uge_root)
    if not uge_summary_path:
        return
    print "*"
    print uge_summary_path
    print "*"
    uge_summary = open(uge_summary_path, 'w')
    uge_summary.write('This file: %s\n\n' % uge_summary.name)
    uge_summary.close()

    # Create a token file to keep track of still running uge jobs
    token_file = os.path.join(os.path.dirname(uge_summary_path), '..', '.uge_is_running')
    open(token_file, 'a').close()

    # start the UGE job to wait for then collect all job outputs
    # -sync y will halt this child process until uge returns
    #print 'In child process::cmd:', cmd
    os.system(cmd)

    show_uge_summary(uge_root)
    # Remove token file
    os.remove(token_file)

    # Make sure the child process stops ececuting here
    #os._exit(0)

def show_uge_summary(uge_root):
    _, uge_summary_path = get_summary_file_name(uge_root)
    if uge_summary_path:
        #cmd = 'xterm -title "Summary of UGE jobs %s" -geometry 180x24 -bg black -fg green -e less %s &' % \
        cmd = 'pygmentize -g %s &' % \
            (uge_summary_path)
        #print cmd
        os.system(cmd)
    else:
        print 'Error::Cannot find any uge directories'

def get_summary_file_name(uge_root):
    carmtmp = create_carm_env(getenv='CARMTMP')
    if uge_root == 'last':
        sandbox_list = glob.iglob('%s/BEHAVE_SANDBOX_%s_uge_*' % \
                                      (carmtmp, os.environ['USER']))
        try:
            _uge_root = max(sandbox_list, key=os.path.getctime)
        except ValueError:
            # There are no uge directories
            return '', ''
    elif uge_root.find('/') == -1:
        _uge_root = os.path.join(carmtmp, uge_root)
    else:
        _uge_root = uge_root

    behave_root = os.path.join(_uge_root, 'behave')
    uge_summary_path = os.path.join(behave_root, 'uge_summary')

    return behave_root, uge_summary_path

def compile_uge_summary(uge_root):
    # Collect results from uge runs
    behave_root, uge_summary_path = get_summary_file_name(uge_root)
    if not behave_root:
        return

    uge_summary = open(uge_summary_path, 'a')
    has_error = False
    for qfile in sorted(os.listdir(behave_root)):
        #print qfile
        if qfile != 'uge_summary':
            qfile_path = os.path.join(behave_root, qfile)
            if qfile.endswith('err') and os.path.getsize(qfile_path) > 0:
                has_error = True
            uge_summary.write(' > > > File: %s\n\n' % qfile)
            shutil.copyfileobj(open(qfile_path, 'r'), uge_summary)

    if has_error:
        uge_summary.write('\n# ERROR # : There were errors sending UGE jobs!\n')

    uge_summary.write(' # # #     All jobs have finished!   # # # \n\n')
    uge_summary.write(' # # #     Close this window with Q  # # # \n\n')
    uge_summary.close()


def compile_rules():
    # Try to use OTS compile script
    ret = compile_rules_ots()
    if ret:
        # Else use built in function
        ret = compile_rules_behave()

    if not ret:
        download_etabs()

    return ret

def compile_rules_ots():
    # Assumes OTS scripts
    ret = None
    cmd = 'bin/compile_all.py'
    ret = os.system(cmd)
    return ret

def compile_rules_behave():

    orig_os_environ = copy.deepcopy(os.environ)

    # Set the CARMUSR, CARMSYS, CARMDATA, CARMTMP and CARMSYSTEMROOT variables
    # use the original values, not behave test ones (yet)
    cmds = print_sys_def.main(args=['--python'])
    # Set all the env variables
    for cmd in cmds:
        exec(cmd)

    custom_path = os.path.expandvars('$CARMUSR/lib/python/behave/features/steps')
    compile_path = '$CARMSYS/bin/crc_compile'
    rule_set_path = '$CARMUSR/crc/source/'
    sys.path.append(custom_path)
    import util_custom as custom

    rule_sets = [custom.rule_set_tracking]

    for rule_set in rule_sets:
        print 'Compiling: %s' % rule_set
        params = get_compile_params(rule_set)
        ret = os.system(compile_path + params + ' -enable group_redefine -optimize gpc -optimize -explorer %s%s' % (rule_set_path, rule_set))
        if ret:
            return ret

    # make sure to unset CARM vars so that print_sys_def will work later
    os.environ = orig_os_environ
    print 'Compiling done'
    return


def get_compile_params(rule_set):
    if 'pairing' in rule_set:
        return ' apc'
    elif 'rostering' in rule_set:
        return ' matador'
    else:
        return ''


def download_etabs():
    carmtmp = create_carm_env(getenv='CARMTMP')
    carmtmp_etables = os.path.join(carmtmp, 'ETABLES')

    if os.path.exists(carmtmp_etables):
        shutil.rmtree(carmtmp_etables)
    os.makedirs(carmtmp_etables)
    os.chdir(carmtmp_etables)

    etabs = ['ac_qual_map',
             'activity_category',
             'activity_group',
             'activity_group_period',
             'activity_link_set',
             'activity_set',
             'activity_set_period',
             'activity_status_set',
             'agmt_group_set',
             'agreement_validity',
             'aircraft_type',
             'airport',
             'apt_requirements',
             'apt_restrictions',
             'apt_restrictions_course',
             'assignment_attr_set',
             'bases',
             'cabin_training',
             'ci_exception',
             'cnx_time_training',
             'country_req_docs',
             'course_ac_qual_set',
             'crew_base_set',
             'crew_complement',
             'crew_contract_set',
             'crew_document_set',
             'crew_need_jarops_period',
             'crew_need_service',
             'crew_qualification_set',
             'crew_rank_set',
             'crew_recurrent_set',
             'crew_restriction_set',
             'exchange_rate',
             'hotel_contract',
             'hotel_transport',
             'lh_apt_exceptions',
             'lifus_airport',
             'meal_customer',
             'minimum_connect',
             'per_diem_compensation',
             'per_diem_tax',
             'preferred_hotel',
             'preferred_hotel_exc',
             'property',
             'property_set',
             'publication_type_set',
             'rave_string_paramset',
             'salary_region',
             'simulator_set']
    ret = os.system('$CARMUSR/bin/testing/dump_etabs.sh %s' % ' '.join(etabs))
    if ret:
        return ret
    ret = os.system('cp $CARMUSR/current_carmdata/ETABLES/crew_training_log_codes.etab .')
    if ret:
        return ret
    return


def show_verbose_info():
    """ Show extra verbose information
    This file may be created by test steps to show more information,
    e.g. for debug purposes like showing multiple HTML reports
    The file will be imported and the run() function will be run.
    """

    carmtmp = create_carm_env(getenv='CARMTMP')
    if carmtmp.find('SANDBOX') > -1:
        verbose_path = os.path.join(carmtmp, 'behave')
    else:
        verbose_path = os.path.join(carmtmp,
                                    'BEHAVE_SANDBOX_%s' % os.environ['USER'],
                                    'carmtmp',
                                    'behave')
    verbose_file = os.path.join(verbose_path, 'verbose.py')

    if os.path.isfile(verbose_file):
        sys.path.append(verbose_path)
        import verbose
        verbose.run()
    else:
        print 'No verbose file to show: ', verbose_file


if __name__ == "__main__":

    # Assume path <system_root>/lib/python/behave/test_behave.py
    system_root = os.path.join(os.getcwd(), sys.argv[0])[:-33]

    args = get_parser_args()
    log(args, '# # # Test Behave args: %s' % args)

    log(args, 'Cleaning old sandbox environments')
    clean_sandbox(args)

    if args.showuge:
        log(args, 'Showing uge summary job: %s' % args.showuge)
        # Show uge summary job, specified or last
        show_uge_summary(args.showuge)
        sys.exit(0)

    if args.ugesummary:
        log(args, 'INTERNAL (compile uge summary)')
        # Should only be called from uge summary job assuming xterm is already displayed
        compile_uge_summary(args.ugesummary)
        sys.exit(0)

    if args.compile:
        log(args, 'Compiling rule sets')
        ret = compile_rules()
        if ret:
            print 'Error when compiling rules: ', ret
            sys.exit(1)
    if args.etabs:
        log(args, 'Dumping etables from db')
        ret = download_etabs()
        if ret:
            print 'Error when compiling rules: ', ret
            sys.exit(1)
    if args.uge:
        log(args, 'Starting UGE jobs')
        start_studio_uge(args)
    elif not args.notests:
        log(args, 'Calling start Studio script')
        start_studio(args)

    if args.verbose:
        log(args, 'Showing verbose information')
        show_verbose_info()
    

    sys.exit(0)


# End of file
