#!/usr/bin/env python

import os
import zipfile
import argparse
import logging
import time
import shutil
from dateutil.parser import parse


abspath_to_carmuser = "/opt/Carmen/CARMUSR"
temp_folders = ["current_carmtmp_cas", "current_carmtmp_cct"]
carmuser_path = None


"""
    This module finds the desired map and corresponding temp map and compresses them. The  purpose is to 
    get more spaces. 
"""


def strtosec(strtime):
    """ Simple string to time parser.

    This function get time string and parse it to seconds.

    Args:
        strtime (str): unix like time stamp

    Returns:
        t (int): seconds of time passed

    Raises:
        ValueError: if strtime is not possible to parse; then kill the process with signal 1.
    """
    try:
        ptime = parse(strtime)
        return time.mktime(ptime.timetuple())
    except ValueError:
        logging.error("Can not parse '%s' to date", strtime)
        exit(1)


# pack all folders in a directory
def pack_folders(root, parent_path, folders):
    for folder_name in folders:
        abs_path = os.path.join(root, folder_name)
	relative_path = abs_path.replace(parent_path + "/", "")
        logging.debug("Adding %s to archive..." % abs_path)
        zip_file.write(abs_path, relative_path)
        logging.debug("Added %s to archive" % abs_path)


# pack all files in a specific directory
def pack_files(root, parent_path, files):
    for file_name in files:
        abs_path = os.path.join(root, file_name)
        relative_path = abs_path.replace(parent_path + "/", "")
        if not is_a_dead_link(abs_path):
            logging.debug("Adding %s to archive" % abs_path)
            zip_file.write(abs_path, relative_path)
            logging.debug("Added %s to archive" % abs_path)



#pack all directories, subdirectories and files in carmuser and temp directories
def pack_dir(parent_path):
    contents = os.walk(parent_path)
    output_path = parent_path + ".zip"
    global zip_file
    try:	
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True)

        for root, folders, files in contents:
            pack_folders(root, parent_path, folders)
            pack_files(root, parent_path, files)
        logging.info("%s scuccessfully created" % output_path)
    except IOError, message:
        logging.error(message, exc_info=True)
        exit(1)
    except OSError, message:
        logging.error(message, exc_info=True)
        exit(1)
    except zipfile.BadZipfile, message:
        logging.error(message, exc_info=True)
	print (1)
    except zipfile.LargeZipFile, message:
        logging.error(message, exc_info=True)
        exit(1)
    finally:
       zip_file.close()






def is_a_dead_link(path):
    is_a_dead_link = os.path.islink(path) and not os.path.exists(os.readlink(path))  
    if is_a_dead_link:
        logging.debug("Unlinking %s..." % path)
        os.unlink(path)
	return True
    return False 

"""
   Makes sure that carmuser path exists and carmuser path is not a symbolic link
   Symbolic links often maight be under development, carmuser under developmenet should
   be excluded.
"""
def find_required_paths(carmuser_path):
    mypath = os.path.join(abspath_to_carmuser, os.path.basename(carmuser_path))
 
    if not mypath == carmuser_path:
        carmuser_path = os.path.join(abspath_to_carmuser, carmuser_path)
    

    if not os.path.exists(carmuser_path):
        logging.error("%s does not exist. Program exited" % carmuser_path)
        exit(1)
   
    if(os.path.islink(carmuser_path)):
        logging.error("%s is a symbolic link. Carmuser is under development" % carmuser_path)
        exit(2)
 
    temp_dirs = get_temp_dirs(carmuser_path)
    # temo_dirs is empty, then it should be a carmuser for finnair
    if not temp_dirs:
       logging.error("%s seems to belong to FINNAIR" % carmuser_path)
       exit(3)

    if len(temp_dirs) < 3:
       print_missing_temp_dir(temp_dirs)


    return carmuser_path, temp_dirs

   
    # remove older carmuser and temp directories   
    # remove old files and directories
    for temp in temp_dirs:
        remove_dir(temp)
    remove_dir(carmuser_path)

  
    


"""
    Returns carm temp directories for a specific directory
"""
def get_temp_dirs(carmuser_path):
    temp_dirs = []
    for folder_name in os.listdir(carmuser_path):
        folder_path = os.path.join(carmuser_path, folder_name)
        if os.path.islink(folder_path) and folder_name in temp_folders:
            symlink_path = os.readlink(folder_path)
            if os.path.exists(symlink_path):
                temp_dirs.append(os.path.abspath(symlink_path))
    return temp_dirs



"""
    Removes read-only files by first giving write permission then remove
"""
def del_even_read_only(action, name, exc):
    try:
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    except:
        logging.error("Could not change mode of %s" % name)


"""
    Loops through all subdirectories and removes them
"""
def remove_dir(dir_to_remove):
    logging.info("Removing %s..." % dir_to_remove)
    from shutil import rmtree
    rmtree(dir_to_remove, onerror=del_even_read_only)
    logging.info("Removed %s " % dir_to_remove)


"""
     Checks whether there are some missing carmtemp directories, if there  are some, the function shows
     them 
"""
def print_missing_temp_dir(temp_list):
    missing_dirs = [item for item in temp_list if item not in temp_folders] 
    for temp in missing_dirs:
       logging.error("%s is missing" % temp)

    if missing_dirs:
        exit(1)


    	

def run():
    import argparse
    #  parser = argparse.ArgumentParser(description="archive carmukser path")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--carmuser', required=True, help="path of carmuser")
    parser.add_argument('-k', '--keep', default=False, action='store_true', help='set keep flag to True which in return DOES NOT REMOVE the carmuser directory!')
    parser.add_argument('-d', '--delete', default=False,  action='store_true', help='set to delete carmuser folder without zip it')
    parser.add_argument('-o', '--output', default="",  help='set output file name to save log messages')
    parser.add_argument('-v', '--verbos', default=False, action='store_true', help='set logging to verbos (debug level)')
    args = parser.parse_args()
    if args.verbos:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    if args.output != "":
        logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel, filename=args.output, handlers=[logging.StreamHandler])
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    logging.info("Args are parsed and started the archiving process")
    try:
        carmuser_path, temp_dirs = find_required_paths(args.carmuser if args.carmuser else args.c)
	logging.debug("carmuser_path is: {0}".format(carmuser_path))
    
        for temp_dir in temp_dirs:
            pack_dir(temp_dir)

        if args.delete:
	    shutil.rmtree(carmuser_path, ignore_errors=True, onerror=logging.error("Error occurred during deleting carmuser directory and error ignored!!!"))
        else:
	    pack_dir(carmuser_path)


        """"
            remove dirs and files
        """
        if not args.keep:
	    for temp_dir in temp_dirs:
	        remove_dir(temp_dir)
	    remove_dir(carmuser_path)

    except KeyboardInterrupt, message:
        logging.error("Program Interrupted!")
    

if __name__ == "__main__":
    start_time = time.strftime("%c")
    run()
    end_time = time.strftime("%c")
    logging.info("End of the execution at %s and took: %0.2f seconds.\n\n" % (end_time, strtosec(end_time) - strtosec(start_time)))
	
