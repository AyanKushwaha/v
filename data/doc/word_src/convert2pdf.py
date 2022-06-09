#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import fnmatch
import sys


# Check environment
if sys.platform.find("win") < 0:
    print "This script must be executed on Windows"
    sys.exit(1)
else:
    try:
        import win32com.client as win32
    except:
        print "Python Win32 not found, please install"
        sys.exit(1)


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def convert2pdf(doc_file, out_dir):
    
    out_file = os.path.basename(doc_file)
    out_file = os.path.join(out_dir, out_file[:out_file.rfind(".")] + ".pdf")
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = False
    
    doc = word.Documents.Open(doc_file)

    # Set print view. Needed in Word 2013 where read-only view is default.
    wdPrintView = 3
    
    #Making sure that the final revision is displayed
    wdRevisionsViewFinal = 0

    view = word.ActiveDocument.ActiveWindow.View
    view.Type = wdPrintView
    view.ShowRevisionsAndComments = False
    view.RevisionsView = wdRevisionsViewFinal

    #Exporting document as pdf
    wdExportFormatPDF = 17
    wdExportOptimizeForPrint = 0

    doc.ExportAsFixedFormat(out_file,
                            wdExportFormatPDF,
                            OpenAfterExport=False,
                            OptimizeFor=wdExportOptimizeForPrint,
                            UseISO19005_1=True)
    wdSaveOptions = 0
    doc.Close(SaveChanges=wdSaveOptions)
    word.Application.Quit()


if __name__ == "__main__":
    
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    (opts, args) = parser.parse_args()
            
    in_dir = os.getcwd()
                
    out_dir =  os.path.join(in_dir, "pdfs")
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
        
    for doc_file in find_files(in_dir, "[!~]*.doc*"):
        out_dir = os.path.dirname(doc_file.replace(in_dir, os.path.join(in_dir, "pdfs")))
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
    
        print doc_file
        convert2pdf(doc_file, out_dir)
        
        
