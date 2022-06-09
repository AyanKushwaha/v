import Cui
import carmensystems.rave.api as R
from carmensystems.rave.api import RuleFail

modifiedCrew = None

def preSave():
    global modifiedCrew
    import carmusr.modcrew as modcrew
    modifiedCrew = [str(crew) for crew in modcrew.get()]
    
    printRuleFailures()

def postSave():
    printRuleFailures()
    
    
def printRuleFailures():
    mc = modifiedCrew
    if mc is None:
        import carmusr.modcrew as modcrew
        mc = [str(crew) for crew in modcrew.get()]
    print "printRuleFailures: %r" % mc
    Cui.CuiDisplayGivenObjects(Cui.gpc_info,
                               Cui.CuiScriptBuffer,
                               Cui.CrewMode,
                               Cui.CrewMode,
                               mc,
                               0)
    Cui.CuiSetCurrentArea(Cui.gpc_info, Cui.CuiScriptBuffer)
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiScriptBuffer, 'WINDOW')
    for _, crew, rulefailures in R.eval("default_context", R.foreach(
                                        R.iter("iterators.roster_set"), 
                                            "crew.%id%", 
                                            R.foreach(R.rulefailure())
                                        )
           )[0]:
        print "%s:" % crew
        for rf, in rulefailures:
            print "  %s:%s %s  (%s, %s)" % (rf.rule, rf.failtext, rf.failobject, rf.startdate, rf.deadline)
    