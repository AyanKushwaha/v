#!/usr/bin/env python 



'''
This script is used to parse connection string and schema from PROD.xml, PROD_TEST.xml and CMSDEV.xml. cmsshell is not a good idea in long processes 
e.g when when export on a machine and import on another machine "schema_dp_prod_test.yml" instead fetching connection string and schema using cmsshell environment variable, we run this 
script with the path to the xml file and the profile type and the script parses them for us.

This script might be modified, feel free to change/extend it, for example exceptions for now are not handled you can add it.
'''

import xml.etree.ElementTree as ElementTree
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
import sys


schema = ""
db_map = {}
profiles = ['live', 'history', 'admin_live', 'admin_history', 'interbids', 'admin_live_dump', 'admin_history_dump']


def get_db_block(root, type):
    logging.debug('Fetching db tags...')
    db_map = {}
    for node in root.getchildren():
        db_map["%s/%s" % (type,node.tag)] = node.text
    logging.debug('Fetched db tags ')
    return db_map


def get_schema_block(root, type):
    schema_db_block = {}   
    logging.debug('Fetching schema tags...')
    for node in root.findall('./dave/profile'):
        if node.attrib['name'] == type:
            schema_db_block = get_db_block(node, type)
            break
    logging.debug('Fetched schema tags')
    return schema_db_block

    


def get_value_of_tag(var, type, db_map, schema_map):
    logging.debug('Fetching value of %s variable from xml' % var)
    xpath, char = parse_str(var)
    if xpath.startswith('db'):
       logging.debug( "Value of %s is %s%s" % (var, db_map[xpath], "%s" % char if char is not None else ''))
       return  "%s%s" % (db_map[xpath], "%s" % char if char is not None else '')
    else:
        xpath = schema_map[xpath]

        if xpath.startswith('%'):
            xpath = xpath[1:]
            char = char if char is not None else ''
            type = xpath[xpath.find('(')+1:xpath.find('/')]
            xpath += char
            logging.debug("Value of %s is %s" % (var, get_value_of_tag(xpath, type, db_map, schema_map)))
            return get_value_of_tag(xpath, type, db_map, schema_map)    



def parse_str(var):
    logging.debug('Removing parenthesis')
    var_b = var
    char = None
    if not var.endswith(')'):
      char = var[-1]
      var = var[:-1]
    logging.debug('%s is converted to %s' % (var_b, var))
    return (''.join([c for c in var if c != '(' and c != ')']), char)





def parse_connection(root, url, type):
    global db_map
    logging.debug('trying to parse the connection string: %s' % url)
    connection_str = ""
    db_map = get_db_block(root, 'db')
    schema_map = get_schema_block(root, type)
    for var in list(filter(None, url.split('%'))):
        if '/' in var:
            var = get_value_of_tag(var, type, db_map, schema_map)
        else: 
            pass
        if var != 'oracle:': 
            connection_str += var
            
    logging.debug('Connection string parsed. Result: %s' % connection_str)
    return connection_str


def get_connection_string(root, type):
    logging.debug('fetching profile for %s' % type)
    for node in root.findall('./dave/profile'):
        if node.attrib['name'] == type:
            logging.debug('Found the profile %s' % type)
            logging.debug('Searching for connection string in  children nodes')
            for child in node.getchildren():
                if child.tag == 'url':
                    logging.debug('Found connection string and return it: %s' % child.text)
                    return child.text
    logging.debug('Connection string not found')
    return None



def get_logging(verbose):
    if verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)




def parse_params():
    args = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    args.add_argument('-p', '--path', help='Path to xml file', required=True)
    args.add_argument('-t', '--type', help='Type of schema you want to dump', required=True)
    args.add_argument('-v', '--verbose', default=False, action='store_true', help='Increase output verbosity')
    return args.parse_args()



def get_error_msg():
    return sys.exc_info()[1]


def run():
    parser = parse_params()
    if parser.type not in profiles:
        logging.error('Invalid type. Type should be either live or history')
        exit(-1)
    get_logging(parser.verbose)
    logging.info('Parsing xml...')
    tree = None
    try:
        tree = ElementTree.parse("%s" % parser.path)
    except:
        logging.error("Could not parse: %s" % parser.path)
        logging.error("%s" % get_error_msg())
        exit(-1)

    root = tree.getroot()
    logging.debug('Getting url from %s' % parser.path)
   
    url = get_connection_string(root, parser.type)
    if url == None:
        logging.error("Could not fetch url. Check %s" % parser.path)
        logging.error("%s" % get_error_msg())
        exit(-2)


    con_str = parse_connection(root, url, parser.type)
    type = 'db/schema_%s' % ('live' if '_live' in parser.type else  'history')
    schema =  db_map[type]
    logging.debug('connection_str: %s' % con_str)
    logging.info('connection_str: %s' % con_str)
    # DON'T REMOVE/CHANGE FOLLOWING LINES, THEY ARE NEEDED IN ANSIBLE. ALSO THE ORDER MATTERS
    print "schema: %s" % schema
    print "connection_str: %s" % con_str



if __name__ == '__main__':
  run()
