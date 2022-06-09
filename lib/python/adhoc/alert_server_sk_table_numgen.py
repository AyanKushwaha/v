#!/usr/bin/env python

# Python code to rearrange table numbering

def list_modification_run(module, table):
    import re, shutil

    start_flag = False
    end_flag = False
    counter = 1
    remove_number_pattern = re.compile('[0-9] ->')
    # Check the start point of table with table alert_grouping_customization_tab
    # and check end point of table end keyword
    with open(module, 'r') as old:
        with open('new', 'w') as new:
            for line in old:
                if not end_flag and re.search(table, line):
                    start_flag = True
                    new.write(line)
                elif start_flag and re.match('(?:end)', line):
                    end_flag = True
                    new.write(line)
                elif not end_flag and start_flag:
                    # remove numbers in the line
                    if remove_number_pattern.search(line):
                        new.write(line.replace(line.split()[0], str(counter)))
                        counter += 1
                    else:
                        new.write(line)

                else:
                    new.write(line)
    shutil.move('new', module)

if __name__ == '__main__':
    list_modification_run('alert_server_sk', 'alert_grouping_customization_tab')
