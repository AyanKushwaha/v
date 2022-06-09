from jeppesen.defaults import *

project = u'SAS Maintenance'
copyright = u'2012, Jeppesen Systems AB'

version = '1.0'
release = version

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', "ConfigurationManagementPlan_v%s.tex" % (version),
   u'Jeppesen SAS CMS Configuration Management Plan',
   u'Jeppesen Systems AB', 'manual'),
]
