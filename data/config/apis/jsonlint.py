#! /usr/bin/env python

import sys
import json


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "  usage: jsonlint.py <json-file>"
    for json_file in sys.argv[1:]:
        with open(json_file) as f:
            try:
                json.load(f)
            except ValueError, e:
                print "  Error in file '%s':" % json_file
                print "   ", e