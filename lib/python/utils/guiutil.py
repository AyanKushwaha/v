

import Cui
import Gui
import utils.selctx

class UpdateManager(object):
    _dirty_tables = set()
    _gui_change = False
    _started = 0
    # CuiReloadTable, TM.refresh() and similar only allowed in Studio mode.
    _isStudio = not utils.selctx.BasicContext().isRS
    
    @classmethod
    def start(cls):
        cls._dirty_tables = set()
        cls._gui_change = False
        cls._started = 1
        
    @classmethod
    def setDirtyTable(cls, table):
        cls._dirty_tables.add(table)
        cls._gui_change = cls._isStudio
        
    @classmethod
    def setGuiChange(cls):
        cls._gui_change = cls._isStudio
        
    @classmethod
    def done(cls, noguiupdate=False):
        if not cls._started:
            return False
        else:
            cls._started = 0
            for t in list(cls._dirty_tables):
                if cls._isStudio:
                    Cui.CuiReloadTable(t)
                cls._dirty_tables.remove(t)
            if cls._gui_change and not noguiupdate:
                Gui.GuiCallListener(Gui.RefreshListener, "parametersChanged")
                Gui.GuiCallListener(Gui.ActionListener)
            return cls._dirty_tables or cls._gui_change

