'''
Base class for validity reports

@author: rickard
'''
import carmensystems.rave.api as R
import carmensystems.publisher.api as prt
from report_sources.include.SASReport import SASReport
import Cui
from AbsDate import AbsDate
from AbsTime import AbsTime
from tm import TM
from sets import Set
from os import environ
import os.path
import time
from utils.performance import clockme

class ValidityReport(SASReport):
    """
    Abstract base class for validity reports.
    
    To implement a validity report, override createContents
    """
    def getPeriod(self):
        start,end = R.eval("fundamental.%pp_start%", "fundamental.%pp_end%")
        return (start, end)
        
    def getRosterFilter(self):
        filter = []
        filterStr = "Window"
        if self.arg("PLAN"):
            Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiNoArea, "PLAN")
            filterStr = "Plan"
        region = self.arg('REGION')
        if region and region != "ALL":
            filter.append('crew.%region%="'+region+'"')
            filterStr += " " + region
        cat = self.arg('MAINCAT')
        if cat and cat != "ALL":
            filter.append('fundamental.%main_cat%="'+cat[0]+'"')
            filterStr += " " + cat
        return (filterStr, filter)
        
    def createContents(self, boxes, raveFilter):
        """
        Example:
            prb = RosterProblemSet(filter=filter)
            boxes.head("Roster")
            boxes.add("Overlapping activities", prb.checkOverlaps())
            boxes.end()
        """
        raise NotImplementedError("Must override createContents")
    
    def getEnvironment(self):
        env = {}
        try:
            try:
                env['CARMUSR'] = os.path.realpath(environ['CARMUSR'])
            except:
                env['CARMUSR'] = ''
            try:
                env['CARMSYS'] = os.path.realpath(environ['CARMSYS'])
            except:
                env['CARMSYS'] = ''
                
            env['Period'] = "%s - %s" % R.eval("fundamental.%pp_start%", "fundamental.%pp_end%")
            env['Loaded per.'] = "%s - %s" % R.eval("fundamental.%loaded_data_period_start%", "fundamental.%loaded_data_period_end%")
            env['Region'] = "%s" % R.eval("planning_area.%filter_company_p%")
            env['Site'] = environ.get('SITE','Unknown') + " / " + environ.get("CARMCCSUBSITE", "")
            env['Database'] = environ.get('DB_URL','Not Defined')
            env['Creator'] = "%s @ %s %s" % (environ.get('USER',''), environ.get('HOST',''), time.ctime())
            if self.isReportWorker():
                env['App'] = "ReportWorker"
                env['Pubtype'] = self.getReportServerPublishType()
            else:
                env['App'] = "Studio"
        except:
            # Return the data 'so far'
            pass
        return env
    
    def isReportWorker(self):
        """
        Returns True if running in a report server, False otherwise.
        """
        try:
            import carmusr.application as application
            if application.isReportWorker: return True
            return False
        except ImportError, err:
            raise err
        
    def getReportServerPublishType(self):
        try:
            import carmensystems.common.reportWorker as reportWorker
            publishType = reportWorker.ReportGenerator().getPublishType()
            if not publishType:
                return ''
        except:
            return None
        
    def create(self):
        start,end = self.getPeriod()
        filterStr,filter = self.getRosterFilter()
        stt = start.split()
        ste = end.split()
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        interv = "%s %s" % (months[stt[1]-1],stt[0])
        if stt[0] != ste[0]:
            interv = "%s %s - %s %s" % (months[stt[1]-1],stt[0],months[ste[1]-1],ste[0])
        elif stt[1] != ste[1]:
            interv = "%s - %s %s" % (months[stt[1]-1],months[ste[1]-1],stt[0])

        SASReport.create(self, 'Problems in %s' % interv, showPlanData=False,
                         headerItems={"Filter: ": filterStr,
                                      "Period: ": interv})
        
        
        self.createContents(BoxMaker(self), filter)
        
        env = self.getEnvironment()
        if env:
            self.add(prt.Row(prt.Text("")))
            self.page()
            self.add(prt.Row(prt.Text("Environment"), font=prt.Font(size=12, weight=prt.BOLD)))
            r = prt.Row(background='#e5e5e5')
            r.add(prt.Column(prt.Text("Key", font=prt.Font(weight=prt.BOLD))))
            r.add(prt.Column(prt.Text("Value", font=prt.Font(weight=prt.BOLD))))
            self.add(prt.Row(prt.Text("")))
            self.add(r)
            for k in sorted(env.keys()):
                self.add(prt.Row(prt.Column(prt.Text(str(k))), prt.Column(prt.Text(str(env[k])))))
            
            
        #self.add(prt.Row(prt.Text("Crew tables"), font=prt.Font(size=12, weight=prt.BOLD)))
        #v = self.box("Table: per_diem_tax", prb.checkPer()) or v
        #if not v:
        #    self.add(prt.Row(prt.Text("No problems found"), font=prt.Font(size=10, weight=prt.BOLD, style=prt.ITALIC)))
                
                
class BoxMaker(object):
    colors = ('#ffffff', '#e5e5e5')
    def __init__(self, box):
        self.summary =  prt.Column(prt.Row(
            prt.Text("Summary"), font=prt.Font(size=12, weight=prt.BOLD)
            ))
        phd = prt.Row(background=self.colors[1])
        phd.add(prt.Column(prt.Text("Problems", font=prt.Font(weight=prt.BOLD))))
        phd.add(prt.Column(prt.Text("Region", font=prt.Font(weight=prt.BOLD))))
        self.summary.add(phd)
        self.box = box
        self.printSuccess = False
        self.inHead = False
        self.box.add(prt.Row(self.summary))
        self.clr = False
        self.colHeads = None
        
    def head(self, text):
        if self.inHead:
            self.end()
        self.printSuccess = True
        self.summary.add(prt.Row(prt.Text(text), font=prt.Font(style=prt.ITALIC), background=self.colors[1]))
        self.clr = False
        self.box.add(prt.Row(prt.Text("")))
        self.box.page()
        self.box.add(prt.Row(prt.Text(text), font=prt.Font(size=12, weight=prt.BOLD)))
        self.colHeads = None
        self.inHead = True
        
    def add(self, title, result):
        self.colHeads = None
        if result:
            #result.sort(cmp=lambda x,y:cmp(x.row(), y.row()))
            self.printSuccess = False
            sumrow = prt.Row()
            sumrow.add(prt.Column(prt.Text(str(len(result)), align=prt.RIGHT)))
            sumrow.add(prt.Column(prt.Text(title)))
            if len(result):
                if len(result) == 1:
                    title += " (1 problem)"
                else:
                    title += " (%d problems)" % len(result)
            
            self.box.add(prt.Row(prt.Text("")))
            self.box.page()
            self.box.add(prt.Row(prt.Text(title), font=prt.Font(size=10, weight=prt.BOLD, style=prt.ITALIC)))
            self.summary.add(sumrow)
            orw = None
            for prb in result:
                self.printSuccess = False
                self.box.page()
                hd = prb.header()
                if hd != self.colHeads:
                    self.colHeads = hd
                    self.box.add(prt.Row(prt.Text("")))
                    self._row(hd, bold=True, background=self.colors[1])
                    self.clr = False
                rw = prb.row()
                trw = rw
                if orw:
                    for i in range(len(rw)-1):
                        if i < len(orw):
                            if str(rw[i]) == str(orw[i]):
                                trw[i] = ''
                            else:
                                break
                orw = rw
                self._row(trw)
        
    def _row(self, vals, bold=False, background=None):
        if background == None:
            background = self._bgcolor()
        r = prt.Row(background=background)
        for col in vals:
            if bold:
                r.add(prt.Column(prt.Text(col, font=prt.Font(weight=prt.BOLD))))
            else:
                r.add(prt.Column(prt.Text(col)))
        
        self.box.add(r)
    def _bgcolor(self):
        color = self.colors[self.clr]
        self.clr = not self.clr
        return color
    
    def end(self):
        if self.inHead and self.printSuccess:
            self.box.add(prt.Row(prt.Text("No problems found"), font=prt.Font(size=10, weight=prt.BOLD, style=prt.ITALIC)))
        self.inHead = False
        self.printSuccess = False
        
        
class RosterProblemSet(object):
    def __init__(self, context="default_context", filter=None):
        self.context = context
        self.filter = filter
        
    @clockme
    def checkOverlaps(self):
        rv = []
        flt = self.filter[:]
        flt.append("studio_overlap.%roster_overlap%")
        v, = R.eval(self.context, R.foreach(R.iter("iterators.roster_set", where=tuple(flt)),
                                       "crew.%id%", "crew.%extperkey%", R.foreach(R.iter("iterators.leg_set", where="studio_overlap.%leg_overlap%"),
                                                                              "leg.%code%",
                                                                              "leg.%flight_nr%",
                                                                              "leg.%start_utc%",
                                                                              "leg.%end_utc%")))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]))
        for _, crewId, extPerKey, legs in v:
            i = 0
            while i < len(legs) - 1:
                cd1 = legs[i][1]
                cd2 = legs[i+1][1]
                if cd1 == "FLT": cd1 =legs[i][2]
                s1 = legs[i][3]
                e1 = legs[i][4]
                while i < len(legs) - 1:
                    i += 1
                    if cd2 == "FLT": cd2 =legs[i][2]
                    s2 = legs[i][3]
                    e2 = legs[i][4]
                    if s2 < e1:
                        s1str = s1.time_of_day()
                        rv.append(RosterProblem(extPerKey, "Overlap between %s (%s-%s) and %s (%s-%s)" % (cd1, s1.time_of_day(), e1.time_of_day(), cd2, s2.time_of_day(), e2.time_of_day()), key={'Date':AbsDate(s1)}))
                        cd1 = cd2
                        s1 = s2
                        e1 = e2
        return rv
        
    @clockme
    def checkMissingStations(self):
        rv = []
        flt = self.filter[:]
        flt += ["void(leg.%end_country%) or void(leg.%start_country%)"]
        v, = R.eval(self.context, R.foreach(R.iter("iterators.leg_set", where=tuple(flt)),
                                       "crew.%extperkey%", "leg.%start_date%", "default(leg.%flight_id%, leg.%code%)", "leg.%start_country%", "leg.%end_country%", "leg.%start_station%", "leg.%end_station%"))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]) or cmp(a[3], b[3]))
        for _, extPerKey, startDate, legCode, startCountry, endCountry, startStation, endStation in v:
            if not startCountry:
                rv.append(RosterProblem(extPerKey, "%s has unknown start station %s" % (legCode, startStation), key={'Date':AbsDate(startDate)}))
            if not endCountry:
                rv.append(RosterProblem(extPerKey, "%s has unknown end station %s" % (legCode, endStation), key={'Date':AbsDate(startDate)}))
                
        return rv
        
    @clockme
    def checkCrewOffInWrongBase(self,check_codes=("FRE","BL","VAC","SGD")):
        rv = []
        flt = self.filter[:]
        flt += [' or '.join(['leg.%%group_code%%="%s"' % x for x in check_codes])]
        
        flt += ["leg.%start_station% <> crew.%homeairport% and leg.%start_station_base% <> crew.%homeairport%"]
        v, = R.eval(self.context, R.foreach(R.iter("iterators.leg_set", where=tuple(flt)),
                                       "crew.%id%", "crew.%extperkey%", "leg.%start_date%", "leg.%code%", "leg.%start_station%", "crew.%homeairport%"))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]) or cmp(a[3], b[3]))
        for _, _, extPerKey, startDate, legCode, legStation, crewStation in v:
            rv.append(RosterProblem(extPerKey, "%s is in station %s, but crew stationed at %s" % (legCode, legStation, crewStation), key={'Date':AbsDate(startDate)}))
                
        return rv
        
    @clockme
    def checkTripLength(self):
        rv = []
        flt = self.filter[:]
        flt += ["trip.%has_only_flight_duty%", "trip.%time% > 9*24:00"]
        v, = R.eval(self.context, R.foreach(R.iter("iterators.trip_set", where=tuple(flt)),
                                       "crew.%id%", "crew.%extperkey%", "trip.%start_day%", "trip.%start_utc%", "trip.%end_utc%"))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]) or cmp(a[3], b[3]))
        for _, _, extPerKey, startDate, start, end in v:
            rv.append(RosterProblem(extPerKey, "Trip (%s-%s) unreasonably long" % (start, end), key={'Date':AbsDate(startDate)}))
                
        return rv
        
    @clockme
    def checkFullDayActivities(self):
        rv = []
        flt = self.filter[:]
        flt += ["not leg.%is_flight_duty%", "leg.%time% >= 22:00", "leg.%end_utc% > fundamental.%pp_start%", "leg.%start_utc% < fundamental.%pp_end%", "leg.%start_od% <> 0:00 or (leg.%end_od% <> 0:00 and leg.%end_od% <> 23:59)"]
        v, = R.eval(self.context, R.foreach(R.iter("iterators.leg_set", where=tuple(flt)),
                                       "crew.%id%", "crew.%extperkey%", "leg.%start_date%", "leg.%code%", "leg.%start_od%", "leg.%end_od%"))
        v.sort(cmp=lambda a,b: cmp(a[2], b[2]) or cmp(a[3], b[3]))
        for _, _, extPerKey, startDate, legCode, startTime, endTime in v:
            rv.append(RosterProblem(extPerKey, "%s has homebase times %s-%s" % (legCode, startTime, endTime), key={'Date':AbsDate(startDate)}))
                
        return rv
    
    def getCrew(self):
        v, = R.eval(self.context, R.foreach(R.iter("iterators.roster_set", where=tuple(self.filter)), 'crew.%id%'))
        return v
        
class TableProblemSet(object):
    @clockme
    def checkValidityDates(self, table, key, display=None, validfrom='validfrom', validto='validto', no_check_after_pp_end=False, isabsdate=True, can_equal=False, search=None, filter=None):
        combo = {}
        rv = []
        q = getattr(TM, table)
        if search:
            q = q.search(search)
        for r in q:
            if filter:
                if not filter(r): continue
            def getval(col):
                v = getattr(r, col)
                if hasattr(v, '_id'):
                    v = v._id
                return v
            k = tuple(map(getval, key))
            if not k in combo:
                combo[k] = []
            combo[k].append((getattr(r,validfrom), getattr(r,validto))) 
        for k in combo.keys():
            v = combo[k]
            errs = self._checkDateRange(v, no_check_after_pp_end=no_check_after_pp_end, isabsdate=isabsdate, can_equal=can_equal)
            if errs:
                rv.append(TableProblem(table, errs, dict(zip(key,k)))) 
        return rv
    
    @clockme
    def checkKeys(self, table, search=None, filter=None):
        combo = {}
        rv = []
        q = getattr(TM, table)
        ed = q.entityDesc()
        key = {}
        for i in range(ed.keysize()):
            key[ed.keyfieldname(i)] = ed.keytype(i)
            
        if search:
            q = q.search(search)
        for r in q:
            if filter:
                if not filter(r): continue
            
            def getval(col):
                if key[col] == 10:
                    return (col, str(r.getRefI(col)).strip())
                return (col, str(getattr(r, col)).strip())
            
            k = dict(tuple(map(getval, key)))
            for kn in key:
                kt = key[kn]
                if kt == 8:
                    s = getattr(r, kn)
                    if s != s.strip():
                        rv.append(TableProblem(table, "Key field %s starts/ends with whitespace" % kn, k))
                else:
                    try:
                        s = getattr(r, kn)
                    except:
                        rv.append(TableProblem(table, "Reference violation on %s=%s" % (kn, k[kn]), k))
           
        return rv
                
    def _checkDateRange(self, dates, no_check_after_pp_end=False, isabsdate=True, can_equal=False, allow_gaps=False):
        d, = R.eval("fundamental.%now%")
        imin = int(d) - 60*1440
        imax = int(d) + 60*1440
        if no_check_after_pp_end:
            imax = int(R.eval("fundamental.%pp_end%")[0])
        if isinstance(dates[0], list):
            dates = tuple(dates)
        if not isinstance(dates[0], tuple):
            raise ValueError("Expected list of tuples of dates")
        if isabsdate == None:
            if isinstance(dates[0][0], AbsDate):
                isabsdate = True
            elif isinstance(dates[0][0], AbsTime):
                isabsdate = False
            else:
                raise ValueError("Invalid date type %s" % str(type(dates[0])))
        if isabsdate:
            idates = [(int(x[0])/1440, int(x[1])/1440) for x in dates]
            strf = lambda x: AbsDate(x*1440)
            imin /= 1440
            imax /= 1440
        else:
            idates = [(int(x[0]), int(x[1])) for x in dates]
            strf = AbsTime
        idates.sort()
        vld = None
        for i in range(len(idates)):
            s,e = idates[i]
            if i > 0:
                if e < s:
                    return "Inverted date range %s-%s" % (strf(s), strf(e))
                if can_equal and s < idates[i-1][1] or not can_equal and s <= idates[i-1][1]:
                    return "Overlap in interval %s-%s" % (strf(s), strf(idates[i-1][1]))
                elif not not allow_gaps and s > idates[i-1][1]+1:
                    return "Gap in interval %s-%s" % (strf(idates[i-1][1]+1), strf(s-1))
                    
                if not allow_gaps and i == len(idates)-1:
                    if e < imax:
                        vld = "No validity exists after %s" % strf(e)
            else:
                if not allow_gaps and s > imin:
                    vld = "No validity exists before %s" % strf(s)
        
        return vld

class Problem(object):
    def __str__(self):
        return "<Problem>"
    def __repr__(self):
        return self.__str__()
        
    def header(self):
        return ["Problem"]
    
    def row(self):
        return [str(self)]

class TableProblem(Problem):
    colnames = {'crew_id':'Crew'}
    def __init__(self, tablename, message, key=None):
        self.tablename = tablename
        self.message = message
        self.key = key
        
    def trans(self, k):
        if k in TableProblem.colnames:
            return TableProblem.colnames[k]
        return ' '.join([x[0].upper() + x[1:] for x in k.split('_')])
        
    def header(self):
        if self.key:
            return [self.trans(x) for x in sorted(self.key.keys())] + ["Problem"]
        return ["Problem"]
        
    def row(self):
        if self.key:
            return [self.key[x] for x in sorted(self.key.keys())] + [self.message]
        return [self.message]
        
    def __str__(self):
        return self.message

class RosterProblem(Problem):
    def __init__(self, extperkey, message, leg=None, key=None):
        self.extperkey = extperkey
        self.message = message
        self.leg = leg
        self.key = key
        
    def header(self):
        rv = ["Crew"]
        if self.key: rv += self.key.keys() 
        rv.append("Problem")
        return rv
        
    def row(self):
        rv = [self.extperkey]
        if self.key: rv += self.key.values()
        rv.append(self.message)
        return rv
        
    def __str__(self):
        return "%s: %s" % (self.extperkey, self.message)
        
