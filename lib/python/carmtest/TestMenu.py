

"""
Create context sensitive dynamic test menus. The test menu will both contain
tests defined in usual menu-files as well as a dynamic list of available
'unittests'.

@author: rickard
modified: [acosta:10/089@14:18]
"""

import utils.mnu # Needed
import utils.mnu as mnu
import os
import sys
import carmtest.framework.TestFunctions as TF

from carmtest.framework import TestFixture


__all__ = ['install', 'uninstall']
__version__ = r'$Revision: 1.7 $'

# Keep a handle to avoid garbage collection
unit_tests = None

# Should be unique
test_menu_id = 'DynTestMenu001'


class RunTheTest:
    """Button action: Run single test or all tests in package."""
    def __init__(self, cat, module=None, test=None):
        self.cat = cat
        self.module = module
        self.test = test

    def __call__(self, *a, **k):
        TF.run_tests(self.cat, self.module, self.test)


class SubUnitTestMenu(mnu.Menu):
    """Sub menu for test package."""
    def __init__(self, cat):
        component = cat[5:].capitalize()
        self.cat = cat
        self.component = component
        mnu.Menu.__init__(self, cat, title=component)
        self.refresh()
        
    def refresh(self):
        del self[:]
        unittests = self.get_tests(self.cat)
        if unittests:
            self.append(mnu.Title('Tests in %s' % self.component))
            self.append(mnu.Separator())
            self.append(mnu.Button(title='Run all tests', action=RunTheTest(self.cat), mnemonic='_R'))
            self.append(mnu.Separator())
        else:
            self.append(mnu.Title('-> No tests found.'))
        self.extend(unittests)
        
    def __call__(self):
        self.refresh()
        mnu.Menu.__call__(self)

    def get_tests(self, cat):
        L = []
        for t in TF.list_tests(cat):
            tname = '???'
            if issubclass(t, TestFixture):
                try:
                    tname = t.__name__
                    tmod = t.__module__.split('.')[-1]
                    try:
                        tlabel = t.__doc__.strip()
                    except:
                        tlabel = tmod
                    # will raise exception if test not available
                    t.available()
                    L.append(mnu.Button(title=tlabel, action=RunTheTest(cat, tmod, tname)))
                except Exception, e:
                    L.append(mnu.Title("%s (Error: %s)" % (tname, e)))
        return L


class UnitTestMenu(mnu.Menu):
    """Menu named 'UnitTests' is defined in menu sources (Tests.menu)"""
    def __init__(self):
        mnu.Menu.__init__(self, 'UnitTests', title='Unit Tests', mnemonic='_U')

    def __call__(self):
        """Modifying the list of menu items before attaching."""
        self[:] = [mnu.Title('Unit Tests'), mnu.Separator()]
        self.extend([SubUnitTestMenu(c) for c in TF.list_categories()])
        mnu.Menu.__call__(self)


def install():
    """Create unit test menu and attach pre-defined test menus."""
    global unit_tests
    import carmstd.rpc as rpc
    unit_tests = UnitTestMenu()
    plan = mnu.Menu('TestPlan', title='Test', mnemonic='_T', identifier=test_menu_id)
    plan.attach('TOP_MENU_BAR')
    co = mnu.Menu('TestCrewObject', title='Test', mnemonic='_T', identifier=test_menu_id)
    co.attach('LeftDat24CrewCompMode1')
    ao = mnu.Menu('TestAssignmentObject', title='Test', mnemonic='_T', identifier=test_menu_id)
    ao.attach('MainDat24CrewCompMode1')
    ag = mnu.Menu('TestAssignmentGeneral', title='Test', mnemonic='_T', identifier=test_menu_id)
    ag.attach('MainDat24CrewCompMode2')
    rpcmon = mnu.Title("RPC: %s" % rpc.rpc_server(), identifier=test_menu_id)
    rpcmon.attach('TOOL_BAR')

    os.environ["TEST_MENUS_ACTIVE"] = "1"
    def openTestPlan():
        import carmusr.tracking.OpenPlan as O
        O.loadReportWorkerPlan()
    def openCrewPlan():
        import carmusr.tracking.OpenPlan as O
        O.loadSingleCrewPlan()

    openrpt = mnu.Button(title="Open report worker plan...", action=openTestPlan)
    openrpt.attach("FileMenu", after="Open")
    opencrew = mnu.Button(title="Open specific crew...", action=openCrewPlan)
    opencrew.attach("FileMenu", after="Open")


def uninstall():
    """Remove test menus."""
    for top_menu in ('TOOL_BAR', 'TOP_MENU_BAR', 'LeftDat24CrewCompMode1',
            'MainDat24CrewCompMode1', 'MainDat24CrewCompMode2'):
        mnu.delete(top_menu, identifier=test_menu_id)


if __name__ == '__main__':
    # Add the test menus
    install()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
