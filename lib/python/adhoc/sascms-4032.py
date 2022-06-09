
"""
This script will modify the task names in est_calc_setup_node table (from Task___XX to XX)
and modify the tables which have references to that table
(est_calc_node_relation, est_task, est_driver, est_layout_node) 

Usage:
    bin/startMirador.sh --script -s adhoc.sascms-4032 [test]

"""
__verision__ = "$Revision$"
__author__ = "Berkay Beygo, Jeppesen"

import sys, os
from tm import TM
import carmensystems.manpower.core.modelserver_errors as modelserver_errors

class BaseError(Exception):
    pass


class TaskNameUpdater(object):
    def __init__(self, schema, dburl, save=False):
        self._schema = str(schema)
        self._dburl = str(dburl)
        self._save=save


    def connect(self):
        """
        Creates and opens connection to a DAVE database
        """
        sys.stdout.write("Connecting to url = %s, schema = %s ..." % (self._dburl, self._schema))
        TM.connect(self._dburl, self._schema, '')
        TM.loadSchema()
        sys.stdout.write(" ...Connected!\n")

    def __del__(self):
        """
        Closes down connections to the DAVE database
        """
        sys.stdout.write("Closing down database connection ...")
        TM.disconnect()
        sys.stdout.write(" Done!\n")

    def update_key_atts_table(self, TM, look_up_dict):
        """
        Updates the tables containing a reference to est_calc_setup_node table and the field to be updated is a key.
        First add a new row afterwards delete the old one
        
        @param TM:The table manager
        @type TM: TableManager 
        @param look_up_dict: matches the old reference to the new one
        @type look_up_dict: Dict
        """
        counter = 0
        for row in TM.est_calc_node_relation:
            try:
                if (row.child) in look_up_dict:
                    counter += 1
                    newRow = TM.est_calc_node_relation.create((row.parent, look_up_dict[row.child]))
                    newRow.factor = row.factor
                    TM.est_calc_node_relation[(row.parent, row.child)].remove()
            except Exception, e:
                print "\n error est_calc_node_relation :", row.child.name, e
        print "\n --Number of updates est_calc_node_relation: ", counter
              
    def update_non_key_atts_table(self, TM, look_up_dict):
        """
        Updates the tables containing a reference to est_calc_setup_node table and the field to be updated is a non key attribute.
        
        @param TM:The table manager
        @type TM: TableManager 
        @param look_up_dict: matches the old reference to the new one
        @type look_up_dict: Dict
        """
        counter = 0
        for row in TM.est_task:
            try:
                if (row.calcnode) in look_up_dict:
                    counter += 1
                    row.calcnode = look_up_dict[row.calcnode]
            except Exception, e:
                print "\n error est_task :", row.code, e
        print "\n --Number of updates est_task: ", counter
        
        counter = 0
        for row in TM.est_driver:
            try:
                if (row.depnode) in look_up_dict:
                    counter += 1
                    row.depnode = look_up_dict[row.depnode]
            except modelserver_errors.ReferenceError, e:                
                print "\n error est_driver :", row.name, e
        print "\n --Number of updates est_driver: ", counter
        
        counter = 0
        for row in TM.est_layout_node:
            try:
                if (row.calcnode) in look_up_dict:
                    counter += 1
                    row.calcnode = look_up_dict[row.calcnode]
            except Exception, e:
                print "\n error est_layout_node :", row.name, e
        print "\n --Number of updates est_layout_node: ", counter

           
    def run(self):
        self.connect()

        print "Loading tables"
        TM(["est_calc_setup_node"])
        TM(["est_calc_node_relation"])
        TM(["est_task"])
        TM(["est_layout_node"])
        TM(["est_driver"])
        TM.newState()
        
        look_up_dict = {}
        print "Running.."

        for row in [_ for _ in TM.est_calc_setup_node]:
            try:
                if (row.nodetype.name == "TASKDRIVER") and ("Task___" in row.name):
                    newRow = TM.est_calc_setup_node.create((row.setup, row.name.replace("Task___", "")))
                    newRow.nodetype = row.nodetype
                    look_up_dict [row] = newRow
                    
            except Exception, e:
                print "\n error1 :", row.name, e
                pass
            
        self.update_non_key_atts_table(TM, look_up_dict)
        self.update_key_atts_table(TM, look_up_dict)
        
        for k in look_up_dict.keys():
            TM.est_calc_setup_node[(k.setup, k.name)].remove()
        
        del look_up_dict
        if self._save:
            print "Saving..."
            TM.save()
        else:
            print "Not saving..."
        print "Done, exiting..."
        
def usage():
    print __doc__

def main(args):
    db_url = os.environ["DB_URL"]
    schema = os.environ["SCHEMA"]

    save = True
    try:
        if args[1] == "test":
            print "Test run without save."
            save = False
        
    except:
        pass
    updaterObj = TaskNameUpdater(schema, db_url, save)
    updaterObj.run()
    del updaterObj

main(sys.argv)
