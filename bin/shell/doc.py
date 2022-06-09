#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import glob
import os
import shutil
import subprocess
import sys
import fnmatch
import distutils.dir_util


WORKDIR=os.getenv('CARMUSR')

#dir containing document sources
DOC_SRC_DIR=os.path.join(WORKDIR, 'data/doc/src')

#dir for generated documentation
GENERATED_DOCS=os.path.join(WORKDIR, 'docs')

#dir containing contrib packages
PYTHON_CONTRIB_PACKAGES=os.path.join(WORKDIR, 'lib/contrib')

#dir where contrib libs are unpacked
PYTHON_CONTRIB=os.path.join(WORKDIR, 'lib/contrib/python')

# Dir for java files
JAVA_DIR= os.path.join(WORKDIR, 'java_src')

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


def _execute_shell_cmd(cmd):
    """ Executes a shell command and returns the return code, stdout and sterr
    """
    proc = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (out, err) = proc.communicate()
    ret = proc.wait()
    return (ret, out, err)

#Creating contrib lib, if not already existing
def _prepare_contrib_dir(force_update=False):
    if force_update:
        print "Cleaning contrib dir (%s)" % PYTHON_CONTRIB
        shutil.rmtree(PYTHON_CONTRIB)
    if not os.path.exists(PYTHON_CONTRIB):
        print "Creating contrib dir (%s)" % PYTHON_CONTRIB
        os.mkdir(PYTHON_CONTRIB)

#unpacking contrib packages
def _unpack_contrib_packages():
    for f in glob.glob("%s/*.zip" % PYTHON_CONTRIB_PACKAGES):
        bn = os.path.splitext(os.path.basename(f))[0]
        package_dir_name = os.path.join(PYTHON_CONTRIB, bn)
        if not os.path.exists(package_dir_name):
            print "Preparing %s ..." % bn
            _execute_shell_cmd("unzip %s -d %s" % (f, PYTHON_CONTRIB))

#Builds documentation with Sphinx
# Parameters:
#  sourceDir: dir containing the Sphinx document
#  targetDir: dir where generated documentation shall be stored
#  type:      'html' or 'latex'
def _build_documentation(sourceDir, targetDir, type="html"):
    import sphinx
    sphinx.main(["placeholder",
                 "-b",
                 "%s" % type,
                 "%s" % sourceDir,
                 "%s" % targetDir])

    if type == "latex":
        print "Generating pdf file from LaTeX source ..."
        make_command = "make -C \"%s\"" % targetDir
        _execute_shell_cmd(make_command)

#generating documentation for each document in doc dir
def _generate_documentation(formats, document=None):

    doc_glob = "%s/" % DOC_SRC_DIR
    
    if document:
        doc_glob += "%s" % document
    else:
        doc_glob += "*"

    for d in glob.glob(doc_glob):
        bn = os.path.basename(d)
        print d, bn
        if os.path.isdir(d) and \
            not bn == "CVS" and \
            not bn[0] == "." and not bn[0] == "_":
            print "Processing '%s' documentation ..." % bn
            for f in formats:
                _build_documentation(d,
                                     os.path.join(
                                         os.path.join(
                                             GENERATED_DOCS,
                                             os.path.basename(d)),
                                         format_output_folder_mapping[f]),
                                     f)




def _find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename



def generate_udm(name = "udm.pdf"):
    """ Generates the UDM
    """

    if not os.path.exists(GENERATED_DOCS):
        os.mkdir(GENERATED_DOCS)

    path = os.path.expandvars("${CARMUSR}/data/config/models/documentation")
    os.chdir(path)
    ret, std, err = _execute_shell_cmd("make")    
    print std
    print err 
    
    generated_file = os.path.join(path, name)
    if not os.path.exists(generated_file):
        print "Failed to create udm"
        return 1
    
    shutil.copy(generated_file, GENERATED_DOCS)
    print "%s created %s" % (name, GENERATED_DOCS)
    
    return ret
    
def generate_rule_description(name=None):
    """ Generates rule descirption
    """

    if not os.path.exists(GENERATED_DOCS):
        os.mkdir(GENERATED_DOCS)

    if name is None:
        name = "rules.pdf"

    print "Compiling Java code..."    
    _CLASSPTH = [os.path.join(JAVA_DIR, "com.carmensystems.rave.parsers.jar"),
                 os.path.join(JAVA_DIR, "antlr-3.1.1.jar")]     
    _CLASSPTH = ":".join(_CLASSPTH)
    javac_path = 'javac'
    cmd = os.path.expandvars("%s -cp %s %s" % (javac_path, _CLASSPTH, os.path.join(JAVA_DIR, "DocumentRules.java")))
    ret, std, err = _execute_shell_cmd(cmd)
    if ret != 0:
        print "Failed to compile"
        print std, err
        return 1 
    
    print "Running Java code..."
    cmd = os.path.expandvars("java -cp %s:%s DocumentRules ${CARMUSR} > ${CARMUSR}/data/doc/rules.tex" % (_CLASSPTH, JAVA_DIR))
    ret, std, err = _execute_shell_cmd(cmd)

    if ret != 0:
        print "Failed to generate rules description"
        print std, err
        return 1 
        
    os.chdir("/tmp")

    print  "Compiling LaTeX..."
    cmd = os.path.expandvars("pdflatex ${CARMUSR}/data/doc/rules.tex")
    ret, std, err = _execute_shell_cmd(cmd)

    if ret != 0:
        print "Failed to compile LaTeX"
        print std, err
        return 1 

    shutil.copy(name, GENERATED_DOCS)
    
    print "rules.pdf created %s" % (GENERATED_DOCS) 
    return 0


def generate_udt(document=None, force_update=False, pdf=False, html=True):
    """ Generates the UDT
        document - Specify the document to generate. Default behaviour is to build all documents
        pdf - generate pdf (default=False)
        html - generate html (default=True)
        force_update - force update of contrib (default=False)
        
    """

    if not os.path.expanduser(GENERATED_DOCS):
        os.mkdir(GENERATED_DOCS)

    out_formats = []
        
    if html:
        out_formats.append('html')

    if pdf:
        out_formats.append('latex')
    
    print "Prepare contrib dir..."    
    _prepare_contrib_dir(force_update)
    print "Unpack contrib packages..."
    _unpack_contrib_packages()
    print "Generate documentation..."
    _generate_documentation(out_formats, document=document)


def compile_release(out_dir, clean=False, rules=False):
    """ Compiles a documentation release
        out_dir - Destination directory
        clean - Remove generated docs before building (Default: False)
        rules - Generate rules.pdf documentation (Default: False)
    """
    
    if clean:
        print "INFO: Deleting %s" % (GENERATED_DOCS)
        distutils.dir_util.remove_tree(GENERATED_DOCS)
    
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.getcwd(), out_dir)

    # Create new release directory structure
    release_dir = out_dir
    indx = 1
    while os.path.exists(release_dir):
        release_dir = "%s_%u" % (out_dir, indx)
        indx += 1 

     
    # Create main directories
    print " - Creating directories"
    func_ref_dir = os.path.join(release_dir, "functional_reference")
    spec_dir = os.path.join(release_dir, "specifications")
    manuals_dir = os.path.join(release_dir, "manuals")
    project_dir = os.path.join(release_dir, "project")
             
    for dir in [release_dir, func_ref_dir, spec_dir, manuals_dir, project_dir]:
        os.mkdir(dir)

    # Copy the pdf generated from word documents
    print " - Copying Word documents in pdf format to outdir"
    word_files_converted_to_pdf_dir = os.path.join(WORKDIR, 'data', 'doc', 'word_src', 'pdfs')

    if not os.path.exists(word_files_converted_to_pdf_dir) or not os.path.isdir(word_files_converted_to_pdf_dir):
        print "WARNING: No directory containing pdf versions of Word documents found, skipping word documents"
    else:
        copied_files = distutils.dir_util.copy_tree(word_files_converted_to_pdf_dir, release_dir)
        if len(copied_files) < 5:
            print "WARNING: Only these files were copied from word_src, forgotten to generate PDFs?"
                
    # Create rule description
    if rules:
        print " - Generating rule documentation"
        rule_description = "rules.pdf"
        generate_rule_description(name=rule_description)
        print " - Copying rule documentation to outdir"
        shutil.copy(os.path.join(GENERATED_DOCS, rule_description), func_ref_dir)
    
    # Create UDM
    print " - Generating UDM documentation"
    udm = "udm.pdf"
    generate_udm(udm)
    print " - Copying UDM documentation to outdir"
    shutil.copy(os.path.join(GENERATED_DOCS, udm), func_ref_dir)
        
    #Create UDT
    print " - Generating UDT documents (pdf)"
    generate_udt(pdf=True, html=False)
    
    #Find all pdfs and copy them
    print " - Copying UDT documents"
    skip_files = ["udm.pdf", "rules.pdf"]
    dst_dict = {"functional_reference" : func_ref_dir, 
                "trouble_shooting_guide" : manuals_dir,
                "configuration_management" : project_dir,
                "system_administration_guide": manuals_dir}
    
    for file in _find_files(GENERATED_DOCS, "*.pdf"):
        if os.path.basename(file) in skip_files:
            continue
        
        for pattern, dst in dst_dict.iteritems():             
            if file.find(pattern) > -1:
                shutil.copy(file, dst)

    # Clean files
    print " - Cleaning up"
    clean_file_patterns = ["*.db"]

    for pattern in clean_file_patterns: 
        for file in _find_files(release_dir, pattern):
            print "removing file %s" % (file)
            os.remove(file)
        

    print "Documentation release created in: %s" % (release_dir)

if __name__ == "__main__":
    generate_udt()






    

