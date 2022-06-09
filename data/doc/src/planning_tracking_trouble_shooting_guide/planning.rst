
Planning Trouble Shooting Procedures
------------------------------------


Erroneous data in plan
^^^^^^^^^^^^^^^^^^^^^^

**Area**
  Planning (SASCMS-4214, SASCMS-4847)


**Symptom**
  - When loading a database plan a warning message with the following text appears:

  ::

    Warning: There is erroneous data in plan. 
    Please contact     
    Carmen Support

  - The logfile contains error(s) of the following type:

  ::
  
    Error! TripTable::postProcess(): Erroneous data:
      CRR: 
        tab_ix: -1
        name: 
        tag: Nonpersonal CRR
        tag: No free leg CRR
        envSubPlanIx = 0
        crew: nil
        .
        .
        .


**Diagnose/Cause**
  Database contains corrupt trip data within the time span loaded        
        
**Solution**

  Run clean-up script:

  1.  Start cms shell and locate logfile containing the error above  ``> logs`` (for planning studio logs go to $CARMUSR/current_carmtmp_cas/logfiles)
  2.  ``> logcheck erroneousdata [logfile]``
  3.  The script outputs a list of trips and reports on what  seems broken.
  4.  If run with the flag --removebrokentrips=True broken trips will be removed (after pressing ENTER when prompted)
  5.  A new commitid is returned when the trip(s) have been removed.

  NOTE! This will BATCH EDIT LIVE DATA

Inconsistent chains
^^^^^^^^^^^^^^^^^^^
**Area**
  Planning (SASCMS-4406) 

**Symptom**
  User gets a warning message with something like the following text:

  ::
  
    ERROR: Assigned CRR must have the same kernel as ...
    Internal Error: Inconsistent chain.
    Contact Carmen Support

**Diagnose/Cause**
  Inconsistent crr chains caused by Return-To-Ramp or Diversion flights. When this occurs new 
  legs are created within a trip, by a DIG job, breaking the original crr chain.

**Solution**
  The problem is solved by reopening the database plan. 

Export not possible
^^^^^^^^^^^^^^^^^^^

**Area**
  Planning (SASCMS-5067, SASCMS-4705)

**Symptom**
  User gets an error message when trying to export a scenario to file plan. The logfile 
  contains an error of the type:

  ::

    ExportScenario::_create_ground_task_map_tmp_table: GenericEntity::unsafeGetRef: Column task in table ground_task_attr contains 
    value <TASK KEY> that does not exist in referred table ground_task. Here <TASK KEY> is of type udor+id for a ground task

**Diagnose/Cause**
  There is a row in table ground_task_attr referring to a task that does not exist in table ground_task.

**Solution**
  The problem is solved by removing the entry with a bad task key from the table  ground_task_attr

