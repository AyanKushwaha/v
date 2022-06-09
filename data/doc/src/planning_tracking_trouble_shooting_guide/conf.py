from jeppesen.defaults import *

project = u'SAS Planning and Tracking Troubleshooting Guide'
copyright = u'2012, Jeppesen Systems AB'

version = '1.0'
release = version

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', "TroubleShootingGuide_Planning_and_Tracking_v%s.tex" % (version),
   u'Jeppesen SAS CMS Planning and Tracking Troubleshooting Guide',
   u'Jeppesen Systems AB', 'manual'),
]
