'''
Created on May 7, 2010

@author: rickard
'''


from carmtest.framework import *

class system_010_Selection(MacroTestFixture):
    "GUI: Selection"
    
    @REQUIRE("PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test_001_SelectSingleCrew(self):
        crew = list(self.getCrew(max_crew=100).keys())
        crew = crew[-1]
        self.log("Selecting crew %s" % crew)
        self.select(area=0, crew=crew)
        sel = list(self.getCrewInWindow(0).keys())
        assert len(sel) == 1, "Expected 1 crew to be selected, found %d" % len(sel)
        assert sel[0] == crew, "Expected crew %s, found crew %s" % (crew, sel[0])

    def test_002_SelectSingleCrewCommandLine(self):
        macro ="""<?xml version="1.0" encoding="UTF-8"?>
            <All>
                <Command 
                    label="Commandline/SelectCrew" 
                    script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_crew((Cui.CuiArea0, &apos;&apos;), (&apos;CREW&apos;, &apos;&apos;, &apos;r&apos;))&quot;)" 
                    level="0">
                    <CommandAttributes label="Commandline/SelectCrew"
                        script="PythonEvalExpr(&quot;carmusr.tracking.CommandlineCommands.show_crew((Cui.CuiArea0, &apos;&apos;), (&apos;CREW&apos;, &apos;&apos;, &apos;r&apos;))&quot;)"
                        level="0" returnVal="0" />
                </Command>
            </All>"""
        crew = list(self.getCrew(max_crew=100).keys())
        crew = crew[-2]
        self.log("Selecting crew %s" % crew)
        self.run_macro(macro, {'CREW':crew})
    
        sel = list(self.getCrewInWindow(0).keys())
        assert len(sel) == 1, "Expected 1 crew to be selected, found %d" % len(sel)
        assert sel[0] == crew, "Expected crew %s, found crew %s" % (crew, sel[0])