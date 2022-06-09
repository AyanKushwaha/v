#!/usr/bin/env python

"""
A utility for updating values within XML files.

USAGE:

For usage instructions:
xmledit.py --help

EXAMPLES:

Consider this file 'data.xml':

<?xml version="1.0" ?>
<program>
  <user>
    program-user
  </user>
  <config>
    <user>
      username
    </user>
  </config>
</program>

 * Setting the value of 'user' to 'myself' within <program><config>:

   ./xmledit.py -p program/config -s user myself data.xml

TODO:

 * Handle character encodings. All files are currently automatically converted
   to utf-8. It would be better if the encoding of the original file were kept.
 
"""

from xml.dom.minidom import parse
from optparse import OptionParser
from sys import exit

_options = {}

def set_elements(dom, element, value):

    global _options
    
    path_list = []
    if _options.element_path:
        path_list = _options.element_path.split("/")

    if len(path_list) > 0:
        set_elements_in(get_elements_with_tagname(dom.childNodes, path_list[0]),
                        path_list[1:],
                        element,
                        value)
        
    else:
        set_elements_in(dom, [], element, value)

def set_elements_in(elements, path, element_to_set, new_value):
    for e in elements:
        if len(path) > 0:
            set_elements_in(get_elements_with_tagname(e.childNodes, path[0]),
                            path[1:],
                            element_to_set,
                            new_value)
        else:
            for element_to_set in get_elements_with_tagname(e.childNodes,
                                                            element_to_set):
                set_element_value(element_to_set, new_value)

def get_elements_with_tagname(element_list, tagname):
    l = []
    for e in element_list:
        try:
            if e.tagName == tagname:
                l.append(e)
        except:
            pass
    return l

def set_element_value(element, value):
    element.childNodes[0].data = value

if __name__ == "__main__":
    usage = "usage: %prog [options] xml files to process"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--filter", dest="filter",
                      help="Only edit elements with tagname matching filter")
    parser.add_option("-n", "--dry-run", action="store_true", dest="dryrun",
                      default=False,
                      help="Run program without actually changing any files")
    parser.add_option("-s", "--set", dest="set_element", nargs=2,
                      help="Sets value for element (eg. -s element value)")
    parser.add_option("-p", "--path", dest="element_path",
                      help="Path that specifies elements")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Make a lot of noise")

    (opts, args) = parser.parse_args()

    _options = opts

    if(len(args) == 0):
        print "No file(s) specified."
        exit()

    for f in args:
        if _options.verbose:
            print "Processing '%s...'" % f

        try:
            current = open(f)
        except:
            print "Could not open file '%s'" % f
            continue

        try:
            dom = parse(f)
        except:
            print "Could not parse file '%s'" % f
            continue

        current.close()

        if _options.set_element:
            set_elements(dom, _options.set_element[0], _options.set_element[1])

        if not _options.dryrun:
            try:
                savefile = open(f, "w")
                savefile.write(dom.toxml())
                savefile.close()
            except:
                print "Failed to save file '%s'" % f
                exit()

