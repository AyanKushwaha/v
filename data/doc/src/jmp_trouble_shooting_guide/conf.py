from jeppesen.defaults import *

project = u'SAS JMP Troubleshooting guide'
copyright = u'2012, Jeppesen Systems AB'

version = '1.0'
release = version

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', "TroubleShootingGuide_Manpower_v%s.tex" % (version),
   u'Jeppesen SAS CMS Manpower Troubleshooting guide',
   u'Jeppesen Systems AB', 'manual'),
]
