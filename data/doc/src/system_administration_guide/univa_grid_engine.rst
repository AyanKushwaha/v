Univa Grid Engine
=================

The Univa Grid Engine batch system is used to queue and run jobs. This system
provides fast parallel execution by distributing compilation and other batch
jobs to available machines in the network.

Documentation about the Univa Grid Engine can be downloaded from: http://www.univa.com/products/grid-engine.php

.. _univa_grid_engine.univa_grid_engine_installation:

Univa Grid Engine installation
------------------------------

This is a short version on how to install Univa Grid Engine. Please see the full
documentation which is provided with the Univa installation package.

#. Create a user account and a group for the batch administrator, for example
   ``sgeadmin:sge``. An alternative is to reuse an existing account like ``batch:carm``. The examples in this text assume the user ``batch:carm``.
#. Register two ports, ``sge_qmaster`` and ``sge_execd``, by editing the file
   ``/etc/services`` on the master host, the NIS server or wherever ports are defined for the site. The recommended port numbers (registered at IANA)
   are as follows:
   
   * ``sge_qmaster=6444/tcp``
   * ``sge_execd=6445/tcp``

#. Log in as root on the host that should run the master daemon.
#. Create a directory for the installation, for example ``/opt/uge-8.0.3``. The
   directory must be mounted and be accessible with the same path name on
   all hosts in the cluster. The administrator user must own the directory and
   have the same group ID. Set the environment variable ``SGE_ROOT`` to point
   to this directory.


#. Untar the tarball with the common files and the relevant tarball with the
   architecture-dependent files.

#. Set the file permissions:
   
   ``util/setfileperm.sh $SGE_ROOT``
#. Run the install script for qmaster with default options for everything:
   
   ``./install_qmaster``
   
   ``(user batch, group carm, cell name=default, use berkeley db,
   no spooling server, group id range 20000-20100, no shadow,
   start daemons at boot, Host(s)=all hosts in the cluster, no
   shadow host, default configuration)``

#. Log in as root on each machine in the cluster and install the execution daemons using the default options for everything:
   
   ``cd $SGE_ROOT``
   
   ``./install_execd``

#. Add the relevant user name for Jeppesen support, which needs access as
   manager. The example assumes the login name ``carmen``.

   Example::

     qconf -am carmen

Univa Grid Engine configuration
-------------------------------

This instruction configures Univa Grid Engine for a Jeppesen system.

Prerequisites
^^^^^^^^^^^^^

* Univa Grid Engine software must be installed and the daemons should be up
  and running before the cluster can be configured. See :ref:`univa_grid_engine.univa_grid_engine_installation`.
* To change the configuration, you must be registered as a manager for SGE.
* All commands in this instructions should be run in a system shell.
* If defined, the environment variable ``EDITOR`` is used for selecting a text
  editor when required.

Configuration of the complex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following set of requested complex variables has to be defined.

==================== ======== =============== =======================================================================================
Complex variable     Type     Values          Description
==================== ======== =============== =======================================================================================
``apc``              BOOL     True/False      Host/Queue open for APC jobs.
``matador``          BOOL     True/False      Host/Queue open for Crew Rostering Optimizer jobs.
``publisher``        BOOL     True/False      Host/Queue open for Rave Publisher jobs.
``rave``             BOOL     True/False      Host/Queue open for Rave compilations.
``studio``           BOOL     True/False      Should be set to true, to enable the Session Server to find servers to start Studio on.
``carmrun<n>``       BOOL     True/False      Host configured for running Carmen version <n>.
``carmbuild<n>``     BOOL     True/False      Host configured for compiling Carmen version <n>.
``carmarch``         RESTRING See table below Platform architecture.
==================== ======== =============== =======================================================================================

.. note::

   To enable Rave compilations, both ``carmbuild<n>`` and ``rave`` must be set to ``true``.

The following table lists the supported platforms:

==================== ================== ==================
Platform             CARMSYS/bin/$ARCH  carmarch value
==================== ================== ==================
Red Hat Linux 64-bit ``x86_64_linux``   ``x86_64_linux``
SUSE Linux 64-bit    ``x86_64_suse``    ``x86_64_suse``
Sun Solaris 64-bit   ``x86_64_solaris`` ``x86_64_solaris``
==================== ================== ==================

See *System Requirements* for detailed specifications of the supported platforms.

To configure the complex, do as follows:

#. Create a text file named ``complex`` with the following contents (for Carmen version <n>)::
   
     apc apc BOOL == YES NO FALSE 0
     carmarch carmarch RESTRING == YES NO NONE 0
     carmbuild<n> carmbuild<n> BOOL == YES NO FALSE 0
     carmrun<n> carmrun<n> BOOL == YES NO FALSE 0
     matador matador BOOL == YES NO FALSE 0
     publisher publisher BOOL == YES NO FALSE 0
     rave rave BOOL == YES NO FALSE 0
     studio studio BOOL == YES NO FALSE 0

#. Register the complex variables by running the command::

     qconf -Mc complex

#. The complex variables can be displayed with the command::
      
     qconf -sc

   and edited with the command::
    
     qconf -mc

   See ``man qconf`` for more details. The configuration can also be viewed and
   modified from the ``qmon`` GUI. See ``man qmon`` for more details.

Configuration of submission hosts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All hosts running Studio should be enabled as submit and administrative
hosts, but they do not have to run any daemons.

The following commands register a host called ``portmoller``::

  qconf -as portmoller
  qconf -ah portmoller

The first command adds a submit host, and the second an administrative host.

.. note::

   The commands must be run on a host that is already registered as administrative host.
   At least one administrative host must be configured when installing the cluster.

Configuration of execution hosts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
All hosts that should be used as execution hosts must have the daemon
installed and started prior to the configuration.

The complex variables model the capabilities of an execution host, and the
Jeppesen specific complex variables must be configured for each execution
host in the cluster.

#. On each execution host, enter the following command to check that the daemon is running::
   
     ps -e | grep sge_exec

   The command should report a running process. If installed but not running, the daemon can be started by the user root with the command::
   
     start $SGE_ROOT/$SGE_CELL/common/sgeexecd

   Check the log file in    $SGE_ROOT/$SGE_CELL/spool/<hostname>/messages``.
   If the daemon cannot connect to qmaster, or write to the spool
   directory, the log file is created in ``/tmp``.

#. On each execution host, use the ``qconf`` command to configure the complex variables listed in the table `univa_grid_engine.configuration_of_the_complex`.
   
   The ``qconf`` syntax is::
      
     qconf -aattr exechost complex_values <variable> <hostname>

   where ``variable`` is a name=value pair that defines a complex variable,
   for example ``apc=true``. See examples in the next section.

Execution host configuration examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following examples show how each complex variable may be configured.

.. admonition:: Example 1

   ::
   
     qconf -aattr exechost complex_values carmarch=x86_64_linux portmoller

   Configures the host ``portmoller`` as a 64-bit Linux machine.

.. admonition:: Example 2

   ::
  
     qconf -aattr exechost complex_values carmrun16=true portmoller

   Configures the host ``portmoller`` as a machine where the system can run.

.. admonition:: Example 3

   ::
   
     qconf -aattr exechost complex_values carmbuild16=true rave=true portmoller

   Configures the host ``portmoller`` as a machine where the system can compile rule sets.

.. admonition:: Example 4
   
   ::
   
     qconf -aattr exechost complex_values carmbuild16=false landvetter

   Configures the host ``landvetter`` as a machine where the system cannot compile rule sets.

.. admonition:: Example 5
   
   ::
   
     qconf -aattr exechost complex_values apc=true portmoller
     qconf -aattr exechost complex_values matador=true portmoller
     qconf -aattr exechost complex_values publisher=false portmoller
     qconf -aattr exechost complex_values rave=false portmoller

   Configures the host ``portmoller`` to accept APC and Crew Rostering Optimizer
   jobs, but no batch reports or Rave compilations.

.. note::
   
   The complex variable studio is reserved for future use, and should be set to
   ``false`` on all execution hosts for the time being::

     qconf -aattr exechost complex_values studio=false `qconf -sel`

Displaying and editing the host configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The configuration of a host can be displayed with the command::
  
  qconf -se <hostname>

The configuration of a host can be edited with the command::
  
  qconf -me <hostname>

See ``man qconf`` for more details. The configuration can also be viewed and
modified from the graphical user interface ``qmon``. See ``man qmon`` for more
details.

Checking the host configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use the command ``qhost`` to check the host configurations. The result is filtered with respect to the complex values defined on the hosts. Note that
``global`` is a special object and not a host.

.. admonition:: Example 1

   ::
   
     qhost -l carmrun16=true,apc=true
     qhost -l carmrun16=true,matador=true
     qhost -l carmrun16=true,publisher=true

   Lists the hosts that are open for APC, Crew Rostering Optimizer and batch reports.

.. admonition:: Example 2

   ::
   
     qhost -l carmbuild16=true,rave=true

   Lists the hosts that are open for Rave compilations.

.. admonition:: Example 3

   ::
   
     qhost -l carmbuild16=true,rave=true,carmarch='x86_64*'

   Lists the hosts that are able to run a particular architecture by adding a resource requirement for ``carmarch``.

Configuration of queues
^^^^^^^^^^^^^^^^^^^^^^^
.. note::
  
   The resource studio is currently not used, but still defined as it will be used by future Jeppesen releases.
 
#. The ``all.q`` queue is configured by default when installing SGE. It can be
   used without modifications as the only queue, but it is recommended to
   either remove this queue, or to disable it for Jeppesen jobs.
   To completely remove ``all.q`` issue the command::
     
     qconf -dq all.q

   To keep ``all.q`` but disable it for all Jeppesen jobs::
   
     qconf -aattr queue complex_values apc=false all.q
     qconf -aattr queue complex_values carmbuild<n>=false all.q
     qconf -aattr queue complex_values carmrun<n>=false all.q
     qconf -aattr queue complex_values matador=false all.q
     qconf -aattr queue complex_values rave=false all.q
     qconf -aattr queue complex_values studio=false all.q
     qconf -aattr queue complex_values publisher=false all.q

#. Add a queue named ``opt`` by running the command::

     qconf -aq opt

   An editor showing the queue configuration for the new ``opt`` queue is displayed. Close the editor without changing the configuration.
  
   ``opt`` will be the default queue for all Jeppesen batch jobs, except Rave compilations. The name ``opt`` is not mandatory.

#. Add a queue named rave::

     qconf -aq rave

   ``rave`` will be the default queue for all Jeppesen Rave compilations. The name ``rave`` is not mandatory.

#. It is recommended that the ``opt`` and ``rave`` queues are attached to all hosts
   in the cluster through the host alias ``@allhosts``::

     qconf -aattr queue hostlist @allhosts opt rave

   In this way, new hosts added in the future automatically appear in the queues.

#. If there is a preferred order to allocate hosts for jobs, which is usually the
   case if some hosts are faster than others, the allocation order can be configured by setting the sequence order. The following example assumes that
   there are two identical fast hosts named ``one`` and ``two``, and one slow host
   with the name ``three``.

   .. admonition:: Example 1

      First, configure the scheduler to use sequence numbers::
   
        qconf -msconf

      Change the line ``queue_sort_method load`` to ``queue_sort_method seqno`` in the displayed editor, then save and exit.
   
      Configure the opt and rave queues to first use the faster machines one
      and two by giving them a lower sequence number::
   
        qconf -rattr queue seq_no '0,[one=1],[two=1],[three=2]' opt
        rave

      (Sequence number 0 will be the default value for all hosts that are not given a specific value.)

#. Remove any load thresholds from the ``opt`` and ``rave`` queues::

     qconf -rattr queue load_thresholds none opt rave

   Thresholds are primarily interesting when configuring queues for low priority jobs.

#. Set the priority for the jobs in the ``opt`` queue to be of lower priority than
   Rave compilations (higher number gives lower priority)::
   
     qconf -rattr queue priority 0 rave
     qconf -rattr queue priority 10 opt

#. Allow the queues to be restarted::

     qconf -rattr queue rerun true opt rave

   This will allow jobs to be restarted in case a host becomes unavailable during the execution of a job.

#. Configure the number of slots the queues should have on each host. It is recommended to use one slot per processor.

   .. admonition:: Example 2

      The following example assumes that the hosts ``one`` and ``two`` have four
      processors, and all other hosts have two processors.::
     
        qconf -rattr queue slots '2,[one=4],[two=4]' opt rave

#. Open the ``opt`` queue for optimization jobs and batch reports, but close it
   for other types of Jeppesen jobs::
   
     qconf -aattr queue complex_values apc=true opt
     qconf -aattr queue complex_values matador=true opt
     qconf -aattr queue complex_values rave=false opt
     qconf -aattr queue complex_values studio=false opt
     qconf -aattr queue complex_values publisher=true opt

#. Open the Rave queue for Rave compilations, but close it for other types of
   Jeppesen jobs::
   
     qconf -aattr queue complex_values apc=false rave
     qconf -aattr queue complex_values matador=false rave
     qconf -aattr queue complex_values rave=true rave
     qconf -aattr queue complex_values studio=false rave
     qconf -aattr queue complex_values publisher=false rave

#. The queue configurations can be displayed with the commands::

     qconf -sq opt
     qconf -sq rave

   and edited with the commands::
   
     qconf -mq opt
     qconf -mq rave

   See ``man qconf`` for more details.

   The configuration can also be viewed and modified from the graphical
   user interface qmon. See man qmon for more details.

#. Use the command ``qselect`` to check the queue instances. The result will
   be filtered with respect to the complex values defined on the host and on
   the queue.

   .. admonition:: Example 3

      ::
   
        qselect -l carmrun16,apc
        qselect -l carmrun16,matador
        qselect -l carmrun16,publisher

      Lists the queue instances that are open for APC, Crew Rostering Optimizer and batch reports.

   .. admonition:: Example 4

      ::
     
        qselect -l carmbuild16,rave

      Lists the queue instances that are open for Rave compilations.
  
   You can also list the queue instances that are open for a particular architecture by adding a resource requirement for carmarch.
   For the Rave compilations to work it is absolutely necessary that there is at least one open
   queue instance for each platform that the CARMUSR is configured to
   compile rules for. Check the variables ``GPC_ARCHS``, ``APC_ARCHS`` and
   ``MATADOR_ARCHS`` in ``$CARMSUR/CONFIG.extension.site``, or anywhere else where these variables are defined, to get the actual configuration.

   .. admonition:: Example 5

      ::
      
        qselect -l carmbuild16,rave,carmarch='x86_64_linux*'

Setting up environment for parallel APC and building Rave rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a new parallel environment for APC with the command ``qconf -ap apc`` with the following parameters:

===================== =============
Parameter             Value
===================== =============
``pe_name``           ``apc``
``slots``             ``999``
``user_lists``        ``NONE``
``xuser_lists``       ``NONE``
``start_proc_args``   ``/bin/true``
``stop_proc_args``    ``/bin/true``
``allocation_rule``   ``$pe_slots``
``control_slaves``    ``TRUE``
``job_is_first_task`` ``TRUE``
``urgency_slots``     ``max``
===================== =============

Enable the ``apc`` environment in all queues that should run APC jobs with the
following command (assuming a queue name ``opt``)::

  qconf -aattr queue pe_list apc opt

Advanced configurations
^^^^^^^^^^^^^^^^^^^^^^^
Expert administrators may add additional queues as described in the SGE
manuals. A Jeppesen system will not request any particular queue name, but
will use the resource requirements above when submitting jobs.

Additional resource requirements and command line parameters for qsub can
be defined in the external table:

``$CARMUSR/data/config/SGEOptions.etab``

(template in ``$CARMSYS/data/config/SGEOptions.etab``).

The pick-list displayed in the Submit form in Studio is generated from the
first column. The corresponding string in the second column is used as extra
parameters for ``qsub`` when submitting optimization jobs or batch reports.
There is currently no similar way to add extra parameters for Rave compilations.

See ``man qsub`` for further details on parameters for ``qsub``.

Separate queues for master job and helper jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For rostering optimization jobs it is possible to have two sets of resource
requirements and command line parameters, one for the master job and one
for the helper jobs.

Add a new external table, ``SGEHelperOptions.etab`` with the same format as
SGEOptions.etab and place it in the same directory, ``$CARMUSR/data/config``.
Define the master job resource requirements and command line
parameters in ``SGEOptions.etab`` and the helper job resource requirements
and command line parameters in ``SGEHelperOptions.etab``.

When starting an optimization job, the **Batch Options** pick-list will read
from ``SGEOptions.etab``, while the **Helper Options** pick-list will read from
``SGEHelperOptions.etab``. If no ``SGEHelperOptions.etab`` is found, the
**Helper Options** pick-list will read from the default ``SGEOptions.etab``.

Configure the Studio batch viewer in CARMSYS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Perform the following steps to configure the Studio batch viewer:

#. Unpack the CARMSYS for user batch. The example assumes that the
   CARMSYS is unpacked and located in

   ``/opt/Carmen/batch/CARMSYS``.
#. In ``/opt/Carmen/batch/CARMSYS`` create the following directories with
   read and write permissions for user and group of users running the batchviewer:
   ``tmp``
   
   ``tmp/BatchViewer``

#. Set the following environment variables and add them to the file ``CONFIG_extension`` in the CARMUSR::

     PYBATCHSYS=/opt/Carmen/batch/CARMSYS
     PYBATCHTMP= $PYBATCHSYS/tmp
     PYBATCHLIB= $PYBATCHSYS/lib/python

   You do not necessarily need to install a separate CARMSYS for the batch.

Jeppesen Batch Viewer Daemon start and stop
----------------------------------------------------
**Start**

Start the Univa Grid Engine daemon as user batch with the command::

  $CARMSYS/bin/start_gridengine_daemon

Before you start the daemon you have to assure that you are the correct user
and that you have set the environment variables correct.

**Stop**

Stop the Univa Grid Engine daemon as user batch with the command::

  $CARMSYS/bin/stop_batchviewer_daemon

**Ping**

Ping the Univa Grid Engine daemon as user batch with the command::

  $CARMSYS/bin/ping_batchviewer_daemon

Univa Grid Engine backup
------------------------

Backup copies of the Univa Grid configuration should be made regularly and
before any major reconfigurations. Run the installation script with the ``bup``
flag and default options for everything else.::

  cd $SGE_ROOT
  ./inst_sge -bup

The result is a tar file ``default/backup/backup.tar.gz`` which contains
the entire configuration.

Univa Grid Engine command line options
--------------------------------------

To list all administrative hosts::

  qconf -sh

To list all submit hosts::

  qconf -ss

To list all execution hosts::
  
  qconf -sel

To change the number of slots possible per machine in the ``rave`` queue:

#. Issue the command::
   
     qconf -mq rave

#. Go to the line beginning with ``hosts``. The number shown is the default
   number of slots for all hosts in the queue. To change the number of slots
   for machine ``portmoller`` to ``1``, modify the line according to:
   
   ``hosts 2,[portmoller=1]``

#. Configure the attributes per host in ``qmon``.

Local spooling
--------------
In order to reduce NFS traffic generated by Grid Engine, you might want to
consider using local spooling. The downside is that logfiles will not be available on NFS, and in order to get hold of these you need to access them on each
server.

Installation
^^^^^^^^^^^^

#. For each execution and master node, create a local spool directory::

     mkdir /var/spool/sge
     chown sgeadmin:root /var/spool/sge

#. Install ``qmaster`` as described here:

   http://wikis.sun.com/display/GridEngine/How+to+Install+the+Master+Host.

#. Install ``execd`` as described here:
   http://wikis.sun.com/display/GridEngine/Example+Execution+Host+Installation

   In step 12 ("Local execd spool directory configuration"), answer yes to the
   question: "Do you want to configure a local spool directory?".
   As local spool directory, enter the one created above (``/var/spool/sge``).
