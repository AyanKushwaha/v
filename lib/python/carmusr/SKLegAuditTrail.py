import carmensystems.studio.plans.LegAuditTrail as CarmsysLegAuditTrail
import Cui
import traceback
import carmensystems.rave.api as R

class NeedPresentator(CarmsysLegAuditTrail.Presentator):
    """
    Presentation object for crew_need_exception
    """
    def present(self, changeType, column, old, new):
        dict = {'pos6': 'AS',
                'pos7': 'AH'}
        if dict.has_key(column):
            columnDesc = 'Extra %s service need' % (dict[column])
            if old:
                old = self.valueToStr(old)
            if new:
                new = self.valueToStr(new)
            return self.presentDefault(changeType, columnDesc, old, new)
        else:
            return CarmsysLegAuditTrail.Presentator.present(self, changeType, column, old, new)

    def valueToStr(self, val):
        if val == -1:
            return "Default extra service need"
        else:
            return str(val)


class SimExcPresentator(CarmsysLegAuditTrail.Presentator):
    """
    Presentation object for ground_task_attr:SIM EXC
    """
    def present(self, changeType, column, old, new):
        if column == "value_int":
            columnDescr = "Crew need exc"
            if old is not None:
                old = self.getNeedRepr(old)
            if new is not None:
                new = self.getNeedRepr(new)
        else:
            columnDescr = "Briefings exc"
            if old is not None:
                old = self.getBriefRepr(old)
            if new is not None:
                new = self.getBriefRepr(new)
        return self.presentDefault(changeType, columnDescr, old, new)
        
    def getNeedRepr(self, val):
        (fc, fp, fr, tl, tr) =  R.eval("leg.%%_sim_need_fc%%(%s)" %val,
                                       "leg.%%_sim_need_fp%%(%s)" %val,
                                       "leg.%%_sim_need_fr%%(%s)" %val,
                                       "leg.%%_sim_need_tl%%(%s)" %val,
                                       "leg.%%_sim_need_tr%%(%s)" %val)
        out = "%s/%s/%s/.../%s/%s" %(fc, fp, fr, tl, tr)
        return out

    def getBriefRepr(self, val):
        (brief, midbrief, debrief) = R.eval("leg.%%_sim_brief_exc%%(%s)" %val,
                                            "leg.%%_sim_midbrief_exc%%(%s)" %val,
                                            "leg.%%_sim_debrief_exc%%(%s)" %val)
        out = "%s/%s/%s" %(brief, midbrief, debrief)
        return out
        
class SKAuditDomainFactory(CarmsysLegAuditTrail.AuditDomainFactory):
    """
    SAS Specific extentions to what and how audit trail on legs should be handled
    """
    def __init__(self):
        CarmsysLegAuditTrail.AuditDomainFactory.__init__(self)
        
    def getAuditDomain(self, area=Cui.CuiWhichArea):
        """
        CARMUSR wrapping change the column sort order
        """
        presentators, presentationName, crewConnectionEntity = CarmsysLegAuditTrail.AuditDomainFactory.getAuditDomain(self, area)
        for presentator in presentators:
            presentator.setSortMethod(CarmsysLegAuditTrail.Presentator.SORT_DESCRIPTION)
        return presentators, presentationName, crewConnectionEntity
            
    def getFlight(self, area, areaMode, crew):
        """
        Adds audit trail on crew_need_exception as well
        """
        presentators, presentationName, crewConnectionEntity = CarmsysLegAuditTrail.AuditDomainFactory.getFlight(self, area, areaMode, crew)
        # Assumption: We only perform the audit trail on a single leg
        if presentators and presentators[0]:
            results = self.search("crew_need_exception", {'flight_udor':int(presentators[0].pk['udor']),
                                                          'flight_fd':str(presentators[0].pk['fd']),
                                                          'flight_adep':str(presentators[0].pk['adep'])})
            if results:
                for (entityI, pk) in results:
                    presentators.append(NeedPresentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity

    def getGroundDuty(self, area, areaMode, crew, activityType):
        """
        Adds audit trail on crew_need_exception as well
        """
        presentators, presentationName, crewConnectionEntity = CarmsysLegAuditTrail.AuditDomainFactory.getGroundDuty(self, area, areaMode, crew, activityType)
        # Assumption: We only perform the audit trail on a single leg
        if presentators and presentators[0]:
            results = self.search("ground_task_attr", {'task_udor':int(presentators[0].pk['udor']),
                                                       'task_id':str(presentators[0].pk['id']),
                                                       'attr':'SIM EXC'})
            
            if results:
                for (entityI, pk) in results:
                    presentators.append(SimExcPresentator(entityI, pk))
        return presentators, presentationName, crewConnectionEntity
    
# Entry point for Leg based audit trails
# Use our SKAuditDomainFactory
def Show(area=Cui.CuiWhichArea):
    auditTrail = CarmsysLegAuditTrail.LegAuditTrail(SKAuditDomainFactory(), area)
    auditTrail.run()
    
