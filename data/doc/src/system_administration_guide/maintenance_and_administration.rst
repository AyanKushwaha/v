.. _maintenance_and_administration:

Maintenance and administration
==============================

This chapter contains tasks related to maintenance and administration of a
SAS CMS2 system. The system requires normal system administration
responsibilities. This section gives hints about some system administrator
tasks of particular interest when running a CMS system.

Minor upgrade of CARMSYS
------------------------

If the released CARMSYS is a minor release or a patch release (service pack)
and it is compatible with the currently used CARMSYS, it is easy to update a
system. All new cores must be tested in the test environment before an
upgrade is done in the production system.

 1. Inform the users of the unavailability of the system during the upgrade.
 2. Make sure all users are offline.
 3. Stop sysmond running on the specific system, and verify that all components and interfaces are shut down.
 4. Remove the current_CARMSYS link.
 5. Create a new link, pointing to the new CARMSYS release.
 6. Re-compile the rule sets used.
 7. Do a basic system sanity check.
 8. Start the system using sysmond.
 9. Verify interfaces, system components, and inform users about the upgrade.

Minor upgrade of CARMUSR
------------------------
A minor upgrade is when the system needs a smaller update or patch, which
does not change any important calculations etc. In practice this is upgrades
which solves specific issues, or contain minor enhancements.

The particular steps to be performed are customer specific.

SAS CMS updates are normally planned by SAS together with Jeppesen and specific
installation instructions are generated for each release with tailored installation
instructions.

System growth
-------------

As the number of users increases and there is a need for more computers, it is
the system administrator's responsibility to plan for this. This includes
determining the need for more memory, selecting new computers, preparing the
network etc. It also includes to predict, based on disk usage tracking, when
there will be no more disk space and to budget for this situation.

A running CMS system is in a state where it constantly receives and emits
information. Information is fed into the system from a variety of external
systems, usually through some message broker, but also from files that are
regularly read from the file systems. Information is also produced and exported to
external systems. There is also a multitude of log files being produced and
used.

The default location for all information that is not stored in the database is the
CARMDATA directory and its various subdirectories. Obviously, the amount
of information stored in CARMDATA grows constantly and unless some
form of pruning strategy is employed - for example "keep only x months
worth of data" - it will eventually grow beyond the boundaries.

This can happen surprisingly quickly. First of all, it is initially common to
underestimate the amount of data that is fed into the system, so all feed files
are usually larger than expected. Secondly, some of the log files produced by
the system can grow very large, very quickly.

Contact the Jeppesen Service Centre for additional advice.

Disk usage
----------

An important task of any system administrator is to administrate and track
disk usage. One part of this is to have up-to-date knowledge about the disks
that are installed in the computers, what file systems they contain, their sizes
and their contents.

If there is no available disk space, a Jeppesen system behaves unpredictably. In
that case follow these general steps:

 1. Determine which file system that has no more available disk space.
 2. Search for large unnecessary files and remove them, for example core
    files.
 3. Compress rarely used files, for example OAG files or some local plans.
 4. If the amount of data simply has become too large, move some of the data
    to another file system and create the appropriate symbolic links and NFS
    mounts.

Backups
-------

A Jeppesen system produces important flight operation data that represent a
considerable amount of time, both man hours and CPU hours. It is thus essential
that this data is carefully backed up at regular intervals. Each customer
must decide how many days/hours they believe that they can afford to lose
and decide a backup strategy based on that decision. The safe-keeping of
backup data is also the system administrator's responsibility.

Add a new server host
---------------------

When adding a new server host, it is necessary to install and configure SGE,
authentication services (see :ref:`installation`) and SSH so the system
can use it properly.

.. Note::
   The following instructions assume that all normal system administration tasks
   for the host (NFS, DHCP, etc.) have been taken care of.

Install CARMUTIL
^^^^^^^^^^^^^^^^

The CARMUTIL package must be installed on the host.

Check get_host script
^^^^^^^^^^^^^^^^^^^^^

Make sure that the new host can be selected by the Session Server's or your
customized ``get_host script``.

Install and configure the SGE execution daemon on the new host
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Log in as root and run the installation script. Use default options for
everything. Here is a Bash shell example::

  $ export SGE_ROOT=/opt/Carmen/sge
  $ cd $SGE_ROOT
  $ ./install_execd

Source the relevant settings file, depending on your shell, under ``$SGE_ROOT/default/common/``.

Configure the complex variables for the host. For CMS, the values ``carmrunmaster``, 
``carmbuildmaster`` and ``studio`` should be set to true.

Configure the new host as a submission host and as an administrative host.

Configure the new host as an execution host.

Make sure that the new host is in the host list for the ``opt``, ``rave`` and ``studio``
queues.

Configure SSH
^^^^^^^^^^^^^

Configure SSH with HostBasedAuthentication for the new host. Look at an
existing host's SSH configuration under ``/etc/ssh/`` to see what
``ssh_config`` and ``sshd_config`` should look like.

Users and roles
---------------

There are several users of the CMS system in different departments, for
example planning, tracking, and training. All users do not normally have
access to all functions in the system; you only see the functions you use. For
this purpose there are roles in the system.

Each user belongs to a role. The role controls system behaviour, such as
menus and access rights in forms and tables.

Storing and fetching of roles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All users and their roles are stored in the CARMUSR in XML format, as part
of the common system configuration.

At start-up, the system parses this information to get the current roles for the
users.

Add or modify a user
--------------------

.. Note::
   There are many possible ways of physically storing the complete system
   configuration. It may be stored in one single file, or any combination of smaller
   files. The examples in this manual should be regarded as illustrations, not as
   absolute rules.

A new employee, Alice, will start working with Tracking. She needs a new
account. Bob has changed tasks and is now an administrator of the system.

Apply these changes to the configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the user configuration (which could be in $CARMUSR/etc/users.xml,
for example) as follows::

  <users>
    <user name="Alice">
      <role>Tracking</role>
    </user>
    <user name="Bob">
      <role>Administrator</role>
    </user>
    ...
  </users>

Add a new application for a role
--------------------------------

An employee with the Administrator role wants to start Emacs from the
launcher. Add this functionality to the configuration.

 1. Edit ``$CARMUSR/etc/config.xml``. Inside the applications element, add
    an include element that refers to the new application.

    Example::

      <applications>
      ...
      <include href="${CARMUSR}/etc/application_emacs.xml"/>
      </applications>

 2. Create a new file, ``$CARMUSR/etc/application_emacs.xml``, with the
    following contents::

      <application name="emacs">
      <name>Emacs</name>
      <icon>Emacs.gif</icon>
      <tooltip>Start Emacs</tooltip>
      <com.carmensystems.basics.spl.command>emacs &</
      com.carmensystems.basics.spl.command>
      </application>

 3. Edit ``$CARMUSR/etc/roles.xml``. For the Administrator role, add a new
    ``application`` element specifying emacs::

      Example <role name="Administrator">
      <comment></comment>
      <application>tableeditor</application>
      <application>studio</application>
      <application>alertmonitor</application>
      <application>salary_data_form</application>
      <application>emacs</application>
      </role>

Import and export of airport file
---------------------------------

There is a tool to import or export an airport file into or from a database.
Usage::

  airporttool [options]

The tool supports both UDMAIR classic and enterprise, and has the following options:

``-h, --help``
   Show this help message and exit.
``-c CONNECTIONSTRING, --connection-string=CONNECTIONSTRING``
   Dave connection string.
``-s SCHEMA, --schema=SCHEMA``
   Name of the database schema.
``-b BRANCHID, --branch=BRANCHID``
   The id of the Dave branch.
``-f AP_FILE, --filename=AP_FILE``
   Name of airport file.
``-i, --import``
   Import airport file to database.
``-e, --export``
   Export from database to airport file.
``-u UDM_VERSION, --udm-version=UDM_VERSION``
   The UDM major version to use. The version is fetched from the database automatically if no version is given.

Importing an airport file
^^^^^^^^^^^^^^^^^^^^^^^^^

At import the airport file is treated as the master data source. Any airport in
the airport file missing in the database is created in the database. Any airport
in the database not included in the airport file is deleted from the database.
However, if a city or country in the database is not related to any airport in the
database and airport file it is only ignored and not deleted.

To run airporttool in import mode, use the ``-i`` option.

.. admonition:: Example

   Connection string: ``oracle:demo/foo@dbhost/mybigdb``

   Schema: ``test_schema``

   Airport file: ``apt_file``

   Command::

     airporttool -i -c oracle:demo/foo@dbhost/mybigdb -s \
     test_schema -f apt_file

Exporting an airport file
^^^^^^^^^^^^^^^^^^^^^^^^^

To run airporttool in export mode, use the ``-e`` option.

.. admonition:: Example

   Connection string: ``oracle:demo/foo@dbhost/mybigdb``

   Schema: ``test_schema``

   Airport file: ``apt_file``

   Command::

     airporttool -e -c oracle:demo/foo@dbhost/mybigdb -s \
     test_schema -f apt_file

Database-related tasks
----------------------

For export and import, Oracle tools such as DataPump are recommended.

For information on procedures and Jeppesen tools (such asMkSchema,
ImportSchema, ExportSchema and DBOptimize) for creating and maintaining a
database with the DAVE component, refer to *Database Administration
Guide for Jeppesen DAVE (for Oracle databases)*.

Recovery
--------

If a server crashes and it is not possible to restart it, do as follows:

Application Server crash
^^^^^^^^^^^^^^^^^^^^^^^^

If an application server crashes, no immediate action is necessary. UGE will
redistribute the load to another server and the system will continue running,
but all user sessions on that server are lost and must be restarted.

Core server crash
^^^^^^^^^^^^^^^^^

 1. List the services in the configuration for the server host.

 2. Move the services from the faulty server to a new server by updating the
    configuration. If the new server is an application server, then remove it
    from the SGE configuration (set the Studio complex variable to false).

 3. Restart Sysmond on the new server


Manpower accumulators
---------------------

Manpower accumulators store historical data in an efficient way. Each crew
member has one or more accounts with a record of all the data and transactions.
An account baseline is the fixed balance of an account on a particular
date.

The shell script ``$CARMUSR/accumulate`` updates accumulators in Dave by
calling the Python module ``carmensystems.manpower.accumulate``.

Syntax::

  accumulate schema category acc_from acc_new_from acc_to

``schema``
   The name of the schema

``category``

``acc_from``
   Previous start of accumulation period.

``acc_new_from``
   New start of accumulation period. A new leave balance baseline will be
   created if ``acc_new_from > acc_from``.

``acc_to``
   Accumulate up to this date.

The interval is processed one month at a time to limit the amount of used
memory.

How it works
^^^^^^^^^^^^

Accumulation is done for establishment tasks and user specific accumulators,
and has 2 parts:

 1. Accumulation of accounts and the move of baseline.
    This is done between ``acc_from`` and ``acc_new_from``. The full period
    ``acc_from`` to ``acc_new_from`` and full assignments are loaded. ``acc_from``
    should be the existing baseline so the new baseline set at ``acc_new_from``
    can be calculated correctly. The new baseline replaces the existing baseline.
 2. Accumulation of establishment tasks and user specific accumulation.
    This is done in monthly episodes starting at the ``acc_new_from`` to ``acc_to``.::

      old baseline
      new baseline
      today
      acc_from
      acc_new_from
      acc_to 

      |
      |
      |
      |yyyyyyyyyyyyyyyyyy|yyyyyyyyyyyyyyy|
      |
      |xxxxxxxxxxxxxxx|
       ------------------------------------------> timeline

``yyyy`` represents the time period for which ``account_entry`` table is computed.

``xxxx`` represents the time period for which the establishment tasks and user
specific accumulation is computed.

If the baseline is not supposed to move ``acc_from`` and ``acc_new_from``
should be the same date.
