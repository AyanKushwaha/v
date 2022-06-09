import os
import sys

carmsysPath = os.environ['CARMSYS']
crewDataPath = os.environ['CARMUSR'] + '/Testing/perftests/crew_test_data.digxml'
assignDataPath = os.environ['CARMUSR'] + '/Testing/perftests/assig_test_data.digxml'
dbconn = os.environ['DATABASE']
dbschema = os.environ['DB_SCHEMA']

def loadRefreshData():
  #Load crew and assignments
  crewCommand = carmsysPath + '/bin/carmrunner loadDigXml  -c ' + dbconn + ' -s ' + dbschema + ' ' + crewDataPath
  assignCommand = carmsysPath + '/bin/carmrunner loadDigXml  -c ' + dbconn + ' -s ' + dbschema + ' ' + assignDataPath
  os.system(crewCommand)
  os.system(assignCommand)
