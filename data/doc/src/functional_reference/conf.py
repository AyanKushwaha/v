from jeppesen.defaults import *

import datetime

project = u'Jeppesen SAS CMS Functional Reference'
copyright = u'2012, Jeppesen Systems AB'

version = '1.0'
release = version

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('contents', "FunctionalReference_v%s.tex" % (version),
   u'Jeppesen SAS CMS Functional Reference',
   u'Jeppesen Systems AB', 'manual'),
  ('crew_meal/index', "FunctionalReference_Crew_Meal_v%s.tex" % (version),
   u'Jeppesen SAS CMS Functional Reference Crew Meal',
   u'Jeppesen Systems AB', 'manual')
]
