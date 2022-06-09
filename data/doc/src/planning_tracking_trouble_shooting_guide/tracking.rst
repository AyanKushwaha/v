Tracking Trouble Shooting Procedures
------------------------------------

Specific users cannot access launcher
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System


**Symptom**

  Specific users cannot access launcher and get error "system not configured properly".

**Diagnose/Cause**

  - Since there are many local modification in $CARMUSR/etc/users/PROD.xml, some userids can be written more than once.
  - It will confuse sessionserver and return an empty launcher.

**Solution**

  Remove the duplicated user ids.

Table Editor cannot startup for non-administrator user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking


**Symptom**

  Table Editor cannot startup for non-administrator user, but it works for administrator.

**Diagnose/Cause**

  - Sessionserver was not started from clean shell, but from cmsshell.
  - cmsshell contains complex environment variable, it will hard code CCROLE = Administrator. Changing roles won't help.
  - Administrators suppose to use TableEditorAdmin instead of normal TableEditor application.
  - It will be problematic if user is a tracker but try to use normal TableEditor with administrator role.

**Solution**

  Restart sessionserver in CLEAN shell (NOT cmsshell).

Number of alerts differs between Alert Monitor and Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking


**Symptom**
  
  The number of alerts in AlertMonitor does not match the number of illegalities in Studio.

**Diagnose/Cause**

  - A certain rule is violated twice on the same object. This will give two illegalities in Studio, 
    but only one alert in Alert Monitor
  - The AlertGenerator has a different parameter set.           
        
**Solution**
  
  The parameter sets are located in $CARMUSR/crc/parameters/tracking. See if there are differences
  between Studio and the AlertGenerator.

Application is missing in the Launcher 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Area**
  System 

**Symptom**
  A user does not have access to a specific application through the Launcher


**Diagnose/Cause**

  1. The user does not have the right role the the specific application. 
  2. The users role does not have access to the specific application

**Solution**

  1. The users role can be edited in $CARMUSR/etc/users.xml 
  2. Which role that have access to a specific application can be edited in $CARMUSR/etc/roles.xml 
 

Time is not synchronized between Alert Monitor and Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Studio and Alert Monitor have different "now time".

**Diagnose/Cause**

  1. Studio and Alert Monitor are set to different time zones. 
  2. Environment variable TZ not set to UTC in start/configuration scripts. 

**Solution**

  1. Set Studio and Alert monitor to use the same time zone. In Alert Monitor the time zone is changed in the drop down list in the upper left corner. In Studio the time zone is changed in "Tools" -> "Preferences". Change "Scale time presentation" to the prefered time zone. 
  2. Make sure TZ is set to UTC. 



Keyboard is not working correctly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  The keyboard is not working correctly in Studio, e.g. special characters like "å,ä and ö" can not be entered. 

**Diagnose/Cause**
  Exceed setup is incorrect.

**Solution**
  Setup Exceed to use the correct keyboard layout. Instructions can be found at: Z:\Customer\Projects\Finnair CMS\03 Development\01 Project management\10 Documentation\02 Configuration instructions 


"Command could not be invoked" message when starting Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  The following message is recived when Studio starts: "Command could not be invoked". No Java-forms can be opened in Studio. 

**Diagnose/Cause**
  Java is not installed or not in the path 
  
**Solution**
  Install java and add it to the path. 


Reports are opened centered over both screens
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  On systems with dual screens the reports are opened centered over both screens.

**Diagnose/Cause**
  Old Exceed is not handling X-window positions correctly. 

**Solution**
  Not known, update Exceed?


Components dying, Oracle not available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System

**Symptom**

  Component fails when trying to connect to Oracle 
  
  ::  
  
    The following OCI errors found in component logfile(s): 
    ORA-01034: ORACLE not available 
    ORA-27101: shared memory realm does not exist 
  

**Diagnose/Cause**

  Oracle may have run out of processes. Verify whether this is the case by checking
  the number of Oracle processes. If these are up by the limit (default: 128), it's bad...  

**Solution**
  Try to remove the components/clients "eating" up Oracle processes 


Rule parameter form can only be opened once
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System

**Symptom**
  "Tools -> Rule parameters" can only be opened once.  

**Diagnose/Cause**
  Exceed issue (the bug has been seen on Exceed ver. 11.0.0.0). 

**Solution**
  Update to, at least, Exceed 11.0.0.11. 


Studio is not starting
^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System

**Symptom**
  An error message is shown when trying to start Studio. The message is something like: 
  ``"Could not start Studio.Make sure the X-server is running"`` If this message comes after a longer delay (~1 minute) it 
  could indicate that the KDC is down or not responding, see below. No visible symptom to the user. 

**Diagnose/Cause**

  1.  If it is not possible to start any other graphical application either (e.g. emacs), the disk might be full (probably with core dumps and/or logfiles). 
  2.  SGE is used to distribute Studio sessions between several servers. This error might therefore occur if the sgeserver is down. See if the client can connect to the sgemaster by running the command qstat. 
  3.  The SessionServer's get_host script may be incorrect (and fail). NB. The script may also fail if all possible hosts (in ths SGE studio queue) are misconfigured... (see below) 
  4.  The host chosen by get_host may be misconfigured in SGE, e.g. wrong carmarch. 
  5.  SSH may be misconfigured or the .ssh directory and/or the .ssh/authorized keys may have wrong file permissons. 
  6.  The Kerberos KDC is down/not responding 
  7.  The System (CARMUSR/CARMSYS) configuration is inconsistent or erroneous. 
  8.  The SessionServer is down/not responding. If this is the case, trying to start Studio will most likely hang indefinitely. 
  9.  The SessionServer's etc/system_config.xml, has not been touched after a CARMSYS or CARMUSR change. This cause is not so likely but a lot of weird symptoms may occur because of this so it's good to keep this in mind.  

**Solution**

  1.  Free up some space on the disk. 
  2.  Start the sgeserver by running this command with superuser (root) privileges: /sbin/service sgemaster start. You can then use qhost to verify that all clients are running. Start a client that is not running by issuing the following command as superuser (root): /sbin/service sgeexecd start 
  3.  Correct the SessionServer's get_host script and verufy that it works as it should. 
  4.  Correct the SGE configuration for the host in question and try to verify that it is correct. 
  5.  Check (and possibly correct) the SSH configuration and/or file permissions. 
  6.  Verify that the Kerberos KDC is running. Restart it (as superuser) if it isn't: /sbin/service krb5kdc start
  7.  Verify the configuration using CARMUSR/bin/xmlconfig.sh --all or $CARMSYS/bin/xmlconfig --all 
  8.  If the SessionServer is down (terminated) you will have to restart it (as superuser) on the SessionServer host with /sbin/service tomcat5 start . If it is hung or otherwise just non-responding you will probably have to restart it with /sbin/service tomcat5 restart . Moreover, all users will most likely have to restart their entire sessions, i.e. restart the launcher and whatever application(s) they need. 
  9.  Touch the SessionServer's etc/system_config.xml 


Fatal Error when eg. Studio tries to open plan caused by ORA-12541
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System

**Symptom**
  Components, i.e. servers and Studio fails during startup when trying to load plan. Error ORA-12541 in logfile. 

**Diagnose/Cause**
  No Oracle listener is responding when trying to connect using the Oracle connect string.

**Solution**

  1.  Verify that the Oracle connect string is correct. If not, fix it in the configuration! This will probably also require fixing the subplanHeader file in $CARMDATA/LOCAL_PLAN. 
  2.  If the connect string is correct, you will have to determine whether the Oracle listener is up and running on the db_host(s). Use e.g. 'ps', 'netstat' or 'lsof' to do this. NB. The traditional/default port for Oracle is 1521. If the port is defined in /etc/services you will have to grep for the name there instead of the portnumber! 

  ::
   
     Example using netstat 
     [carmen@aylx032 ~]$ netstat -a | grep 1621
     tcp        0      0 aylx032.finnair.fi:1621     *:*                         LISTEN      
     tcp        0      0 aylx032-vip.finnair.fi:1621 *:*                         LISTEN 


  ::   
    
     Example using ps 
     [carmen@aylx032 ~]$ ps aux | grep tns
     orarac   26244  0.0  0.0 65876 10532 ?       Ssl  14:12   0:00 /orabin/rac102/dbms/bin/tnslsnr LISTENER_RACPROD_AYLX032 -inherit
     orarac    1969  0.0  0.0 65216 9756 ?        Ssl  14:33   0:00 /orabin/rac102/dbms/bin/tnslsnr LISTENER_CMPL_AYLX032 -inherit
     orarac    6124  0.0  0.0 65168 9672 ?        Ssl  15:07   0:00 /orabin/rac102/asm/bin/tnslsnr LISTENER -inherit
     carmen   11268  0.0  0.0 51100  704 pts/1    R+   16:54   0:00 grep tns



Cannot compile, message about Stale NFS file handle (SGE)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Cannot compile rave program using sge, local compilation still workds 
  No error messages can be found in the sge queues 
  

**Diagnose/Cause**
  The NFS has been restarted, the sge master host has been rebooted

**Solution**
  Log in to the sge master, and run ``sudo /sbin/service sgemaster start`` or use restart. 


Problems blocked SGE queues
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Processes do not start in time. Example external forms, rave compilations.
  Starting studio fom launcher or Alert Monitor works. 
  ``qstat -f`` shows queue items with a capital E in the end.

**Diagnose/Cause**
  The sun grid engine queues have been blocked (E), due to a failed job submission. 
  One frequent cause of failed job submission is "stale NFS handle" 

  Use qstat -f -explain E, and grep the qmaster logfile to find the cause.
   
  ::
  
    qstat -f -explain E
    grep [node with error] /opt/Carmen/sge/default/spool/qmaster/messages

  At Finnair the cause have been a restart of some machines which made the filesystem go down and left stale NFS handles.


**Solution**
  The command ``qmod -cq \*`` clears all queues of errors blocking. It might be wise to check the explanations first and see that all of them are clear. 
  To clear only one queue instance: ``qmod -cq [queue@node]``


Some functionality (usually called from a menu) fails
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  A function is executed but nothing happens, or the visual changes revert to previous state.

**Diagnose/Cause**
  Missing data in lookup tables in the database. 

**Solution**
  Look in the trace log, usually it is printed which data is missing from which table. If not 
  this could still be a problem but the exception is passed to another part of the code so using 
  the trace log may not always work. In that case, try to locate in which module the function 
  resides in by looking in the menu file structure. In that code you can always try to figure out 
  where the exception is raised and there you should be able to see if the code tries to lookup data 
  in some table. 
  E.g: When swapping two trips assigned on rosters, if the entry TRADE (Technical) is missing from 
  assignment_attr_set then both trips are reverted to their previous roster. The swap fails.


Studio contain a lot of looong trips in a roster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  A crew member have no trip breaks at homebase. There is a long continously trip in the roster. 
  This will make much functionality malfunction. 

**Diagnose/Cause**
  The crew member has no or incorrect homebase defined 
  The base is not defined in the system

**Solution**
  Make sure that the crew member has a base by checking in the crew information form. If no base is defined, create a new base definition and save. This can all be done through the crew information form. You might need to have the debug menu to recalulcate trips accoring to rave. Save after the trips have been updated. 
  The base might also be so new that it is not defined yet. Then it need to be added in: 
  crew_base_set table through the table editor, and also the static table for new creation ($CARMUSR/INPUT_FILES/Static...) 
  the DefaultBaseDefinitions files in $CARMUSR/crc/etable..... 
  the DefaultBasedDefinitions files in $CARMUSR/LOCAL_PLAN.... 
  the DefaultBaseConstraints files in $CARMUSR/crc/etable..... 
  the DefaultBasedConstraits files in $CARMUSR/LOCAL_PLAN.... 
  $CARMUSR/ETABLES/Static/asia_bases.etab (if it is am asia base) 
  Crew fast select statements 
  RAVE code!


No tables modified by DigXML message (Interfaces)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  The data which is to be modified in the tables of the database has not been modified. DigXML is used.

**Diagnose/Cause**

  1. The input queue is not configured right or the DIG processes are not up and running or running with 
     incorrect configuration. 
     Check the configuration of the inqueue. Check that all the DIG-processes are up and running. Use 
     for e.g. 'ps aux | grep <interface name>' and look in the Desmond log and the DIG log to see if the 
     processes are healthy. 
  2. The DigXML message is incorrect. Look for error messages in the log of the queue. If the DigXML message
     is incorrect the log will describe the error. Possible errors in the message are; message not well formed, incorrect table name, incorrect name of data field, incorrect data format etc. 
  3. The update period for the Report Server is set to one hour and when trying the check the updated data within 
     the time there are no modifications to be found yet. The time for the update period will increase to 
     approximately 1 minute when the Report Server is implemented with multi tasking solution. 
     Check the configuration of the Report Server to see what the updating time is set to. Do not change the time!


**Solution**

  1. Setup Desmond to run the processes correctly, correct possible errors in the configuration and make sure the right start scripts are run for the DIG-process. 
  2. It is important that the DigXML message is well formed and unfortunately this error is not logged in a good way, so if there is no explanation to the error, the message should be corrected until it is well formed. An easy way to see if it is well formed is to open the message in a browser. If the name of the data field or if the data format is incorrect, make sure to correct this in the compilation of the message. 
  3. If a modification of the database is done and for e.g. a request-response message is used to check the modifications, the modification might not be seen because it will take some time until the Report Server is updated with the new data. This is not an error and this type of modification check must be done after the Report Server has been updated.

No reply messages or error message received by requester (Interfaces)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  The requester does not get a reply message or gets an error message from the reply queue.

**Diagnose/Cause**

  1. The input or output queues are not configured right or the DIG processes are not up and running or running with incorrect configuration. 
     - Check the configuration of the in- and outqueue. Check that all the DIG-processes are up and running. Use for e.g. 'ps aux | grep <interface name>' and look in the Desmond log and the DIG log to see if the processes are healthy. 
  2. An error has occurred in the application either because of a bug in the code or changes in the data base. 
     - The application's stderr is directed to the log of the Report Server, so if an error has occurred in the application it will be found here. Some of the application also replies an error message if an error has occurred. 

**Solution**

  1. Setup Desmond to run the processes correctly, correct possible errors in the configuration and make sure the right start scripts are run for the DIG-process. 
  2. Correct the code bug or correct the interaction with the data base. 


No reports generated (Interfaces)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  There are no reports generated from the application.

**Diagnose/Cause**

  1. The application is not invoked which may be caused by the crontab if it isn't scheduled right or if crontab is running wrong script or a faulty script. 

     - Make sure the crontab is running. Check its configuration to see that right script is running and is scheduled to run on wanted time and interval. Check the run script to make sure it invokes the right application with right parameters. 
  2. The input (if it isn't using the Report Server directly) or output queues are not configured right or the DIG processes are not up and running or running with incorrect configuration.

     - Check the configuration of the in- and outqueue. Check that all the DIG-processes are up and running. Use for e.g. 'ps aux | grep <interface name>' and look in the Desmond log and the DIG log to see if the processes are healthy. 
  3. An error has occurred in the application either because of a bug in the code or changes in the data base.

     - The application's stderr is directed to the log of the Report Server, so if any error has occurred in the application it will be found here. Some of the application also replies an error message if an error has occurred. 

**Solution**

  1. Correct the errors found in the configuration of crontab or correct the scripts. Run the script manually, possibly by adding a date argument for using the correct (non-default) period. 
  2. Setup Desmond to run the processes correctly, correct possible errors in the configuration and make sure the right start scripts are run for the DIG-process. 
  3. Correct the code bug or correct the interaction with the data base. 


Problems connecting to the database due to default port settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  OCI-Error "Listener does not currently know of given SID" 

**Diagnose/Cause**
  Since the default port to oracle databases is 1521 that is what Dave will use if no port is specified. 
  The current database installation at Finnair uses the port 1621. Therefore applications with no specific 
  port given will fail.

**Solution**
  Always specify the port to all applications using the database.


Crew is missing or has wrong position
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Logfile might say "could not find trip for cfd: 0" Hovering with mouse cursor over rostered flight leg 
  shows no position or wrong position according to the generic model.  

**Diagnose/Cause**
  A possible problem might be that the entity crew_flight_duty did not have any value set in the column 
  personaltrip.

**Solution**
  Close studio without saving and then run $CARMUSR/bin/startMirador.sh -s ARASyncFixes Note that this 
  fix only works if that really is the problem. 


Java forms behave strange
^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  A Java form for a specific <user> behaves strange when opening it e.g. it becomes maximized or minimized.  

**Diagnose/Cause**
  ?

**Solution**
  Remove the directory /home/<user>/.java 


One of several hard to find problems with save/refresh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  There are OCI errors stating things like "invalid identifier CA_ET" Can also be other kind 

**Diagnose/Cause**
  This problem might be due to invalid entries in the filter table dave_entity_selection. The error 
  message above is an example of trying to filter on referenced attributes which are not part of the key. 
  Other errors such as malformed "META-SQL" can also be there.

**Solution**
  Edit the table using a db editor such as sqlplus or table editor. Also change it $CARMUSR/crc/etable/inital_load/dave_entity_select.etab


CARMUTIL not correctly installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Get "TRACE: No library libclntsh.so loaded" message in logfile when trying to load schema in Studio. 

**Diagnose/Cause**
  CARMUTIL is probably not correctly installed since the libclntsh.so which is part of Oracle InstantClient apparently cannot be found. Apart from the obvious case when CARMUTIL isn't installed at all, a typical case is when CARMUTIL is installed on NFS-mounted disks which easily can cause timestamp related problems which will cause RPM verification (rpm -V) to fail. When running the command rpm -qa carmutil\* you should get the following output: 
  
  ::
    
    tester6@csc3 ay_work$ rpm -qa carmutil*
    carmutilmaster-master-2.EL4
    carmutil13+-13+-1.EL4
    carmutil13+-13+-1.EL4
    carmutilmaster-master-2.EL4
    
  In addition to this, you should verify that the actual RPM packages are installed in /opt/carmutil instead of /opt/Carmen if the latter is NFS-mounted (which typically is the case). 


**Solution**
  
  1.  Remove CARMUTILs installed if they are installed on NFS-mounted disks, e.g. with rpm -e --allmatches carmutil13+-13+-1.EL4 
  2.  (Re)Install the missing rpm(s) using e.g. rpm -i --prefix=/opt/carmutil <rpm_file>. 
      (On Suppnet the RPM files may be found in /mnt/Carmen_kickstart/RPMS/, provided the disk area is mounted. If not, you will have to mount it with mount -t nfs fillmore:/vol/volmisc/images/RHEL /mnt) 


Studio cannot determine relative order of contexts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  When opening plan it results in a red message box and a red cross that states that the operation has failed. In the logfile it usually says that studio can't determine the relative order of contexts.  

**Diagnose/Cause**
  Studio has most probably not been able to connect to the Oracle database. Look for problems with OCI/ORA in the message. At least the following problems can occur: 
  
  - TNS Listener not found 
  - Invalid login/password 
  - Oracle host not found 


**Solution**
  Check the connect string and look for the database installation on the server. Contact the responsible person for the DB. 


Launcher hangs during startup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  System

**Symptom**
  Client launcher hangs during startup 

**Diagnose/Cause**
  The SessionServer may be down/not responding. Check if it is running and try to figure out if it has been suspended indefinitely. 

**Solution**
  1. If the SessionServer is down, it should be OK to just (re)start it (as superuser) with: ``$ /sbin/service tomcat5 start``
  2. If the SessionServer is hung, try the following (as superuser or the tomcat user): ``$ kill -CONT <ss_pid>``

  If this doesn't help - a restart will probably not resolve the problem entirely if the SessionServer is hung. In that case a restart of the launcher will also be required.


Weird/wrong time in Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Wrong time in Studio, typically a UTC time "interpreted" as local time   

**Diagnose/Cause**
  Clock/hwclock configuration is probably not entirely correct on the actual Studio host.

**Solution**
  If there is a problem with a single host (or two) this type of issue is not really our problem. 
  Check date, clock (/sbin/hwclock), adjtime (/etc/adjtime) and /etc/sysconfig/clock on the host with 
  erroneous time and compare with a host with correct time. If you notice discrepancies, try to provide 
  information about these to IBM/CSC/Whoever is responsible for the client's IT infrastructure/hardware.

Viewing temporary tables via Table Editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  A lot of temporary tables are created through out the code (Python) and they are filtered out in the 
  Table Editor which means that they are not displayed among the database tables. But sometimes it is 
  good to be able to see what their content is to be able to trace any problems there might be.

**Diagnose/Cause**
  ?

**Solution**
  The best and easiest way (!) to see these temporary tables (if you know what they are called by name) 
  is to open the Table Editor and choose to Open a Table from the File menu. Then just type the name of 
  the table or simply scroll in the list until you find it.


Studio does not start from the Alert Monitor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Can not start Studio from the Alert Monitor. An error message showing that the the system tries to find 
  a file in a strange place (might be in a different CARMUSR then the one you are using).

**Diagnose/Cause**
  When starting Studio as root, .pyc files will be written in the CARMSYS. These files will then be used 
  instead of recompiling the .py files.

**Solution**
  Avoid starting a system (or rather any application, e.g. Studio using Python) as root. If you do happen 
  to start as root, reinstall the CARMSYS or (alternatively) remove all .pyc files in the CARMSYS.

Error saving model
^^^^^^^^^^^^^^^^^^

**Area**
  Tracking

**Symptom**
  Not possible to save to database. In the log something like: 
  Error saving model: data too old OCI::Reader::vstmt OCIStmtExecute(...)=OCI_ERROR ORA-00001: unique constraint 
  (CMS_PRODUCTION_GOT_1.FLIGHT_LEG_IP) violated DMFModel::save: got PlainException calling engine save: ModelException: 
  Revision/Key Conflicts in data: Record snapshot outdated in table cms_production_got_1.flight_leg row: 5410, N, 2421, 
  0, 1, 7943, AY 000021 , HEL, DEL, J, 11438595, 11438995, 11438597, 11438995, 11438599, 11438998, M11, , AY, NULL, NULL, 
  NULL, 0, NULL, NULL, NULL, 0, 0, 11438610, 11438992, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 
  253, 85, 4, NULL, 0, NULL, 2370I
  
**Diagnose/Cause**
  To find out where the problem is look at the table record pointed out by the log information. To convert the CarmTime 
  to a useful date there is a python function FDatInt2DateTime(). In the example above you could use "Execute Python 
  code..." and enter "print Dates.FDatInt2DateTime(11438595)". This gives "01Oct2007 11:15" in the log, so the problem 
  in this case was with the flight AY 21 on 1 october. 


**Solution**
  ?
