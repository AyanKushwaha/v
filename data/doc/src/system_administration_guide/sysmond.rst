.. _sysmond:

Sysmond
=======

Sysmond is the monitoring daemon for the background processes in Jeppesen
systems.

This chapter contains the following sections:

* :ref:`sysmond.introduction`
* :ref:`sysmond.configuration`
* :ref:`sysmond.installation`
* :ref:`sysmond.using_sysmond`, with information on :ref:`sysmond.scripts_and_binaries`, :ref:`sysmond.starting_and_stopping_sysmond`.
* :ref:`sysmond.appendix_list_of_cli`

.. _sysmond.introduction:

Introduction
------------
Sysmond's main task is to start the system and maintain it running continuously.
Sysmond is configured with a number of processes to start for each
controlled host. Depending on the configuration Sysmond makes sure these
processes are automatically restarted in case they would crash or become
unresponsive.

Sysmond also provides limited High Availability (HA) capability for
DIG in a defined framework. When background processes run on multiples
nodes, each node will also have one Sysmond instance. Sysmond can
detect when a background process has stopped or crashed, and restart
the failed process. If an active HA-process crashes, the other process
in the HA-pair will be activated and the crashed process restarted
(running in standby). Background processes are started as child
processes.  This makes it possible for Sysmond to detect any unusual
changes in background processes, for example when a process has been
stopped in a controlled way (by human interaction) or in uncontrolled
way (process crash). The use of the HA capability in Sysmond depends
on the support in the managed applications for this feature.

If any configured process, that is not running as ``monitor_only``, dies, Sysmond will automatically restart it.
Sysmond can also be configured to be proactive by defining limit values on the measured statistics for the processes.
You can define a sequence of actions or tasks (consisting of actions) to be
executed when a limit is reached or violated.

Actions
^^^^^^^
Sysmond's main task is to start the system and maintain it running continously. In order to do so,
Sysmond can be configured to handle different situations by actions. Actions are the building blocks
on which other services, as for example tasks, are based on. Actions can be email notifications or CLI
commands.

Tasks
^^^^^
A task, with a unique task name, consists of one or more actions that are executed in sequence, at certain times or time intervals or limits.
For more information on configuring tasks, see :ref:`sysmond.task_properties`.

Statistics
^^^^^^^^^^
For each process defined in the configuration file, Sysmond will measure and
report statistics on memory usage and CPU utilization in a log file, which is
set up in the configuration file. The following statistics are measured:
 
* CPU utilization
* MEM - virtual memory
* RSS - resident set size memory
* FDS - open/used file descriptors.
 
Sysmond is set up to report statistics on all the processes children as well.
Sysmond internally generates all processes which are children of the defined
subprocess.

Limits
++++++
Sysmond can check and report minimum, maximum and load limits on statistics, which are set up in the configuration file. It is possible to define a
sequence of actions and tasks to be executed when a limit is reached or violated.

Signals
^^^^^^^
The normal way to stop Sysmond in a controlled way is to send the ``shutdown``
or ``exit`` command to Sysmond. Sysmond will also shut down in a controlled
when receiving a ``SIGINT``, ``SIGQUIT`` or ``SIGTERM`` signal.

For processes using the Application ping protocol, the first stop method is by
using the protocol to ask the process to terminate, see ``terminate`` in :ref:`sysmond.application_ping_protocol`.

When Sysmond stops in a controlled way, a process started by Sysmond is
stopped in the following way:

#. If there is a configured ``stop_cmd``, this is applied first.
#. If there is a configured ``stop_signal``, this is sent to the process. Alternatively a SIGTERM is sent to the process.
   Sysmond then waits for the processes to end before it quits. The default waiting time is ten seconds and is configurable in :ref:`stop_wait_time <sysmond.stop_wait_time>`.
#. If the process fails to stop by the methods above, a ``SIGKILL`` is sent to it.

.. _sysmond.application_ping_protocol:

Application ping protocol
^^^^^^^^^^^^^^^^^^^^^^^^^
The Application ping protocol, an internal protocol between Jeppesen components, is based on UDP messages and only defined and valid for traffic over
"localhost", and only expected to be in use between the local Sysmond instance and the applications this instance controls. Sysmond has to be either
the originator or the responder of every message exchange, and its peer is the controllable application. A Sysmond instance tracks processes by their PIDs
on the local host. The following commands are defined for the Application ping protocol:

============== ====================== ================================================
Command        Can be sent from       Description
============== ====================== ================================================
``REGISTER``   Application to Sysmond Set up Sysmond application context.
``UNREGISTER`` Application to Sysmond Remove process from ``active`` state.
``GO_IDLE``    Sysmond to application Cause application to go to state ``idle``.
``GO_ACTIVE``  Sysmond to application Cause application to go to state ``active``.
``GO_STANDBY`` Sysmond to application Cause application to go to state ``standby``.
``STATUS``     Sysmond to application Ask for recipient state, or progress into state.
``TERMINATE``  Sysmond to application Cause application to terminate.
============== ====================== ================================================

High availability
^^^^^^^^^^^^^^^^^
Sysmond provides High Availability functionality DIG processes in the CMS system. Sysmond manages processes running on different
nodes in an active-passive cluster mode. As per background process only one pair of clustered processes (one in active and one in standby/passive state) is
supported by Sysmond. There is no limit on the number of Sysmond instances in a Jeppesen system. For example, two Sysmond instances could
monitor one pair of clustered background processes, and two additional Sysmond instances could monitor another pair of background processes.

.. figure: images/ex_two_sysmond_instances_monitoring_process_pairs.png

   Example of two Sysmond instances monitoring process pairs.

If the active process fails to operate properly, it is immediately replaced by
the standby process that now becomes active. A replacement standby process
is created in its turn.

In addition to this, Sysmond also supports process clusters for Report servers
and Trigger servers where implicitly internal worker processes are created.

.. _sysmond.configuration:

Configuration
-------------
Common Configuration is used to configure Sysmond itself as well as the
processes that are monitored by Sysmond. There are configuration elements
(tags) that are specific to Sysmond, and there are others that are used for the
monitored processes.

This section contains:

* :ref:`sysmond.elements_for_monitored_processes`.
* :ref:`sysmond.system_configuration`.

.. tip::
   See also :ref:`common_configuration`

.. _sysmond.elements_for_monitored_processes:

Elements for monitored processes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are several special elements that can be used in the configuration of processes and programs that
are monitored by Sysmond. These elements control the way Sysmond monitors these programs/(sub)processes.

For most of the elements, the value is given as the content of the element (the values below are just examples).
Attributes are also used for some elements.

Limits
++++++
Elements that are use to define limits for CPU, FDS, memory, RSS, and children (subprocesses):

``<cpu_limit min="value" max="value"> action|task</cpu_limit>``
   Defines limits for CPU in percent. See :ref:`sysmond.limits`.

``<fds_limit min="value" max="value"> action|task</fds_limit>``
   Defines limits for open/used file descriptors as integer.

``<mem_limit min="value" max="value"> action|task</mem_limit>``
   Defines limits for virtual memory in Mb.

``<rss_limit min="value" max="value"> action|task</rss_limit>``
   Defines limits for RSS in Mb.

Other elements
++++++++++++++
The following other elements exist:

``<HA_process>true</HA_process>``
   Defines whether a process is a HA process. HA processes must also set the ping_interval, see :ref:`ping_interval <sysmond.ping_interval>`.

``<heartbeat interval="10" timeout="30" start_delay="60"</heartbeat>``
   Each instance of Sysmond will send a heartbeat message over TCP to the
   other Sysmond instances. Configured for the system on ``program`` level, this is
   done every ``interval`` in seconds, at the "same" (right after) time a check is
   made to see if the last message from any other Sysmond instance is older than
   the ``timeout`` value (in seconds). To allow for startup delays when starting up
   several Sysmond instances, the time-out is initially set to ``start_delay`` (in
   seconds).

   When no heartbeat has been received from a Sysmond instance before the
   time-out, HA-processes that are in standby on the local Sysmond instance
   will be activated.

``<home_dir>/ops/iocs/1.0/bin/</home_dir>``
   The home directory for this process.

``<log_file></log_file>``
   Defines where output should go, do not add a file extension. If ``log_file`` is
   not found, ``log_file`` is constructed from ``log_dir`` in combination with
   ``log_name``.

``<log_dir></log_dir>``
   Defines directory for output and is used in combination with ``log_name``. If this
   directory is not defined, the default log directory is used. If the default log
   directory does not exist either, the log is written to the ``/tmp`` directory.

   .. note::
      This only applies when ``log_file`` is not found.

``<log_name>ReportServer</log_name>``
   Defines log file name for output and is used in combination with ``log_dir``. If
   no ``log_name`` is defined, the output file's name is ``sysmond_processname``.

   .. note::
      This only applies when ``log_file`` is not found.

``<log_stdout>true</log_stdout>``
   Defines log level. Includes ``log_stderr``.

``<log_stderr>true</log_stderr>``
   Defines log level. ``log_stderr`` is also used to set the extension on the log file.

.. _sysmond.ping_interval:

``<ping_interval>10</ping_interval>``
   Frequency for pinging a process in seconds. Only applicable on HA-processes and processes monitored with the Application ping protocol, see
   :ref:`sysmond.application_ping_protocol`.

``<ping_retries>3</ping_retries>``
   Number of times for pinging a process, default value is ``3``. Only applicable on
   HA-processes and processes monitored with the Application ping protocol, see :ref:`sysmond.application_ping_protocol`.

``<ping_timeout>5</ping_timeout>``
   Interval in number of seconds allowed for the process to answer the ping
   request before timeout, default value is ``5``. This value should be lower than the
   value set in ``ping_interval``. Only applicable on HA-processes and processes
   monitored with the Application ping protocol, see :ref:`sysmond.application_ping_protocol`.

``<restart>true</restart>``
   Process should restart if it stops/crashes. Not applicable on process group.

``<run_as>carmen</run_as>``
   Defines if the process should be started as another user. This requires that
   Sysmond has appropriate privileges.

``<start_cmd>$CARMSYS/etc/scripts/myScript</start_cmd>``
   Command to start the process.

``<start_attempts>15</start_attempts>``
   Maximum number of start attempts. After this number of start attempts, the
   process will be put in an ``failed`` status and no more automatic start commands for the process will be executed.

``<start_attempts_aggressive>3</start_attempts_aggressive>``
   Maximum number of start attempts without waiting.

``<start_attempts_delay_time>60</start_attempts_delay_time>``
   Time (in seconds) that a process waits between start attempts after
   ``start_attempts_aggressive`` has been run.

``<start_wait_time>10</start_wait_time>``
   Minimum time (in seconds) that a process should run before it is considered
   successfully started.

``<stop_cmd>$CARMSYS/etc/scripts/myScript</stop_cmd>``
   Command to stop the process.

``<stop_sig>15</stop_sig>``
   Signal to stop the process. ``15`` is default value.

.. _sysmond.stop_wait_time:

``<stop_wait_time>10</stop_wait_time>``
   The wait time in seconds to wait for stop command completion before stopping the process via signal(s).

.. _sysmond.task_properties:

Task properties
+++++++++++++++

You can configure tasks consisting of one or more actions to be executed at
certain intervals. As tasks are defined in a namespace, the following applies:

* Tasks defined in the Sysmond program namespace are valid for all Sysmond instances using this configuration.
* Tasks defined in the Sysmond process namespace are specific for that process.

Tasks are scheduled by configuring ``cron`` entries under the ``crontab`` tag. The
``cron`` entry must have a timespec attribute which is similar to a line in a
``crontab`` file. The first position is minutes (0-59), the second position is hours
(0-23), the third position is day in month (1-31), the fourth position is month
(1-12), and the fifth position is weekday (0-6). Ranges and series are allowed,
for example 10, 20, 30, 40-50. All positions can be an asterisk ''"\*"'', which
means the whole range.

Example::

  <crontab>
    <!-- runs the task repeatedly 15 minutes after midnight the 1:st every month-->
    <cron timespec="15 0 1 * *">TASK_1/cron>
    <! runs the task just once-->
    <cron timespec="2011-10-15 13:45">TASK_2/cron>
  </crontab>

.. _sysmond.limits:

Limits
++++++

The limits can be defined in a ``program`` namespace, or in a ``process`` namespace. The following limits can be defined:

* min
* max

In the example, the following limits are defined: minimum limit for CPU,
maximum limit for FDS and minimum and maximum limit for MEM. If different actions
are needed when the minimum or maximum limit is reached, then it must be specified separately.

Example::

  The example code is part of a process configuration.
  <x/path/to/a/process
  x/path/to/a/process
  <limits>
    <cpu_limit min="0">
    ...
    </cpu_limit>
    <fds_limit max="32">
    ...
    </fds_limit>
    <mem_limit min="0" max="2000">
    ...
    </mem_limit>
  </limits>

Email notifications
+++++++++++++++++++
It is possible to send notifications per email. You can define a global email
recipient per program or one email recipient per Sysmond instance. If no
email recipient is defined for a specific Sysmond instance, the global email
recipient defined on program level is used.

.. admonition:: Example

   The example code is part of the configuration in ``$CARMUSR/etc/sysmond.xml``.
  
   For the ``SYSMOND_1`` process, email will be sent to Nisse Blixt, for the
   ``SYSMOND_2`` process, email will be sent to Berra Blixt.
   
   ::
   
     <programs>
       <program>
       <!-- all configuration for all Sysmond processes -->
       <!-- global email recipient, send mail to "Berra Blixt" -->
         <mail>
           <mail_to>berra.blixt@hotmail.com</mail_to>
         </mail>
       <!-- Mail configuration for this Sysmond instance, send mail to "Nisse Blixt" -->
       <process name="SYSMOND_1">
         <mail>
           <mail_to>nisse.blixt@hotmail.com</mail_to>
         </mail>
       </process name>
       <!--No specific mail configuration for this Sysmond instance-->
       <process name="SYSMOND_2">
       </process">
       </program>
     </programs>

.. _sysmond.system_configuration:

System Configuration
^^^^^^^^^^^^^^^^^^^^
Sysmond is responsible for starting and monitoring the different background
processes.

In the common configuration, Sysmond scans the ``hosts`` definitions and for
each ``host``, it finds the names of the processes to start within ``start`` tags. It
will start and monitor all the processes listed in the ``start`` tags for its host.
These processes are defined in ``program/process`` definitions, typically with
one XML file for each type of background process.

.. note::
   To add a process, the declaration must include the ``program`` level.

Common Sysmond settings
+++++++++++++++++++++++
The definition of the Sysmond processes and common Sysmond settings are
typically located in ``$CARMUSR/etc/sysmond/$CARMSYSTEMNAME.xml``.

Example:

.. literalinclude:: ../../../../etc/sysmond/PROD.xml

CarmLog
   You can set CarmLog settings on program, process or global level, see :ref:`carmlog`.

Services
   Services are defined in ``sysmond.xml`` for each Sysmond instance:

   Example::

     <service name="sysmond_1" protocol="http" nr_ports_"2"/>

   The portbase for each host defines the URL for contacting the local Sysmond
   process in ``host.xml``. The value in ``sysmond_ref`` has to be identical to the
   process name defined in ``sysmond.xml``. An example:
   
   Example::

     <host name="reddog" hostname= "reddog" portbase="21000" sysmond_ref="SYSMOND_1">

Configuration of processes
++++++++++++++++++++++++++
Configuration of processes is done in ``<program>.xml`` file. Here you define
start and stop, limits, log settings, ping interval, exit actions, etc. An example:

Example::

  <!-- Process configuration -->
  <programs>
    <program name="Prog_Ett">
      <process name="Proc_1">
        <start_cmd>${CARMUSR}/etc/Test_1.sh</start_cmd>
        <start_wait_time>10</start_wait_time>
        <start_attempts>15</start_attempts>
        <start_attempts_aggressive>5
        </start_attempts_aggressive>
        <start_attempts_delay_time>30
        </start_attempts_delay_time>
        <stop_cmd>pkill -15 Test_1.sh</stop_cmd>
        <stop_sig>9</stop_sig>
        <stop_waittime>5</stop_waittime>

    <!-- MIN Limit definition -->
    <cpu_limit min="25">
      <msg type="mail">Min CPU-Limit violation (Process_1)
      </msg>
    </cpu_limit>

    <!-- MAX Limit definition -->
    <cpu_limit max="75">
      <msg type="mail">CPU-Limit violation (Process_1)
      </msg>
    </cpu_limit>
    <!-- Combined limit definition -->
    <cpu_limit min="25" max="75">
      <msg type="mail">Max CPU-Limit violation (Process_1)
      </msg>
    </cpu_limit>

    <!-- Other limit types -->
    <!-- Virtual memory -->
    <mem_limit></mem_limit>
    <!-- "real" memory usage -->
    <rss_limit></rss_limit>
    <!-- Used/open filedescriptors -->
    <fds_limit></fds_limit>
    <!-- Ping interval, required for HA-processes -->
    <ping_interval>15</ping_interval>
    <!-- Setting of HA-process property -->
    <ha_process>true</ha_process>
    <!-- "Log" settings for process (redirection of stdout & stderr) -->
    <!-- "NOTE! The default is to redirect
    stdout & stderr to /dev/null. In order to
    catch the output on stderr or stdout it MUST be
    configured per process. -->
    <!-- Define logfile-name (with full path) -->
    <log_file>${CARMUSR}/logfiles/Prog_Ett</log_file>
    <!-- OR define log-directory & name separately ignored if log_file is defined-->
    <!-- log_dir defaults to /tmp -->
    <!-- log_name defaults to 'sysmond_' + process name -->
    <log_dir>${CARMUSR}/logfiles</log_dir>
    <log_name>Prog_Ett</log_name>
 
    <!-- What to redirect: if both == true redirect
    stdout & stderr to separate files
    (log_file + extension .out / .err)
    if only log_stdout == true to redirect
    stdout & stderr to 1 file (log_file + extension .log)
    if only log_stderr == true to redirect stderr to
    -a file (log_file + extension .err)-->
    <log_stdout>true</log_stdout>
    <log_stderr>false</log_stderr>

    <!-- Exit actions for the process -->
    <!-- Exit failed executed when a process fails to start -->
    <exit failed="true">
      <msg type= "mail">Proc_1 failed to start</msg>
    </exit>
    <!-- Exit caused by specific signal
    (in this example 15 ===SIGTERM)-->
    <exit signal="15">
      <msg type= "mail">Proc_1 Exited SIG-15</msg>
    </exit>
    <!-- Process exited with result code (in this example 3)-->
    <exit result="3">
      <msg type= "mail">Proc_1 Exited with code 3</msg>
    </exit>
    <!-- "Default" exit task, executed if no other exit task was executed -->
    <exit always="true">
      <msg type= "mail">Proc_2 Exited</msg>
    </exit>

        </process>
      </program>
    </programs>

Process groups
++++++++++++++
Definition of process groups is done in separate configuration files. Process
groups are used when starting different processes with one command. An example:

Example::

  <!-- Definition of process group -->
  <process_group name="HA_1">
    <comment>HA process to be active on Sysmond 1</comment>
    <start>Process_1</start>
    <start>Process_2</start>
  </process_group>

The start of processes and active or standby state for the HA-processes is configured in ``host.xml``. An example:

Example::

  <!-- Configuration of process groups, in this case HA_1
  and HA_2 are process groups while Aclient is a separate
  process. -->
  <hosts>
    <host name="reddog" hostname= "reddog" portbase="21000" sysmond_ref="SYSMOND_1">
    <start active="true">HA_1</start>
    <start active="false">HA_2</start>
    <start active="true">Aclient</start>
    </host>
    <host name="rakanda" hostname= "rakanda" portbase="22000" sysmond_ref="SYSMOND_2">
    <start active="false">HA_1</start>
    <start active="true">HA_2</start>
    <start active="false">Aclient</start>
    </host>
  </hosts>

Scheduling maintenance programs
+++++++++++++++++++++++++++++++
Sysmond supports functionality similar to cron jobs (tasks) for scheduling
maintenance programs, for example calculation of accumulator values. The
tasks are typically executed by customer-specific scripts in the CARMUSR.
An example:

Example::

  <!-- Crontab entry min, hour, day, month, weekday -->
  <!-- Note use of previously defined task -->
  <crontab>
    <cron timespec="* * * * *">TASK_ETT</cron>
  </crontab>

.. _sysmond.installation:

Installation
------------
Server setup for Sysmond is described in *System Reference Manual*.
Creating and installing a CARMUSR Release, Sysmond-specific steps, are
described in *System Reference Manual*.


.. _sysmond.using_sysmond:

Using Sysmond
-------------

* :ref:`sysmond.scripts_and_binaries`
* :ref:`sysmond.starting_and_stopping_sysmond`

.. _sysmond.scripts_and_binaries:

Scripts and binaries
^^^^^^^^^^^^^^^^^^^^
The following scripts and binaries are used:

* ``CARMSYS/etc/scripts``
* ``CARMSYS/bin/$ARCH``

.. note::
   See also *Functional Reference manual*

.. _sysmond.using_the_sysmond_cli:

Using the Sysmond command line interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The commands described in this section are executed as arguments to the
``sysmondctl`` program. This is a small Python script that communicates with
Sysmond via TCP on Sysmond's configured TCP-port.

.. _sysmond.flags:

Flags
+++++
The ``sysmondctl`` script takes the following optional flags:
.. note::

   Usage: ``sysmondctl [flags] <command>``

``-h``
   Show this usage test (same as command ``sysmondctl help``).
``-v``
   Verbose, e.g. show XML commands sent to Sysmond instance.
``-f``
   Send the contents of the XML file ``"<command>"`` to local Sysmond instance.
``-d``
   Use the debug compiled version of Sysmond if available.
``-D``
   Do not daemon()-ize Sysmond instance (only useful for debugging).
``-S``
   When using ssh to start/stop Sysmond on remote hosts, create a special
   ssh key pair (``$HOME/.ssh/sysmondctl_rsa``) to use instead of the
   default. (The ``sysmondctl_rsa`` key will always be used if it exists.)

.. _sysmond.starting_and_stopping_sysmond:

Starting and stopping Sysmond
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _sysmond.starting_sysmond:

Starting Sysmond
++++++++++++++++
You can start Sysmond in a number of ways. There are three different ways to
start Sysmond:

The first way to start Sysmond:

* Enter ``$ sysmondctl start``
  The ``sysmondctl`` script with ``start`` as its argument will start Sysmond.
  This starts the application Sysmond and sends a ``start`` command.

The second way to start Sysmond:

#. Enter ``$ sysmondctl init``
   This command starts Sysmond but not the node. When Sysmond is started
   it enters an ``idle`` state, which means that the system configuration is read,
   all control threads are started but the node (the host Sysmond is controlling including all its configured processes) is still stopped. No process is
   started or monitored and the cron scheduler does not run any configured tasks.
#. Enter ``$ sysmondctl start``
   Sysmond performs a node start. All threads gets unlocked and all configured processes for the node are started and monitored. Sysmond is now in
   its operational mode.

The third way to start Sysmond:

#. Enter $ sysmondctl attach
   Starts Sysmond in ``idle`` mode and attaches to the processes that were left
   running when Sysmond was stopped with the ``detach`` command.
#. Enter $ sysmondctl start
   Sysmond performs a node start. All threads gets unlocked and all configured (not attached) processes are started and monitored.

Starting nodes
++++++++++++++
When running on multiple nodes there needs to be one Sysmond instance on
each node. The ``sysmondctl`` tool connects to one ``sysmond`` but can give a command to any other ``sysmond`` that is configured. Most of the actions can operate
either on local node or any remote node or the whole system.

Use the ``start`` command to start nodes:

Local node
""""""""""
To start the local node, use ``sysmondctl start``.

Remote nodes
""""""""""""
For remote nodes, this works in the following ways:

* To start remote nodes when Sysmond is in ``idle`` or ``passive`` mode (the
  result of ``sysmondctl init``, ``attach``, or ``stop``), the ``sysmondctl start node= "remote hostname"``
  command will bring the remote node fully online.
* If there is no remote Sysmond running, ``sysmondctl start node="remote hostname"``
  will attempt to start Sysmond on the remote node using SecureShell (ssh). This requires both the local and remote node to
  have a common home directory for the logged-in user, i.e. ``$HOME``, and the SecureShell daemon (sshd) on the remote node needs to permit public-key
  authentication. See the ``-s`` option to ``sysmondctl``, as described in :ref:`sysmond.flags`.
* To start all nodes in the system including the remote nodes, use
  ``sysmondctl start node="system"``. This also requires both the local and
  remote node to have a common home directory for the logged-in user, i.e.
  ``$HOME``, and the SecureShell daemon (sshd) on the remote node needs to
  permit public-key authentication. See the ``-s`` option to ``sysmondctl``, as
  described in :ref:`sysmond.flags`.

Starting processes on nodes
+++++++++++++++++++++++++++
Many actions can also take a value, often that will be a process name, and will then only apply to that entity, for example:

.. admonition:: Example

   To start PROCESS1 on local node:
   ::
   
     sysmondctl start PROCESS1

   To start PROCESS1 on remote node:
   ::

     sysmondctl start PROCESS1 node="remote node"

   To start PROCESS1 on all nodes:
   ::

     sysmondctl start PROCESS1 node="system"

A process must be configured to run on a node for start to accept a ``start``
command. If not, but the process is configured for another node the check can
be overridden with the attribute ``forced="true"``, for example:

.. admonition:: Example

   ::
   
     sysmondctl start PROCESS2 forced="true"

   This will start PROCESS2 on local node even if not configured to be started on it.

.. _sysmond.stopping_sysmond_and_nodes:

Stopping Sysmond and nodes
++++++++++++++++++++++++++

* To stop the node but not Sysmond, enter:
  ::
   
    $ sysmondctl stop

  This stops all controlled processes and Sysmond enters the ``passive`` mode.
 
* To stop the local node and Sysmond, enter:
  ::
   
    $ sysmondctl shutdown alternatively
    $ sysmondctl exit

  These commands stop all processes and Sysmond is shut down.
 
* To stop the remote node and Sysmond, enter:
  ::

    $ sysmondctl shutdown node= "remote hostname"


  This requires both the local and remote node to have a common home
  directory for the logged-in user, i.e. ``$HOME``, and the SecureShell daemon
  (sshd) on the remote node needs to permit public-key authentication. See
  the ``-s`` option to ``sysmondctl``, as described in :ref:`sysmond.flags`.

* To stop Sysmond, but not the processes enter:
  ::
   
    $ sysmondctl detach

  This command is used to save the controlled processes states on disk, for
  use when starting Sysmond with the ``attach`` command. The controlled
  processes are left running when Sysmond shuts down.

.. _sysmond.appendix_list_of_cli:

Appendix: List of CLI commands
------------------------------
This appendix lists the available commands in alphabetical order. Each commands maps to an action. The commands are used in the sysmondctl script,
see :ref:`sysmond.using_the_sysmond_cli`.

.. note::
   For all commands, the attribute ``[node="hostname"]`` is supported except for
   the ``exit``, ``attach``, and ``detach`` commands.

   If the node argument is left out, the command is run on the local node.

   If the value of node is set to "system" ``[node="system"]``, the command is run
   on all the configured Sysmond-nodes.

   Usage ``sysmondctl command [Process|Group]``:
   
   The command is performed on the specified process or the process in the
   group,. If no ``process|group`` is given, the command is performed to the local
   Sysmond process. For the ``info``, ``status``, and ``history`` commands information
   is provided on all processes on the local node.

**about**
   ``sysmondctl about``
   
   Display Sysmond's version number and compilation date.

.. _sysmond.active:

**active**
   ``sysmondctl active PROCESS [forced="true|false"]``
   
   Applicable to HA-processes and processes monitored with the application
   ping protocol. Switch the process or process group to active.
   
   .. note::
      All applications running in High Availability mode need to implement the client part of this service.

**at**
   ``sysmondctl at timespec="crontab spec|now" TASK``
   
   Schedule an action or a task to run at a specific date and time.

   Example::

    sysmondctl at timespec="15 0 1 * *" TASK_1
    sysmondctl at timespec="2011-07-07 12:33" TASK_1
    sysmondctl at timespec="now" TASK_1

**attach**
   ``sysmondctl attach``
   
   Starts Sysmond in ``idle`` mode and attaches to the processes that were left running when Sysmond was stopped with the ``detach`` command.

**detach**
   ``sysmondctl detach``

   Exits Sysmond on ``host`` without stopping the controlled processes.

**exec**
   ``sysmondctl exec 'cmd args'``

   Execute command.

**exit**
   ``sysmondctl exit``

   Shut down Sysmond instances only on a local node. See :ref:`sysmond.stopping_sysmond_and_nodes`.

**help**
   ``sysmondctl help`` or
   ``sysmondctl -h``

   Lists the usage text for ``sysmondctl`` commands.

**history**
   ``sysmondctl history [PROCESS|GROUP] [head="1" | tail="10"]``

   For each process, list the first (``head``) and last (``tail``) events (max 100) that occurred for the process.

**init**
   ``sysmondctl init``

   This command starts Sysmond but not the node, see :ref:`sysmond.starting_sysmond`.

**info**
   ``sysmondctl info [PROCESS|GROUP] [verbose="true|false"]``

   Return information for each process on one row.

**list**
   ``sysmondctl list [config|processes|tasks|starts|crontab]``

   List information about processes and tasks.

**monit**
   ``sysmondctl monit pid="1234" | PROCESS``

   Using pid, adds an arbitrary pid to report status for. When used with a process
   name the process is put into ``monitor_only`` status.

**msg**
   ``sysmondctl msg [type="log|mail"] "The message to log/send"``

   Send message text to log file or email.

**ping**
   ``sysmondctl ping PROCESS``

   Ping the processes and display process status. Attribute ``system`` = pings all
   processes. Display status on High Availability and Aping processes. If no
   process is entered, the status of the Sysmond process is displayed.

**restart**
   ``sysmondctl restart PROCESS | GROUP``

   Restart process.

**shutdown**
   ``sysmondctl shutdown [node="hostname"]``

   Shut down Sysmond instances on a local node if no specific node is specified.
   If ``node="system"``, all Sysmond instances are shut down, see :ref:`sysmond.stopping_sysmond_and_nodes`.

**standby**
   ``sysmondctl standby PROCESS|GROUP``

   Only applicable to HA-processes. Switch the process or process group to
   standby. See also :ref:`active <sysmond.active>` and :ref:`switch <sysmond.switch>`.

**start**
   ``sysmondctl start PROCESS|GROUP [forced="true|false"]``

   Start process, process group or node, see :ref:`sysmond.starting_sysmond`.

**status**
   ``sysmondctl status PROCESS|GROUP [verbose="true"]``

   For each process, generate a short status text saying if the process is running or not.

**stop**
   ``sysmondctl stop PROCESS|GROUP``

   Stop process, process group or node, see :ref:`sysmond.stopping_sysmond_and_nodes`.

.. _sysmond.switch:

**switch**
   ``sysmondctl switch PROCESS [restart="true|false"]``

   Only applicable to HA-processes. Switch the state of the process or process
   group from ``active`` to ``standby`` and vice versa. When ``restart="true"``, the
   following happens:

   #. The standby process (process x) is first restarted and set to ``standby``.
   #. The active process (process y) is set to ``standby``. Both process x and process y are now in ``standby``.
   #. The standby process (process x) is set to ``active``.
   #. Lastly, the previously active process (process y) is restarted and set to ``standby``.

   When ``restart="false"``, the following happens:

   #. The active process (process y) is set to ``standby``. Both process x and process y are now in ``standby``.
   #. The standby process (process x) is set to ``active``.

   .. note::
      It is possible to set a HA process to active, even if it already is active on another node by using ``forced="true"``.

**unmonit**
   ``sysmondctl unmonit pid="1234" | PROCESS``

   Remove an arbitrary PID, which was added by ``sysmondctl monitor``. Or, for
   a configured process, clear the ``monitor_only`` (switch back to normal process
   control).
