
"""
import carmusr.tracking.handover_report
reload(carmusr.tracking.handover_report)
carmusr.tracking.handover_report.run()
"""
import traceback

import modelserver as M
import carmensystems.services.dispatcher
from AbsTime import AbsTime
import utils.Names as Names
from tm import TM, TempTable
import utils.wave

utils.wave.register()

HRH = None
MSG_TBL = None
SETTINGS_TBL = None
MAINCAT_SET = None
REGION_SET = None
HAUL_SET = None
UNIT_SET = None

    
def initialize_module(*args):
    """
    This function will be called from the <on-loaded> section in the Wave
    form (handover_report.xml). This is possible beacuse it's registered as
    a service (carmensystems.mirador.tablemanager.handover_initialize_module).
    
    Please note that an implicit 'refreshClient()' action is performed in the
    Wave form invoking this function via
      'model(carmensystems.mirador.tablemanager.handover_initialize_module)'
    
    From Studio, the form is started via:
        StartTableEditor.StartTableEditor(
            ['-fs', '$CARMUSR/data/form/handover_report.xml'])
    """
    
    global MAINCAT_SET, REGION_SET, HAUL_SET, UNIT_SET
    global MSG_TBL, SETTINGS_TBL
    global HRH
    
    print "********************************************************************"
    print "handover_report: initialize_module",args
    
    if HRH is not None:
        print "handover_report: Already initialized"
        print "********************************************************************"
        return False
        
    MAINCAT_SET =  HandoverMaincatSet()
    REGION_SET =   TM.crew_region_set
    HAUL_SET =     HandoverHaulSet()
    UNIT_SET =     HandoverUnitSet()
    SETTINGS_TBL = HandoverSettingsTable()
    MSG_TBL =      HandoverMessageTable()
    print "handover_report: Created tables"

    HRH = HandoverReportHandler()
    print "handover_report: Created handler instance"
        
    carmensystems.services.dispatcher.registerService(HRH.refresh,
        "carmensystems.mirador.tablemanager.handover_refresh")
    carmensystems.services.dispatcher.registerService(HRH.save,
        "carmensystems.mirador.tablemanager.handover_save")
    carmensystems.services.dispatcher.registerService(HRH.createrow,
        "carmensystems.mirador.tablemanager.handover_createrow")
    carmensystems.services.dispatcher.registerService(HRH.generate,
        "carmensystems.mirador.tablemanager.handover_generate")
    print "handover_report: Registered services"
        
    print "********************************************************************"

carmensystems.services.dispatcher.registerService(initialize_module,
    "carmensystems.mirador.tablemanager.handover_initialize_module")


class HandoverReportHandler(object):
    """
    Main Form handler
    """
            
    def refresh(self, *args):
        print "HandoverReportHandler::refresh", args[1:]  
        if utils.wave.STANDALONE:
            TM.refresh()
        utils.wave.refresh_wave_values()
        MSG_TBL.refresh()
            
    def save(self, *args):
        print "HandoverReportHandler::save", args
        utils.wave.refresh_wave_values()
        if utils.wave.STANDALONE:
            is_dirty = False
            TM.newState()
            try:
                is_dirty = MSG_TBL.save()
                if is_dirty:
                    TM.save()
            finally:
                if not is_dirty:
                    TM.undo()
        else:
            MSG_TBL.save()
        MSG_TBL.refresh()
            
    def createrow(self, *args):
        print "HandoverReportHandler::createrow", args
        utils.wave.refresh_wave_values()
        MSG_TBL.createrow()        
        
    def generate(self, *args):
        if utils.wave.STANDALONE:
            raise Exception("Running in non-STUDIO mode, report not available")
            
        utils.wave.refresh_wave_values()
        filter = (("REGION=%s "   % (SETTINGS_TBL.v.region.id)) +
                  ("CATEGORY=%s " % (SETTINGS_TBL.v.main_category.id)) +
                  ("HAUL=%s "     % (SETTINGS_TBL.v.long_short_haul.id)) +
                  ("AVVDISP=%s "  % (SETTINGS_TBL.v.avv_disp.id)) +
                  ("NUMDAYS=%s"   % (SETTINGS_TBL.v.days - 1))
                  ) 
        print "HandoverReportHandler::generate:", filter
        import Cui
        Cui.CuiCrgDisplayTypesetReport(
            Cui.gpc_info,
            Cui.CuiNoArea,
            "plan",
            '/report_sources/hidden/HandoverReport.py',
            0,
            filter)

            
class HandoverMaincatSet(TempTable):
    __name = 'tmp_handover_maincat_set'
    __keys = [M.StringColumn('id','')]
    __cols = [M.StringColumn('name','')]
    def __init__(self):
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        if not len(self):
            self.create(("ALL",)).name = "Cabin Crew and Flight Deck"
            self.create(("CC",)).name  = "Cabin Crew"
            self.create(("FC",)).name  = "Flight Deck"


class HandoverHaulSet(TempTable):
    __name = 'tmp_handover_haul_set'
    __keys = [M.StringColumn('id','')]
    __cols = [M.StringColumn('name','')]
    def __init__(self):
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        if not len(self):
            self.create(("BOTH",)).name = "Longhaul and Shorthaul"
            self.create(("LONG",)).name = "Longhaul"
            self.create(("SHORT",)).name = "Shorthaul"


class HandoverUnitSet(TempTable):
    __name = 'tmp_handover_unit_set'
    __keys = [M.StringColumn('id','')]
    __cols = [M.StringColumn('name','')]
    def __init__(self):
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        if not len(self):
            self.create(("BOTH",)).name = "Tracking and Roster Maintenance"
            self.create(("TRACKING",)).name = "Tracking"
            self.create(("MAINTENANCE",)).name = "Roster Maintenance"


class HandoverSettingsTable(TempTable):
    """
    Temporary table for settings used in the Wave Form.
    Contains one entry only.
    """
    __name = 'tmp_handover_settings'
    __keys = [M.IntColumn('id','')]
    __cols = [M.RefColumn('main_category','tmp_handover_maincat_set',''),
              M.RefColumn('region','crew_region_set',''),
              M.RefColumn('long_short_haul','tmp_handover_haul_set',''),
              M.RefColumn('avv_disp','tmp_handover_unit_set',''),
              M.IntColumn('days', ''),
             ]
             
    def __init__(self):
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        try:
            self.v = self.create((0,))
        except:
            self.v = self[(0,)]
        self.v.main_category = MAINCAT_SET[("ALL",)]
        self.v.region = REGION_SET[("SKD",)]
        self.v.long_short_haul = HAUL_SET[("BOTH",)]
        self.v.avv_disp = UNIT_SET[("BOTH",)]
        self.v.days = 1
                   
    def search_ldap(self):
        return "(&" \
             + self._region_search_ldap() \
             + self._maincat_search_ldap() \
             + self._haul_search_ldap() \
             + self._unit_search_ldap() \
             + "(|(valid_day>=%s)(validto>=%s))" \
                % (tmstr(utils.wave.get_now_date_utc(), date_only=True),
                   tmstr(utils.wave.get_now_utc())) \
             + ")"
            
    def _region_search_ldap(self):
        if self.v.region.id == "SKI":
            return "(region=SKI)"
        return "(|(region=%s)(region=SKI))" % self.v.region.id
            
    def _maincat_search_ldap(self):
        if self.v.main_category.id == "ALL":
            return ""
        return "(|(main_category=%s)(main_category=ALL))" \
                   % self.v.main_category.id
            
    def _haul_search_ldap(self):
        if self.v.long_short_haul.id == "BOTH":
            return ""
        return "(|(long_short_haul=%s)(long_short_haul=BOTH))" \
                   % self.v.long_short_haul.id
            
    def _unit_search_ldap(self):
        if self.v.avv_disp.id == "BOTH":
            return ""
        return "(|(avv_disp=%s)(avv_disp=BOTH))" \
                   % self.v.avv_disp.id     

class HandoverMessageTable(TempTable):
    """
    Temporary table for 'handover_message' db entries corresponding
    to the current settings in the Wave Form.
    
    The settings is kept in HandoverSettingsTable.
    """
    __name = 'tmp_handover_message'
    __keys = [M.UUIDColumn('id', '')]
    __cols = [M.DateColumn('valid_day', ''),
              M.TimeColumn('validto', ''),
              M.StringColumn('free_text', ''),
              M.BoolColumn('new_', ''),
              M.BoolColumn('removed_', ''),
             ]
                     
    def __init__(self):
        TempTable.__init__(self, self.__name, self.__keys, self.__cols)
        
    def refresh(self):
        self.removeAll()
        ldap = SETTINGS_TBL.search_ldap()
        print "HandoverMessageTable::refresh",ldap
        for row in TM.handover_message.search(ldap):
            trow = self.create((row.id,))
            trow.valid_day = row.valid_day             
            trow.validto  = row.validto              
            trow.free_text = row.free_text  
            trow.new_      = False
            trow.removed_  = False
            
    def save(self):
        is_dirty = False
        for row in self:
            if row.removed_:
                if not row.new_:
                    try:
                        print "::REMOVE",row
                        TM.handover_message[(row.id,)].remove()
                        is_dirty = True
                        row.removed_ = False
                        row.new_     = False
                    except:
                        print "handover_report::HandoverMessageTable::save:", \
                              "Removed row not found", row
            elif row.new_:
                print "::CREATE",row
                try:
                    new = TM.handover_message.create((row.id,))
                    is_dirty = True
                    new.main_category   = SETTINGS_TBL.v.main_category.id
                    new.region          = SETTINGS_TBL.v.region
                    new.long_short_haul = SETTINGS_TBL.v.long_short_haul.id
                    new.avv_disp        = SETTINGS_TBL.v.avv_disp.id
                    new.valid_day       = row.valid_day             
                    new.validto        = row.validto
                    new.free_text       = (row.free_text or "").strip()
                    new.created_by   = Names.username()
                    new.created_time = utils.wave.get_now_utc()
                    row.removed_ = False
                    row.new_     = False
                except:
                    traceback.print_exc()
                    print "handover_report::HandoverMessageTable::save:", \
                          "Failed to create", row
            else:
                try:
                    old = TM.handover_message[(row.id,)]
                    for attr in ('valid_day', 'validto', 'free_text'):
                        old_value = getattr(old, attr)
                        new_value = getattr(row, attr)
                        if str(old_value) != str(new_value):
                            print "::UPDATE",attr,"FOR",row
                            if attr == 'free_text':
                                setattr(old, attr, (new_value or "").strip())
                            else:
                                setattr(old, attr, new_value)
                            is_dirty = True
                            old.edited_by = Names.username()
                            old.edited_time = utils.wave.get_now_utc()
                except:
                    traceback.print_exc()
                    print "handover_report::HandoverMessageTable::save:", \
                          "Failed to update", row
                    
        if is_dirty and not utils.wave.STANDALONE:
            import Cui
            Cui.CuiReloadTable("handover_message", Cui.CUI_RELOAD_TABLE_SILENT)

        return is_dirty
            
    def createrow(self):
        row = self.create((TM.createUUID(),))
        row.new_     = True
        row.removed_ = False
        row.valid_day = utils.wave.get_now_date_utc()
        
############################ Utilities & helper functions ######################

def tmstr(date_or_time, date_only=False):
    (yyyy, mm, dd, HH, MM) = AbsTime(date_or_time).split()
    if date_only:
        return "%04d%02d%02d" % (yyyy, mm, dd)
    else:
        return "%04d%02d%02d %02d:%02d" % (yyyy, mm, dd, HH, MM)

