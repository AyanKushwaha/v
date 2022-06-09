import os
from time import strftime
from utils.TimeServerUtils import now
from RelTime import RelTime
import carmensystems.rave.api as R
from cPickle import dumps
from carmensystems.common.Config import Config as C
from AbsTime import AbsTime
from RelTime import RelTime
from utils.selctx import BasicContext


class Archiver(object):
    """ Base class for archivers """
    
    def __init__(self, archive_dir, archive_type, report_name, report_module):
        """ @param archvie_dir - the archive directory
            @param archive_type - the archvie type 
            @param report_name - the name of the report
            @param report_module - the path the report python module
        
        """
        self.archive_dir = archive_dir
        self.archive_type = archive_type
        self.report_name = report_name
        self.report_module = self.import_module(report_module)
        self.sym_link = None
        

    def import_module(self, report_module):
        """ Imports a python module and returns a handle to that module
            @param report_module - the path the report module
         
        """
        
        RPT = None
        try:
            exec "import %s as RPT" % (report_module)
        except ImportError:
            import traceback
            traceback.print_exc()
            raise ValueError, "Crewlist report '%s' does not exist" % (report_module)
        print RPT
        #reload(RPT)
        if not hasattr(RPT, "archive"):
            raise ValueError, "Crewlist report '%s' is not archiveable" % (report_module)
        
        return RPT

    def create_archive_dir(self, date):
        """ Creates an arvhive dir for this specifiec report. The archive dir is on the
            following form {archice_dir}/{archive_type}.{report_name}.{current date}
            
            @param date - 
            @return archive - directory and link 
        
        """
        
        # Create the archive directory
        report = "%s.%s" % (self.archive_type, self.report_name)
        
        y,m,_,_,_ = date.split()
        keydate = "%04d/%02d" % (y, m)
            
        # The actual path
        dir_name= "%s." % (report) + strftime("%Y%m%d_%H%M%S") 
        fpath = fpath0 = os.path.join(self.archive_dir, keydate, dir_name)
            
        # A symlink name, the symlink is used to get an atomic creation
        # the archive files
        self.sym_link = os.path.join(self.archive_dir, keydate, "%s.current" % report)

        i = 0
        while os.path.exists(fpath):
            i += 1
            fpath = "%s.%d" % (fpath0,i)
        
        print "MakingDirs", fpath
        os.makedirs(fpath)

        return fpath
    
    def create_sym_link(self, fpath):
        """ Creates a sym link to the path argument """
        
        if self.sym_link is None:
            raise Exception, "No valid symlink"
        
        if os.path.exists(self.sym_link): 
            os.unlink(self.sym_link)
        os.symlink(fpath.split("/")[-1], self.sym_link)


class MonthlyCrewArchiver(Archiver): 
    """ Class used for archiving crew reports where a report is a month """
        
    def __init__(self, archive_dir, archive_type, report_name, report_module):
        super(MonthlyCrewArchiver, self).__init__(archive_dir, archive_type, report_name, report_module)
    
            
    def archive(self, firstdate, lastdate, base, maincat, rank):
        """ This functions is used to archive reports that are done per crew and month. This means that there will be one 
            report per crew and month i.e. the crew roster will for a whole month and when requesting this in the crew portal
            the complete month will be shown regardless of the input date. E.g. 6Feb2012 will show the roster for Feb2012.
    
        """
    
        where = []
        where.append("not (crew.%%is_inactive_at_date%%(%s) and crew.%%is_inactive_at_date%%(%s))" % (firstdate, lastdate))
        
        if base:
            where.append("default(crew.%%base_at_date%%(%s),crew.%%base_at_date%%(%s))=%s" % (firstdate, lastdate, base))
        if maincat:
            where.append("crew.%%main_func%%=%s" % (maincat))
        if rank:
            where.append("default(crew.%%rank_at_date(%s)%%,crew.%%rank_at_date(%s)%%)=%s" % (firstdate, lastdate, maincat))
        
        crew = [(id,perkey) for _,id,perkey 
                in R.eval("sp_crew", R.foreach(R.iterator("iterators.roster_set"), "crew.%id%","default(crew.%%extperkey_at_date%%(%s),crew.%%extperkey_at_date%%(%s))" % (firstdate, lastdate), where=where))[0] 
                if perkey]
    
        ret = self.report_module.archive(crew, firstdate, lastdate)
            
        if not ret:
            raise Exception, "No response from report"

        fpath = self.create_archive_dir(firstdate)
                     
        print "Creating %d files for %s" % (len(ret), report)
        for id, v in ret.items():
            file(os.path.join(fpath,"%s.xml" % id),"w").write(v)
    
        self.create_sym_link(fpath)
    
class DailyCrewArchiver(Archiver): 
    """ Class used for archiving crew reports where a report is a day """
        
    def __init__(self, archive_dir, archive_type, report_name, report_module):
        super(DailyCrewArchiver, self).__init__(archive_dir, archive_type, report_name, report_module)
    

    def archive(self, firstdate, lastdate):
        """ This functions is used to archive reports that are done per flight. The archiving is
            usually done for a whole month but the files will be kept per day.
        
        """
        
        fpath = self.create_archive_dir(firstdate)
        
        # We are looping each day in the period
        currentdate = firstdate
        while currentdate < lastdate:
            
            where = []
            where.append("not crew.%%is_inactive_at_date%%(%s)" % (currentdate))
        
            crew = [(id,perkey) for _,id,perkey 
                        in R.eval("sp_crew", R.foreach(R.iterator("iterators.roster_set"), "crew.%id%","crew.%%extperkey_at_date%%(%s)" % (currentdate), where=where))[0] 
                        if perkey]

    
            ret = self.report_module.archive(crew, currentdate)
            
            if not ret:
                raise Exception, "No response from report"
                
            if ret:
                _,_,d,_,_ = currentdate.split()
                day_path = os.path.join(fpath, "%02d" % (d))
                print "MakingDirs", day_path
                os.makedirs(day_path)
            
                print "Creating %d files for %s" % (len(ret), report)
                for crew_id, v in ret.items():
                    file(os.path.join(day_path,"%s.xml" % crew_id),"w").write(v)
            else:
                print "No archiving done for ", currentdate
                    
            currentdate = currentdate.adddays(1)
            
        self.create_sym_link(fpath)
        

class DailyActivityArchiver(Archiver):
    """ Class used for archiving flight reports where a report is a day """

    def __init__(self, archive_dir, archive_type, report_name, report_module):
        super(DailyActivityArchiver, self).__init__(archive_dir, archive_type, report_name, report_module)

    def archive(self, firstdate, lastdate):
        """ This functions is used to archive reports that are done per flight. The archiving is
            usually done for a whole month but the files will be kept per day.

        """

        fpath = self.create_archive_dir(firstdate)

        # We are looping each day in the period
        currentdate = firstdate
        while currentdate < lastdate:

            where = ("report_crewlists.%crewlist_allowed%",
                     "report_crewlists.%%activity_udor%% = %s" % (currentdate))

            bc = BasicContext()

            rave_result,  = R.eval(bc.getGenericContext(), R.foreach(R.iter("report_crewlists.activity_set", where=where),
                                                                     "report_crewlists.%activity_id%",
                                                                     "report_crewlists.%activity_udor%"))

            # Create a list of tuples
            activities = [(activity_id, udor) for _, activity_id, udor  in rave_result]

            ret = self.report_module.archive(activities)

            if ret:
                _,_,d,_,_ = currentdate.split()
                day_path = os.path.join(fpath, "%02d" % (d))
                print "MakingDirs", day_path
                os.makedirs(day_path)

                print "Creating %d files for %s" % (len(ret), report)
                for activity_id, v in ret.items():
                    file(os.path.join(day_path,"%s.xml" % activity_id),"w").write(v)
            else:
                print "No archiving done for ", currentdate

            currentdate = currentdate.adddays(1)

        self.create_sym_link(fpath)


class DailyFlightArchiver(Archiver): 
    """ Class used for archiving flight reports where a report is a day """
        
    def __init__(self, archive_dir, archive_type, report_name, report_module):
        super(DailyFlightArchiver, self).__init__(archive_dir, archive_type, report_name, report_module)
    
    def archive(self, firstdate, lastdate):
        """ This functions is used to archive reports that are done per flight. The archiving is
            usually done for a whole month but the files will be kept per day.
        
        """
        
        fpath = self.create_archive_dir(firstdate)
        
        # We are looping each day in the period
        currentdate = firstdate
        while currentdate < lastdate:
            
            where = ("report_crewlists.%crewlist_allowed%", 
                     "report_crewlists.%%activity_udor%% = %s" % (currentdate),
                     "report_crewlists.%leg_is_flight%")
            
            bc = BasicContext()
    
            rave_result,  = R.eval(bc.getGenericContext(), R.foreach(R.iter("report_crewlists.activity_set", where=where),
                                                                     "report_crewlists.%activity_id%",
                                                                     "report_crewlists.%activity_udor%"))
    
            # Create a list of tuples
            activities = [(activity_id, udor) for _, activity_id, udor  in rave_result]
            
            ret = self.report_module.archive(activities)
                
            if ret:
                _,_,d,_,_ = currentdate.split()
                day_path = os.path.join(fpath, "%02d" % (d))
                print "MakingDirs", day_path
                os.makedirs(day_path)
            
                print "Creating %d files for %s" % (len(ret), report)
                for activity_id, v in ret.items():
                    file(os.path.join(day_path,"%s.xml" % activity_id),"w").write(v)
            else:
                print "No archiving done for ", currentdate
                    
            currentdate = currentdate.adddays(1)
            
        self.create_sym_link(fpath)
    

def report(servicetype=None, servicename=None, firstdate=None, base=None, maincat=None, rank=None):
    """ This is the interface to the archiver. The servicetype and servicename is used to figure out
        what reports that will be archived.
        @param serivcetype - only crewlists is currently supported 
        @param servicename - the service name
        @param firstdate - the first date, the month for this date will be archived
        @base - crew base, not used?
        @maincat - crew main category, not used?
        @rank - crew rank, not used?
        
    """ 
    
    if not firstdate:
        firstdate = now().month_floor()
    else:
        if firstdate == "month_start":
            firstdate = now().month_floor()
        elif firstdate == "prev_month_start":
            firstdate = now().month_floor().addmonths(-1)
        elif firstdate == "next_month_start":
            firstdate = now().month_floor().addmonths(1)
        else:
            firstdate = AbsTime(firstdate).month_floor()

    lastdate = (firstdate+RelTime(1)).month_ceil()
        
    if not servicetype:
        raise ValueError, "'servicetype' must be specified"
    if not servicename:
        raise ValueError, "'servicename' must be specified"
        
    archive_dir = os.path.expandvars(C().getProperty("services_archiver/archive_dir")[1])
    if not archive_dir:
        raise Exception, "XML Property 'services_archiver/archive_dir' not set"

    # Get only the last name in the service
    short_service_name = servicename[servicename.rfind(".")+1:]

    # There are a few different types of reports, crew where each report is a month, crew where each report
    # is a day, flight where each report is a day. 
    if short_service_name in ["DUTYOVERTIME", "DUTYCALC", "crewroster", "PILOTLOGCREW", "PILOTLOGSIM"]:
        archiver = MonthlyCrewArchiver(archive_dir, servicetype, short_service_name, servicename) 
        archiver.archive(firstdate, lastdate, base, maincat, rank)
    elif short_service_name in ["crewbasic"]:
        archiver = DailyCrewArchiver(archive_dir, servicetype, short_service_name, servicename)
        archiver.archive(firstdate, lastdate)
    elif short_service_name in ["crewlist"]:
        archiver = DailyActivityArchiver(archive_dir, servicetype, short_service_name, servicename)
        archiver.archive(firstdate, lastdate)
    elif short_service_name in ["PILOTLOGFLIGHT"]:
        archiver = DailyFlightArchiver(archive_dir, servicetype, short_service_name, servicename) 
        archiver.archive(firstdate, lastdate)
    else:
        raise ValueError, "Invalid 'servicename' (%s)" % (servicename)
        
    
