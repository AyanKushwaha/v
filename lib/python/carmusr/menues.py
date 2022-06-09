#!/usr/bin/env python

#
# Code for creating menu files
# Note: depends a lot on rave and other python files!!!
#
# Requires studio.

import sys, os, os.path, time
import re, string, getopt
import random
import tempfile
import Errlog
import Cui
import tempfile
import carmensystems.rave.api as r

import carmstd.studio.area as area
import carmstd.rave as rave

def new2LevelMenu(fd, hook, title, name, titles, cmdSection, cmdElement):
    """
    1. Hooks a section menu into the menu 'hook'
    2. Defines a section menu pointing to element menues
    3. Defines element menues with, optionally section and, element commands

    Titles: dictionary with int(section, element) -> string title
            example: titles = {(1,0):'section 1',(1,1):'element 1.1'}
    fd:     file descriptor to an open file
    """
    # Hook into an existing menu
    fd.write('Menu %s {\n' % hook)
    fd.write('  "%s" f.menu %s\n' % (title, name))
    fd.write('}\n')
    fd.write('\n')

    fd.write('Menu %s {\n' % name)

    # Section menu
    for i in range(1,10):
        try:
            fd.write('  "%s" f.menu %s%s\n' % (titles[(i,0)], name, i))
        except KeyError, e:
            pass
    fd.write('}\n')
    fd.write('\n')

    # Element menu
    for i in range(1,10):
        try:
            if cmdSection:
                t = titles[(i,0)]
                fd.write('Menu  %s%s {\n' % (name, i))
                fd.write(cmdSection % (t, i))
            
            for j in range(1,40):
              try:
                t = titles[(i,j)]
                fd.write(cmdElement % (t, i, j))
              except KeyError, e:
                pass

            fd.write('}\n')
            fd.write('\n')
        except KeyError, e:
            pass


def new1LevelMenu(fd, hook, title, name, titles, cmdElement, useTitle = False):
    """
    1. Hooks an element menu into the menu 'hook'
    2. Defines an element menu with element commands

    Titles: dictionary with int element -> string title
        example: titles = {1:'long trip',2:'reserve'}
    fd:     file descriptor to an open file
    useTitle: true to use title instead of index
    """
    # Hook into an existing menu
    fd.write('Menu %s {\n' % hook)
    fd.write('  "%s" f.menu %s\n' % (title, name))
    fd.write('}\n')
    fd.write('\n')

    fd.write('Menu %s {\n' % name)

    # Section menu
    for i in range(1,40):
        try:
            t = titles[i]
            if useTitle:
                arg=t
            else:
                arg=i
            fd.write(cmdElement % (t, arg))
        except KeyError, e:
            pass
    fd.write('}\n')
    fd.write('\n')


def fetchCrewCostTitles():
    """
    Returns a dictionary with titles,
    key = (section, element)
    element == 0 gives the section title
    """
    # Fetch menu titles
    titles = {}
    
    raveExpr, = r.eval('default_context',r.foreach(r.times(10),
                                                       r.expr('roster_cost.%section_name%(fundamental.%py_index%)')))
    for loopId,sectionId in raveExpr:
        if sectionId <> "":
            titles[(loopId.index,0)] = sectionId
            
    raveExpr, = r.eval(r.foreach(r.times(10),
                                 r.foreach(r.times(40),
                                           r.expr('roster_cost.%element_name%(fundamental.%py_index1%,fundamental.%py_index%)'))))
    for loopId, elements in raveExpr:
        for loopId2, costElement in elements:
            if costElement <> "":
                titles[(loopId.index,loopId2.index)] = costElement
                       
    return titles   

def fetchTitles(raveVar, maxFetch=40):
    """
    Returns a dictionary with titles, key = element
    """
    # Fetch menu titles
    titles = {}
    raveExpr, = r.eval(r.foreach(r.times(maxFetch), raveVar))
    for loopId, title in raveExpr:
       if title <> "":
           titles[loopId.index] = title

    return titles
    


def bidMenu(fd):
    # titles = {(1,0):'section 1',(1,1):'element 1.1'}
    num_bids, = r.eval('crg_bid_statistics.%nr_bid_types%')
    titles = fetchTitles('crg_bid_statistics.%bid_description_ix%', num_bids)

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_bid_p\':\'T\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSelect', 'Bid', 'bidSelect', titles, cmdElement)

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_granted_bid_p\':\'T\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSelect', 'Granted bid', 'bidGrantSelect', titles, cmdElement)

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_not_granted_bid_p\':\'T\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSelect', 'Not granted bid', 'bidNotGrantSelect', titles, cmdElement)

    # Sub Select
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_bid_p\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSubSelect', 'Bid', 'bidSubSelect', titles, cmdElement)

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_granted_bid_p\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSubSelect', 'Granted bid', 'bidSubGrantSelect', titles, cmdElement)

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_bid_statistics.has_not_granted_bid_p\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\', \'studio_select.csl_string_1\':\'\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSubSelect', 'Not granted bid', 'bidSubNotGrantSelect', titles, cmdElement)


def qualificationMenu(fd):
    # titles = {(1,0):'section 1',(1,1):'element 1.1'}
    titles = fetchTitles('studio_qualifications.%ac_fam_ix%')

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'studio_qualifications.crew_has_qualification_csl1\':\'T\'},{\'studio_select.csl_int_1\':\'%s\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSelect', 'A/C Qualifications', 'acQualSelectCrew', titles, cmdElement, True)

    # Sub Select
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'studio_qualifications.crew_has_qualification_csl1\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_string_1\':\'%s\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrewSubSelect', 'A/C Qualifications', 'acQualSubSelectCrew', titles, cmdElement, True)

    # trips
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'qualifications.flight_leg_qual_ac\':\'%s\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrrSelect', 'A/C Qualifications', 'acQualSelectTrip', titles, cmdElement, True)

    # Sub Select
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'qualifications.flight_leg_qual_ac\':\'%s\', \'FILTER_METHOD\':\'SUBSELECT\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrrSubSelect', 'A/C Qualifications', 'acQualSubSelectTrip', titles, cmdElement, True)

    
def costMenu(fd):
    # titles = {(1,0):'section 1',(1,1):'element 1.1'}
    titles = fetchCrewCostTitles()

    # Select
    cmdSection = '  "Any cost for %s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crew_has_cost_csl1\':\'T\'},{\'studio_select.csl_int_1\':\'%s\'})")\n'
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crew_has_cost_csl1_csl2\':\'T\'},{\'studio_select.csl_int_1\':\'%s\',\'studio_select.csl_int_2\':\'%s\'})")\n'
    new2LevelMenu(fd, 'PredefinedCrewSelect', 'Cost Function', 'costSelect', titles, cmdSection, cmdElement)
    
    # Sub Select
    cmdSection = '  "Any cost for %s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crew_has_cost_csl1\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\'})")\n'
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crew_has_cost_csl1_csl2\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\',\'studio_select.csl_int_2\':\'%s\'})")\n'
    new2LevelMenu(fd, 'PredefinedCrewSubSelect', 'Cost Function', 'costCrewSubSelect', titles, cmdSection, cmdElement)
    
    # Sort
    cmdSection = '  "Total cost for %s" REDO f.exec PythonEvalExpr("MenuCommandsExt.sortParam(\'crg_roster_cost.sort_int_1\',{\'crg_roster_cost.sort_int_1\':\'%s\'})")\n'
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.sortParam(\'crg_roster_cost.crew_sort_cost_p1_p2\',{\'crg_roster_cost.sort_int_1\':\'%s\',\'crg_roster_cost.sort_int_2\':\'%s\'})")\n'
    new2LevelMenu(fd, 'SortCrew', 'Cost Function', 'SortCrewCost', titles, cmdSection, cmdElement)

    # Select trip
    # titles = {1:'long trip',2:'reserve'}
    titles = fetchTitles('roster_cost.%header_unassigned_ix%')

    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crr_has_cost_csl1\':\'T\'},{\'studio_select.csl_int_1\':\'%s\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrrSelect', 'Cost Function', 'SelectCrrCost', titles, cmdElement)

    # Sub Select trip
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.selectParam({\'crg_roster_cost.crr_has_cost_csl1\':\'T\', \'FILTER_METHOD\':\'SUBSELECT\'},{\'studio_select.csl_int_1\':\'%s\'})")\n'
    new1LevelMenu(fd, 'PredefinedCrrSubSelect', 'Cost Function', 'SelectCrrSubCost', titles, cmdElement)

    # Sort trip
    cmdElement = '  "%s" REDO f.exec PythonEvalExpr("MenuCommandsExt.sortParam(\'crg_roster_cost.crr_sort_cost_p1\',{\'crg_roster_cost.sort_int_1_crr\':\'%s\'})")\n'
    new1LevelMenu(fd, 'SortCrr', 'Cost Function', 'SortCrrCost', titles, cmdElement)

def usage():
    me=os.path.basename(sys.argv[0])
    print "Script to create a menues"
    print 
    print "Options:"
    print "  -h, --help"
    print "  -b, --bid=<file>             create a new bid menu"
    print "  -c, --cost=<file>            create a new cost menu"
    print "  -q, --qualification=<file>   create a new qualification menu"
    print 
    print "Example: create a cost menu:"
    print me+" -c /tmp/cost.menu"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:c:q:",
                 ["help", "bid=", "cost=", "qualification="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        return
    if len(opts)<1:
        usage()
        return
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-c", "--cost"):
            try:
              #fd = sys.stdout
              fd = open(os.path.expandvars(a.strip()), 'w')
              costMenu(fd)
            except Exception, e:
               Errlog.set_user_message('Failed to create menu: '+ a + '\n exception: '+ str(e));
        if o in ("-q", "--qualification"):
            try:
                fd = open(os.path.expandvars(a.strip()), 'w')
                qualificationMenu(fd)
            except Exception, e:
                Errlog.set_user_message('Failed to create menu: '+ a + '\n exception: '+ str(e));
        if o in ("-b", "--bid"):
            try:
                fd = open(os.path.expandvars(a.strip()), 'w')
                bidMenu(fd)
            except Exception, e:
                Errlog.set_user_message('Failed to create menu: '+ a + '\n exception: '+ str(e));

if __name__ == "__main__":
    main()

