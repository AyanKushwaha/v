#!/usr/bin/env python

import os
import sys
import tempfile
import time

if __name__ == "__main__":

    fd_output, output_name = tempfile.mkstemp(prefix='output_', text=True)
    output_file = os.fdopen(fd_output,'w')

    (fd, steps_catalog_name) = tempfile.mkstemp(prefix='steps_catalog_', text=True)
    os.close(fd)
    print 'the steps catalog file: %s' % steps_catalog_name
    cmd = 'bin/test_behave.py --steps-catalog -i notest > %s' % steps_catalog_name
    os.system(cmd)


    (fd, dry_run_name) = tempfile.mkstemp(prefix='dry_run_', text=True)
    os.close(fd)
    print 'the dry_run file: %s' % dry_run_name

    cmd = 'bin/test_behave.py --dry-run > %s' % dry_run_name
    os.system(cmd)

    #steps_catalog_name = '/tmp/24972604.1.login/steps_catalog_pmIs3c'
    #dry_run_name = '/tmp/24972604.1.login/dry_run_h3Jr6W'

    examples = []
    with open(steps_catalog_name, 'r') as steps_catalog:
        current_step = 'No step yet'
        search_example = False

        for line in steps_catalog:
            line_strip = line.strip()
            if line_strip:
                if not line.startswith(' '): # Found a new step
                    #print line[:-1]
                    if search_example:
                        output_file.write('Error : No example for:  %s' % current_step)
                    search_example = True
                    current_step = line
                elif line.startswith('     '):
                    # Best Practice to use >4 blanks for step comments
                    pass
                elif line_strip.startswith('|'):
                    examples.append(line_strip)
                elif line.startswith('   '):
                    # Example step found
                    search_example = False
                    try:
                        example = line[4:-1].split(' ', 1)[1]
                        #print example
                        examples.append(example)
                    except:
                        pass # Strange example
                else: # Found alternative steps...
                    #print line
                    pass
    #print 'examples: ', examples

    actual_steps = []
    with open(dry_run_name) as dry_run:
        for line in dry_run:
            line_strip = line.strip()
            if line_strip:
                if line_strip.startswith('|'):
                    actual_steps.append(line_strip)
                elif line.startswith('    '):
                    step = line[4:-1].split(' ', 1)[1]
                    actual_steps.append(step)

    #print 'actual steps : ', actual_steps


    for example in examples:
        if not example in actual_steps:
            output_file.write('Error : No test for:  %s\n' % example)
    output_file.close()

    cmd = 'emacs %s &' % output_name
    os.system(cmd)

    # Wait until emacs really starts
    time.sleep(5)
    os.unlink(steps_catalog_name)
    os.unlink(dry_run_name)
    os.unlink(output_name)

