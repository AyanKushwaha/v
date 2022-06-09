import argparse
import os
from pkg_resources import load_entry_point
import sys

def get_parser_args(args=None):
    usage = \
    """
    This is how you use behave.py
    """
    parser = argparse.ArgumentParser(usage)
    parser.add_argument(
        '-i', '--include',
        help='only include these tests')
    parser.add_argument(
        '-D', '--display',
        action="store_true",
        help='Display Stduio and run test(s)')
    parser.add_argument(
       '--dry-run',
        action='store_true',
        help='Do everything but actually run the tests')
    parser.add_argument(
        '--stdout',
        help='set fileno for redirect of stdout')
    parser.add_argument(
        '--steps-catalog',
        action="store_true",
        help='Show a catalog of all available step definitions')
    parser.add_argument(
        '--tags',
        action='append',
        help='Run only tests with this tag (exclude tests with -)')
    parser.add_argument(
        '-v', '--verbose',
        action="store_true",
        help='print more detailed error messages')
    parser.add_argument(
        '--junit',
        action='store_true',
        help='Save reports in JUnit format')
    parser.add_argument(
        '--junit-directory',
        action='append',
        help='JUnit reports directory')
    parser.add_argument(
        '--outfile',
        action='append',
        help='Write to specified file instead of stdout')

    ret = parser.parse_args(args)

    return ret

def rebind_std_streams(args):
    # Remember Python out/err
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    # Set Python out/err to the terminal stream opened in test_behave.py, or hope 6 is free (steal it)
    terminal = int(args.stdout) or 6

    file_descriptor_terminal = os.fdopen(terminal, "w")
    sys.stdout = file_descriptor_terminal
    sys.stderr = file_descriptor_terminal

    # Return the old values
    return (old_stdout, old_stderr)

def restore_std_streams(old_stdout, old_stderr):
    # Restore Python out/err
    sys.stdout = old_stdout
    sys.stderr = old_stderr

def collect_tests_run_and_exit_studio(args):
    print '\n # # # # Entering the world of Behave # # # #\n'
    #print args
    arg_list = []

    # Where to find tests/features
    if args.junit:
        features_path = os.path.expandvars('../../../../../../$CARMUSR/lib/python/behave/features')
    else:
        features_path = os.path.expandvars('$CARMUSR/lib/python/behave/features')
    
     
    print '# # feature path: ', features_path
    arg_list.append(features_path)

    # Only inlcude these tests
    if args.include:
        arg_list.append('-i%s' % args.include)
        #arg_list.append('--include %s' % args.include) # This does not work for some reason?!

    if args.tags:
        for tag in args.tags:
            # TAG may be -TAG wich shold not be recognized as an option
            arg_list.append('--tags=%s' % tag)

    if args.verbose:
        # Do not output with colors
        # useful for debugging and
        # when Behave overwrites stdout (also look at prettyprint step)
        arg_list.append('--no-color')

    # Stop on error, useful when debugging
    #arg_list.append('--stop')

    # Do not wait with print statements, useful when debugging
    if args.verbose:
        arg_list.append('--no-capture')

    # Do not output multiple lines
    #arg_list.append('--no-multiline')

    # Do not use a virtual display for Studio, and keep it open after tests
    if args.display:
        arg_list.append('-D display')
    
    # Do everything but actually run the tests
    if args.dry_run:
        arg_list.append('--dry-run')

    # Output all available steps
    if args.steps_catalog:
        arg_list.append('--steps-catalog')

    # Pass the verbose argument to the Python code to control test output
    if args.verbose:
        arg_list.append('-D verbose')
    
    if args.verbose:
        arg_list.append('--verbose')
    
    if args.junit:
        arg_list.append('--junit')
    
    if args.junit_directory:
        for directory in args.junit_directory:
            arg_list.append('--junit-directory=%s' % directory)
    if args.outfile:
        for output_path in args.outfile:
            arg_list.append('-o=%s' % output_path)

    # Make output a little bit less verbose
    if not args.verbose:
        arg_list.append('--no-source')
        arg_list.append('--quiet')

    if args.verbose:
        print '# # arg_list: ', arg_list

    try:
        load_entry_point('behave==1.2.5', 'console_scripts', 'behave')(arg_list)
    except:
        print '  load_entry_point() failed on host: %s\n\n' % os.getenv('HOST')
        raise

    print '\n # # # # Exiting Behave World # # # #\n'

    if not args.display:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)

if __name__ == "__main__":
    args = get_parser_args()
    if args.verbose:
        print '# # behave args: ', args

    (old_stdout, old_stderr) = rebind_std_streams(args)
    collect_tests_run_and_exit_studio(args)
    restore_std_streams(old_stdout, old_stderr)


# End of file
