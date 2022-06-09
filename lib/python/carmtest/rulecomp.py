import carmstd.parameters as parameters
import os

def test():
  ruleSets=[
    parameters.RuleSet('default_cct',apps="gpc fandango"),
    parameters.RuleSet('default_ccr',apps="gpc matador"),
    parameters.RuleSet('default_ccp',apps="gpc apc"),
    parameters.RuleSet('BuildRotations',apps="gpc")
    ]
  for r in ruleSets:
    if os.path.exists(r.getFilePath()):
      r.compile()
    else:
      print 'RuleSet %s does not exist' % r

if __name__=='__main__':
  test()
  sys.exit(0)
