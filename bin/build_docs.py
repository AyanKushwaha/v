#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script for generating documentation in various formats from
# reStructuredText formatted source documents.
#
# Authors: Henrik Algestam (henrik.algestam@jeppesen.com)
#          Rickard Petzäll (rickard.petzall@jeppesen.com)

import glob
from optparse import OptionParser
import os
import shutil
import subprocess
import sys

if os.getenv('CARMUSR'):
    WORKDIR=os.getenv('CARMUSR')
else:
    WORKDIR=os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))

#dir containing document sources
DOC_SRC_DIR=os.path.join(WORKDIR, 'data/doc/src')

#dir for generated documentation
GENERATED_DOCS=os.path.join(WORKDIR, 'docs')

#dir containing contrib packages
PYTHON_CONTRIB_PACKAGES=os.path.join(WORKDIR, 'lib/contrib')

#dir where contrib libs are unpacked
PYTHON_CONTRIB=os.path.join(WORKDIR, 'lib/contrib/python')

#Adding sphinx and its dependencies to sys.path
sys.path.append(PYTHON_CONTRIB)

#dir containing Jeppesen sphinx defaults
SPHINX_DEFAULTS=os.path.join(WORKDIR, 'data/doc/common')

#Adding Jeppesen sphinx defaults to sys.path
sys.path.append(SPHINX_DEFAULTS)

#Added necessary LaTex files to $TEXINPUTS
os.environ['TEXINPUTS'] = ".:%s:%s:" % (os.path.join(WORKDIR, 'lib/LaTeX'),
                                       os.path.join(PYTHON_CONTRIB, 'sphinx/texinputs'))

format_output_folder_mapping = {'html': 'html',
                                'latex': 'pdf'}

def shell_exec(command):
    (stdout,stderr)=subprocess.Popen(command,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE).communicate()
    return stdout

#Creating contrib lib, if not already existing
def prepare_contrib_dir(force_update=False):
    if force_update:
        print "Cleaning contrib dir (%s)" % PYTHON_CONTRIB
        shutil.rmtree(PYTHON_CONTRIB)
    if not os.path.exists(PYTHON_CONTRIB):
        print "Creating contrib dir (%s)" % PYTHON_CONTRIB
        os.mkdir(PYTHON_CONTRIB)

#unpacking contrib packages
def unpack_contrib_packages():
    for f in glob.glob("%s/*.zip" % PYTHON_CONTRIB_PACKAGES):
        bn = os.path.splitext(os.path.basename(f))[0]
        package_dir_name = os.path.join(PYTHON_CONTRIB, bn)
        if not os.path.exists(package_dir_name):
            print "Preparing %s ..." % bn
            shell_exec("unzip %s -d %s" % (f, PYTHON_CONTRIB))

#Builds documentation with Sphinx
# Parameters:
#  sourceDir: dir containing the Sphinx document
#  targetDir: dir where generated documentation shall be stored
#  type:      'html' or 'latex'
def build_documentation(sourceDir, targetDir, type="html"):
    import sphinx
    sphinx.main(["placeholder",
                 "-b",
                 "%s" % type,
                 "%s" % sourceDir,
                 "%s" % targetDir])

    if type == "latex":
        print "Generating pdf file from LaTeX source ..."
        make_command = "make -C \"%s\"" % targetDir
        shell_exec(make_command)

#generating documentation for each document in doc dir
def generate_documentation(formats, document=None):

    doc_glob = "%s/" % DOC_SRC_DIR
    
    if document:
        doc_glob += "%s" % document
    else:
        doc_glob += "*"
        
    for d in glob.glob(doc_glob):
        bn = os.path.basename(d)
        if os.path.isdir(d) and \
            not bn == "CVS" and \
            not bn[0] == ".":
            print "Processing '%s' documentation ..." % bn
            for f in formats:
                build_documentation(d,
                                    os.path.join(
                                        os.path.join(
                                            GENERATED_DOCS,
                                            os.path.basename(d)),
                                        format_output_folder_mapping[f]),
                                    f)

if __name__ == "__main__":

    out_formats = ['html']
    
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-i", "--document",
                      action="store", type="string", dest="document",
                      help="Specify the document to generate. Default behaviour is to build all documents.",
                      default=None)
    parser.add_option("-d", "--disable-html", dest="no_html_output",
                      action="store_true", default=False,
                      help="Do not generate html documents")
    parser.add_option("-p", "--pdf", dest="output_pdf",
                      action="store_true", default=False,
                      help="Generate pdf documents")
    parser.add_option("-u", "--force-update", dest="force_update",
                      action="store_true", default=False,
                      help="Force update of built-in libraries")

    (opts, args) = parser.parse_args()
    
    if opts.no_html_output:
        out_formats.remove('html')

    if opts.output_pdf:
        out_formats.append('latex')
    
    prepare_contrib_dir(opts.force_update)
    unpack_contrib_packages()
    generate_documentation(out_formats, document=opts.document)
    
