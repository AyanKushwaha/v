#!/usr/bin/python

#
# Script for creating add on menues for specific roles.
# 

import os
import time
import traceback

def createAddonMenu():
    user_role = os.environ.get("CARMROLE")
    user_name = os.environ.get('USER')
    
    addon_menu_file = os.path.join(os.getenv('CARMUSR'), "menu_scripts",
                                   "cmsadm", "addons", "%s.menu" % user_role)
    
    dyn_dir_path = os.getenv('CARMTMP')+'/addon_menus'
    dyn_file_path = os.path.join(dyn_dir_path, 'addon_%s.menu' %user_name)

    # Determine if there is a addon file created before, and if so remove it
    if os.path.isfile(dyn_file_path):
        try: 
            os.remove(dyn_file_path)
        except OSError:
            print "MenuAddon::Main::Could not remove file %" % dyn_file_path
            pass

    # Determine if the user needs special menu or not.    
    if os.path.isfile(addon_menu_file):

        login_time = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
        
        addon_menu_txt = "%s%s" % ("/* This is a menu file specially created for\n",
                                   "   the user %s logged in as %s at %s. */\n\n"
                                   % (user_name, user_role, login_time))

        try:
            # Get the addon data
            addon_menu = open(addon_menu_file)
            addon_menu_txt += addon_menu.read()
            addon_menu.close()
            
            if not os.path.isdir(dyn_dir_path):
                os.makedirs(dyn_dir_path)
            new_tmp_menu = open(dyn_file_path, "w")
            new_tmp_menu.write(addon_menu_txt)
            new_tmp_menu.close()
        
        except:
            traceback.print_exc()
            print "MenuAddon::Main::Error building addon menu"


# Runs the funtion to create the addon menu. 
createAddonMenu()

    
