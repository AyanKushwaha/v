#!/usr/bin/env python

import argparse
import os
import shutil
import subprocess
import sys

def get_parser_args(args=None):
    usage = \
    """
    This is how you initialize the behave/gherkin tests framework
    """
    parser = argparse.ArgumentParser(usage)
    parser.add_argument(
        '-B', '--nobackup',
        action='store_true',
        help='Do not create any backup files')
    parser.add_argument(
        '--cleanbackup',
        action='store_true',
        help='Clean up current system from backup files')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print more detailed messages')
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify the current system')

    ret = parser.parse_args(args)
    return ret

def clean_backup_files(system_root):
    os.chdir(system_root)
    os.system('find -name "*.behave_bkp" -delete')
    # Some find functions may not have the fast -delete option, then use this:
    #os.system('find -name "*.behave_bkp" -exec rm -rf {} \;')

def get_user_name(args, system_dir):
    os.chdir(system_dir)
    if args.verbose:
        print 'Looking for carmusr name in %s' % system_dir
    config_path =  subprocess.Popen(['find','-maxdepth', '2','-name','CONFIG_extension'], stdout=subprocess.PIPE).communicate()[0]
    if config_path:
        carmusr_name = config_path.split('/')[0]
        if args.verbose:
            print 'Found carmusr as: %s' % carmusr_name
    else:
        carmusr_name = 'carmusr'
        if args.verbose:
            print 'Set carmusr to default: %s' % carmusr_name

    return carmusr_name
    

def verify_behave_import(args):
    try:
        import behave
    except:
        print 'Could not import behave module, make sure it is installed'

    if args.verbose:
        print 'behave module is availalbe and can be imported'

def setup_dirs(args, new_system_root, carmusr_name):
    needed_dirs = ['bin',
                   'carmdata_behave',
                   carmusr_name,
                   '%s/lib' % carmusr_name,
                   '%s/lib/python' % carmusr_name,
                   '%s/lib/python/behave' % carmusr_name,
                   'nose_tests',
                   '%s/lib/python/tests' % carmusr_name,
                   ]
    os.chdir(new_system_root)
    for needed_dir in needed_dirs:
        create_dir(args, needed_dir)



def copy_scripts(args, system_root, new_system_root, new_carmusr_name):
    needed_scripts = ['bin/test_behave.py',
                      'bin/test_clone.py',
                      'bin/test_nose.sh',
                      'bin/test_steps.py',
                      'bin/print_sys_def.example',
                      'nose_tests/test.py']

    os.chdir(new_system_root)
    for needed_script in needed_scripts:
        from_file = os.path.join(system_root, needed_script)
        to_file = os.path.join(new_system_root, needed_script)
        copy_file(args, from_file, to_file)

    # Make sure there is a bin/print_sys_def.py
    needed_print_sys_def = 'bin/print_sys_def.py'

    if os.path.basename(new_system_root) == 'empty_system' \
            or os.path.isfile(needed_print_sys_def) \
            and os.path.getsize(needed_print_sys_def) > 2000:
        # Creatign start-up package, or there already is a large file
        # copy the new version
        from_file = os.path.join(system_root, needed_print_sys_def)
        to_file = os.path.join(new_system_root, needed_print_sys_def)
        copy_file(args, from_file, to_file)
    else:
        # The is no file or it is small, copy the example file
        from_file = os.path.join(system_root, 'bin', 'print_sys_def.example')
        to_file = os.path.join(new_system_root, needed_print_sys_def)
        copy_file(args, from_file, to_file)
        with open(to_file, 'r') as the_file:
            all_lines = the_file.read()

        with open(to_file, 'w') as the_file:
            all_lines = all_lines.replace('<carmsystemroot>', new_system_root)
            all_lines = all_lines.replace('<carmusr>', new_carmusr_name)
            the_file.write(all_lines)
        


def copy_carmdata_behave(args, system_root, new_system_root, carmusr_name):
    carmdata_behave_path = os.path.join(system_root, 'carmdata_behave')
    new_carmdata_behave_path = os.path.join(new_system_root, 'carmdata_behave')
    
    # walk through orig behave data
    # for each orig dir crate a new dir if needed, backup and copy all files
    copy_dirs(args, carmdata_behave_path, new_carmdata_behave_path)
    

def copy_behave(args, system_root, new_system_root, carmusr_name, new_carmusr_name):
    behave_path = os.path.join(system_root, carmusr_name,
                               'lib', 'python', 'behave')
    new_behave_path = os.path.join(new_system_root, new_carmusr_name,
                                   'lib', 'python', 'behave')

    copy_dirs(args, behave_path, new_behave_path)
 
def copy_nose_tests(args, system_root, new_system_root, carmusr_name, new_carmusr_name):
    nose_path = os.path.join(system_root, carmusr_name,
                             'lib', 'python', 'tests')
    new_nose_path = os.path.join(new_system_root, new_carmusr_name,
                                 'lib', 'python', 'tests')

    copy_dirs(args, nose_path, new_nose_path)


def verify_rave(args, new_system_root, new_carmusr_name):
    studio_sno_file = os.path.join(new_system_root, new_carmusr_name, 'crc', 'modules', 'studio_sno')
    variables = {'%num_marked_trips%':False, '%num_marked_legs%':False}
    var_defs = {'%num_marked_trips%':'%num_marked_trips% = count(trip_set) where (%trip_is_marked%);',
                '%num_marked_legs%':'%num_marked_legs% = count(leg_set) where (%leg_is_marked%);'}

    try:
        with open(studio_sno_file) as the_file:
            for line in the_file:
                for var in variables.keys():
                    if line.find(var) > -1:
                        variables[var]=True
                        if args.verbose:
                            print 'Found Rave variable studio_sno.%num_marked_trips%'
    except IOError:
        print """\nCould not find Rave module: studio_sno
module studio_sno
%num_marked_trips% = count(trip_set) where (%trip_is_marked%);
%num_marked_legs% = count(leg_set) where (%leg_is_marked%);
%all_legs_in_trip_marked% = all(leg(trip), %leg_is_marked%);
%leg_is_marked% = marked;
"""
        return

    if not all(variables.values()):
        for var in variables.keys():
            if not variables[var]:
                print 'Could not find Rave variable studio_sno.%s \nPlease add it as:\n   %s' % (var, var_defs[var])

def verify_util_custom(args, new_system_root, new_carmusr_name):
    util_custom_path = os.path.join(new_system_root, new_carmusr_name, 'lib', 'python', 'behave', 'features', 'steps')
    sys.path.append(util_custom_path)
    import util_custom as custom

    # Verify crew_homebase is not GOT ... ie the file has been customized
    if custom.crew_homebase == 'GOT':
        print 'File needs to be customized: behave/features/steps/util_custom.py'

def create_dir(args, needed_dir):
    if os.path.isdir(needed_dir):
        if args.verbose:
            print 'dir already exists: %s' % needed_dir
    else:
        if args.verify:
            print 'dir does not exist: %s' % needed_dir
        else:
            try:
                os.mkdir(needed_dir)
                if args.verbose:
                    print 'dir created: %s' % needed_dir
            except:
                print 'Could not create dir: %s' % needed_dir


def copy_file(args, from_file, to_file):
    bkp_file = to_file +'.behave_bkp'
    if args.verify:
        if not os.path.isfile(to_file):
            print 'file does not exist: %s' % to_file
        return

    if not args.nobackup:
        try:
            shutil.move(to_file, bkp_file)
            if args.verbose:
                print 'file moved to bakup: %s' % to_file
        except IOError as exc:
            if exc.errno in (2,):
                # No such file or directory, ignore
                pass
            else:
                print 'Could not move to bakup: %s' % to_file
                return
    try:
        shutil.copy(from_file, to_file)
        if args.verbose:
            print 'file copied: %s' % to_file
    except IOError as exc:
        raise
    
def copy_dirs(args, from_dirs, to_dirs):
    if args.verify:
        if not os.path.isdir(to_dirs):
            print 'dir does not exist: %s' % to_dirs
        return
    rel_path = ''
    orig_root = ''
    orig_root_len = 0
    os.chdir(to_dirs)

    for dirPath, subdirList, fileList in os.walk(from_dirs):
        if orig_root:
            rel_path = dirPath[orig_root_len+1:]
            os.chdir(to_dirs)

            create_dir(args, rel_path)
            os.chdir(rel_path)
        else:
            orig_root = dirPath
            orig_root_len = len(orig_root)

        for fname in fileList:
            if not (fname.endswith('~') or fname.endswith('.pyc')):
                from_file = os.path.join(orig_root, rel_path, fname)
                to_file = fname
                copy_file(args, from_file, to_file)


if __name__ == "__main__":
    args = get_parser_args()
    #print '# # # # # # # args: ', args

    # Assume in new system root
    new_system_root = os.getcwd()

    # Clean all bakcup files in current system
    if args.cleanbackup:
        clean_backup_files(new_system_root)
        exit()

    # Assume path <system_root>/bin/test_clone.py
    system_root = os.path.join(os.getcwd(), sys.argv[0])[:-17]

    # Find the name of the $CARMUSR directories
    carmusr_name = get_user_name(args, system_root)
    new_carmusr_name = get_user_name(args, new_system_root)

    # Verify that python behave module is available
    verify_behave_import(args)

    # Setup dirs
    setup_dirs(args, new_system_root, new_carmusr_name)

    # Copy scripts
    copy_scripts(args, system_root, new_system_root, new_carmusr_name)

    # Copy carmdata_behave
    copy_carmdata_behave(args, system_root, new_system_root, new_carmusr_name)
    
    # Copy behave dirs (incl tests and step implementations)
    copy_behave(args, system_root, new_system_root, carmusr_name, new_carmusr_name)

    # Copy example nose tests
    copy_nose_tests(args, system_root, new_system_root, carmusr_name, new_carmusr_name)
    
    # Verify rave variables
    verify_rave(args, new_system_root, new_carmusr_name)

    # Verify the util_custom file
    verify_util_custom(args, new_system_root, new_carmusr_name)
