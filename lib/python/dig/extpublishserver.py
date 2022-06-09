"""
This module contains functionality for re-publishing crew affected by
certain events reported by external interfaces:
   * Flight schedule time changes
   * Rotation changes that might affect meal stop calculations.
   * Rerouted legs
The purpose of this functionality is to visualize latest flight and meal
stop information in Crew Portal and notify check-in time changes.
For more information about this functionality please refer to RFI 54.

The process of re-publishing crew is designed as a client-server
solution where this module contains components used by the server side
only. 
"""

import os, sys, time
import carmensystems.studio.Tracking.OpenPlan as plan
from utils.ServiceConfig import ServiceConfig
from carmensystems.common.CarmLogger import CarmLogger
import carmusr.ConfirmSave as cs
from tm import TM
from modelserver import ReferenceError
 
    
 
class ExtPublishServer:
    """ This class implements the publication server for re-publishing
        crew affected by external changes. It runs in a batch studio
        instance normally started and supervised by desmond.
        The server enters a main loop where it periodically polls
        table crew_ext_publication for new publication orders issued by
        clients (DIG channels).
    """

    _max_crew = None
    _pubCrew = None
    _cache = None
    logger = None

    def __init__(self, program, process, logpath, loopForever=True):
        self.program = program
        self.process = process
        self.config = ServiceConfig()
        self.sleep_time = int(self.getConfigAttr("sleep_time", 60))
        ExtPublishServer._max_crew = int(self.getConfigAttr("max_crew", 100))
        nr_rotationFiles = int(self.getConfigAttr("nr_rotationFiles", 5))

        if not loopForever:
            self.sleep_time = 5 

        ExtPublishServer.logger = CarmLogger(program, config=self.config, process=process, logLevel='INFO')
        ExtPublishServer.logger.setupRotationFileHandler(logpath, nRotationFiles=nr_rotationFiles, doInitialRollover=True)
        # Prevent studio from opening confirm dialogs
        cs.skip_confirm_dialog = True
        # Load database plan
        ExtPublishServer.logger.info("External publish loading plan...")
        plan.loadPlan()
        # Enter main loop
        self.loop(loopForever)
        
        ExtPublishServer.logger.info("External publish done.")

    def loop(self, loopForever=True):
        """ Loop and save periodically. On each save, publications
            and notifications will be generated
        """
        # Remember initial state
        initialState = TM.currentStateId()
        # Initialize states used for pruning
        s1 = None
        s2 = None
        while(True):
            ExtPublishServer.logger.info("External publish refreshing plan...")
            TM.refresh()
            ExtPublishServer.logger.info("External publish saving plan...")
            plan.savePlan()
            ExtPublishServer.logger.debug("External publish save Done...")
            # Force modcrew clear
            #clearExtPublishCrew()
            # Prune states to avoid overflow
            s = TM.currentStateId()
            if s1: # Will not prune the first time
                ExtPublishServer.logger.debug("Pruning state=%x, initial state=%x" % (s1, initialState))
                TM.pruneStates(s1, initialState)
            s1 = s2
            s2 = s
            time.sleep(self.sleep_time)
            
            if not loopForever:
                ExtPublishServer.logger.info("External publish: %u entries left" % (len(TM.table("crew_ext_publication"))))
                if len(TM.table("crew_ext_publication")) == 0:
                    return
                        

    def getConfigAttr(self, prop, default):
        """ Get attributes from common configuration. Attributes may be 
            defined on either program or process level.
        """
        k, p = self.config.getProperty(self.program + "/" + self.process + "/" + prop)
        if p is None:
            k, p = self.config.getProperty(self.program + "/" + prop)
            if p is None:
                if default is None:
                    raise ValueError('Failed to find property: %s' % prop)
                else:
                    p = default
        return p

    @classmethod
    def getExtPublishCrew(cls, cache=False):
        """ This method is called by Studio through the modcrew module,
            as a part of the save process. It returns a list of crew
            that will be subject to publication/notification handling.
        """

        if cache and cls._cache is None:
            cls._cache = set()
                
        if cls._pubCrew is None:
            cls._pubCrew = set()
                      
            nRecs = 0
            for rec in TM.crew_ext_publication.search('(id=*)'):
                nRecs += 1
                try:
                    if cache:
                        if not rec.crew.id in cls._cache:
                            cls._pubCrew.add(rec.crew.id)
                            cls._cache.add(rec.crew.id)
                    else:
                        cls._pubCrew.add(rec.crew.id)
                except ReferenceError:
                    # Happens if crew does not have a valid contract within
                    # the tracking period, e.g. due to retirement.
                    cls.logger.error("Skipping non-existing crew: %s" % rec)
                    pass
                # Remove the publication orders that have been treated...
                rec.remove()
                if len(cls._pubCrew) >= cls._max_crew:
                    cls.logger.debug("External publish breaking at %d crew" % cls._max_crew)
                    break;
            cls.logger.info("External publish read %d records" % nRecs)
        cls.logger.info("External publish crew %s" % cls._pubCrew)
        return list(cls._pubCrew)

    @classmethod
    def clearExtPublishCrew(cls):
        cls.logger.info("External publish clearing crew list...")
        cls._pubCrew = None


if __name__ == "__main__":
    ExtPublishServer(sys.argv[1], sys.argv[2], sys.argv[3])

