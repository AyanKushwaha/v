Crew Services Trouble Shooting Procedures
-----------------------------------------

The setup of CrewServices is slightly different on the TEST and the PROD system.

**MQ and DIG channels**

On the PROD system all requests from CrewServices including Datalink (landings) are sent on MQ-queue named CQFREQ. The DIG channel named
crewservices reads messages from this MQ-queue.

On the TEST system all requests from CrewServices TEST system are sent on MQ-queue named CQFREQZ. The DIG channel named crewservices_test reads messages from this MQ-queue.
In the TEST system CMS also receives a copy of CheckInOut and landings messages from the PROD system. These messages are sent on MQ-queue CQFREQ to the crewservices DIG channel.
Before the requests reach CMS's MQ-queues, they are routed through a network in Tibco which very likely can be the cause of the problem.

**ReportServers**

A ReportServer serves requests from the crewservices DIG channel. The ReportServer to be used depends on the MQ message.

+ PUBLISH ReportServer

  (Holds published rosters excluding do_not_publish)
   * CrewBasic
   * CrewRoster
   * CrewList
   * DutyCalculation
   * FutureActivities
   * VACATION

+ LATEST ReportServer

  (Holds rosters as they look now including do_not_publish)
   * CrewBasic
   * CrewRoster
   * CrewFlight
   * CrewLanding
   * DutyCalculation
   * PILOGLOGCREW
   * PILOGLOGFLIGHT
   * PILOGLOGSIM
   * PILOGLOGACCUM
   * DUTYOVERTIME

+ SCHEDULED ReportServer

  (Holds rosters as they looked when published)
   * CREWSLIP

**Logfiles**

The logfiles from the crewservices DIG channel are stored in $CARMTMP/logfiles/DIG/.
The MQ messages read by the crewservices channel are recorded to file and stored in $CARMTMP/logfiles/DIG/ with filename CQFREQ_LIVE{YYYMMDD}.log (PROD) and CQFREQ_LIVE_TEST{YYYMMDD}.log (TEST)

The location of the ReportServer logfiles can be found in the table below.

======================= ================================= =================================
ReportServer            PROD                              TEST
======================= ================================= =================================
SAS_RS_WORKER_LATEST    /var/carmtmp/logfiles/ (h1cms07a) /var/carmtmp/logfiles/ (h1cms97a)
SAS_RS_WORKER_PUBLISHED /var/carmtmp/logfiles/ (h1cms08a) /var/carmtmp/logfiles/ (h1cms98a)
SAS_RS_WORKER_SCHEDULED $CARMTMP/logfiles/                $CARMTMP/logfiles/
======================= ================================= =================================



The cmsshell commands in this section is primarily to be used by System Administrators.

Step-by-step check
^^^^^^^^^^^^^^^^^^
1. Does CMS write any new recorded MQ message to the log?

   - Yes. CMS receives the messages and the problem is most likely in CMS.
   - No. CMS does not receive messages and the problem is most likely in Tibco. Contact CSC.

2. Anything unusual in the crewservices DIG channel?

   - Is it running? If not it can be started by executing this cmsshell command on the correct node
     ::

        sysmondctl start crewservices
        sysmondctl start crewservices_test (on TEST)

3. Anything unusual in the ReportServer (PUBLISH) log?

   - Is it running? If not it can be started by executing this cmsshell command on the correct node
     ::

        sysmondctl start SAS_RS_WORKER_PUBLISH
