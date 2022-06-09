from jeppesen.defaults import *

project = u'Jeppesen SAS CMS System Administration Guide'
copyright = u'2013, Jeppesen Systems AB'

version = '1.0'
release = version

source_encoding = 'utf-8-sig'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', "SystemAdministrationGuide_v%s.tex" % (version),
   u'Jeppesen SAS CMS System Administration Guide',
   u'Jeppesen Systems AB', 'manual'),
]
