.. _session_server:

Session Server
==============

Session Server is a component for handling login and authentication. It also
keeps track of the configurations for users and available services.

Session Server is packaged as a standalone product with its own CARMSYS
structure, and it is implemented as a number of web applications running in a
Tomcat web server/servlet engine. For more information on Tomcat, see
http://tomcat.apache.org.

**Components**

Session Server has the following sub-components:

Session Server
   The main component; keeps track of the configurations for each user/
   role and the available services.
Launcher
   The GUI component of Session Server.
ServerFactory
   A component that starts servers on demand.
carmfileservlet
   A component that exports CARMSYS/CARMUSR per system via
   HTTP or HTTPS. It makes parts of the file system available as webaccessible resources.
CarmConfig
   A component that manages the configuration of the carmen systems.
LasProxy
   Handles communication between Studio and Launcher.

.. _session_server.installation_upgrade_of_session_server:

Installation/upgrade of Session Server
--------------------------------------

Session Server distribution is different from the standard CARMSYS in that
it requires both unpacking and installation. The unpacked distributions should
be stored in a well-defined location so that they can be easily reinstalled if
necessary. The recommended location is ``$SessionServerSYS/Deliveries``.

Session Server is delivered as a separate component (a tar file named something
like ``SessionServer-16.1.6.x86_64_linux.tar.gz`` on Linux),
and should normally be installed in ``$CARMEN_HOME/
SessionServer.<hostname>`` (referred to as ``SessionServerSYS``
below).

Prerequisites
^^^^^^^^^^^^^

 * The host machine must be allowed to run Tomcat 7 on ports 8080 and 8443. 
   Tomcat is prepackaged in the session server and does not need to be 
   installed separately.
 * Session Server runs as user carmen. This user needs read privileges to
   ``CARMUSR`` and ``CARMSYS``, and write privileges to ``CARMTMP``.
 * On Red Hat Linux, it is strongly recommended to subscribe the host to
   Red Hat Network, channel Red Hat Enterprise Linux (v. 5 for 64-bit
   x86_64) before installation of Session Server. The installation script will
   try to install the required components.

Installation/upgrade
^^^^^^^^^^^^^^^^^^^^

The tar file should be unpacked in a temporary location on the host machine.
It contains a shell script that installs Session Server with a default setup,
correct user permissions etc. The script can do both the first-time installation, as
well as perform system upgrades when needed.

The script works on all supported platforms and should be run as root::

  sh etc/scripts/sessionserver_deploy.sh

The installation script takes three optional flags:

``-a <authentication mode>``
   The authentication mode can be either unix (plain authentication
   using PAM) or kerberos for Kerberos V authentication. This flag can
   be used to change authentication mode during an upgrade. Default:
   unix.
``-b``
   Batch mode (non-interactive). This flag makes the script use the default
   responses to all questions. Default: no.
``-v``
   Emit verbose progress output. Default: no.

There is no special upgrade option. Upgrading is the same as reinstalling.

Initial configuration
^^^^^^^^^^^^^^^^^^^^^

After installation, the system is ready to be opened for initial access. In order
to make it accessible from Launcher, some configuration is needed:

 1. Log on to the machine where Session Server runs.
 2. Enter ``cd SessionServerSYS/user/etc``.
 3. Open ``systems.xml`` in an editor.
 4. Add system(s) defining available ``CARMSYS``, ``CARMUSR``, etc. as needed.

Each system pointed to in the configuration has its own top-level
``$CARMSYS/etc/system_config.xml`` file.

Upgrading Crew Planning CARMSYS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During major upgrade phases, you need to add a new system configuration in
``system_config.xml``, pointing to the new system that you installed. Copy
the current main system configuration and change the path to the new system.
Do not forget to update the system name.

Uninstalling a Session Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To completely uninstall an existing Session Server, execute the following
command (as root)::

  sessionserver_deploy.sh -u

Running Session Server
----------------------

Usually Session Server is installed in
``/opt/Carmen/SessionServer.<hostname>``

This location is referred to as ``SessionServerSYS`` below.

Starting and stopping
^^^^^^^^^^^^^^^^^^^^^

Session Server is started and stopped using
``SessionServerSYS/bin/sessionserverctl`` (as root or the user specified when installing).

 * Start: ``sessionserverctl start``
 * Stop: ``sessionserverctl stop``
 * Restart: ``sessionserverctl restart`` (Root privileges not necessary.)

Tomcat configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^

The default Tomcat configuration file is::

  SessionServerSYS/user/etc/tomcat5.conf

Log file
^^^^^^^^

Session Server logs to ``SessionServerSYS/tmp/logfiles/catalina.out``.


Launcher options
----------------

Running Launcher from the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Launcher is a Java Web Start application. It can be started using the ``javaws``
command::

  javaws https://<sessionserver>:8443/jws/Launcher.jnlp

A configuration file can be specified using the ``com.jeppesen.carmen.cfg`` system property::

  javaws -wait -J"-Dcom.jeppesen.carmen.cfg=/path/to/test.cfg" https://<sessionserver>:8443/jws/Launcher.jnlp

.. note::
   The ``-J`` option to javaws only accepts a total of 64 characters or less. To
   work around this limitation, the arguments can be put in an environment variable as follows::

     setenv JAVAWS_VM_ARGS="-Dcom.jeppesen.carmen.cfg=/very/long/path/to/test.cfg"
     javaws -wait https://<sessionserver>:8443/jws/Launcher.jnlp

Launcher properties reference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following Java system properties are used by Launcher.

``launcher.gui.title=<title>``
   The default title of Launcher.
``sessionserver=<server>``
   The server to be used when logging in.
``sessionserver.selectable=server1,server2,...,serverN``
   The servers to be shown in the server address field.
``com.carmensystems.cfg.dir=<path>``
   The location where the local configuration files are placed and read.
   Default value: ``%USERPROFILE%/Local Settings/Application
   Data/Jeppesen/Launcher/user``.
``com.carmensystems.user.dir``
   The home directory of Launcher, where it stores logs and configuration
   files. Defaults to ``LauncherConstants#DEFAULT_LAUNCHER_LOCATION``.
``com.jeppesen.carmen.cfg=<path>``
   A local configuration file to be loaded on startup.
``launcher.show.server=<bool>``
   Whether to show or hide the server selection combo box.
   Default value: True.

Application log files and caches
--------------------------------

Studio log file
^^^^^^^^^^^^^^^

Studio generates two log files in ``$CARMTMP/logfiles/``:

``studiostartup.<username>.log``
   This file captures any errors that might occur before the Studio start
   script has launched. Normally, the file contains only one line with the
   path to the Studio binary.
``Studio.<type>.<user>.<date>.<host>``
   This file contains the full Studio log.

Java client application cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Java applications Rave IDE and Scenario Analyzer, as well as Launcher
itself, are downloaded to the client workstation the first time they are started.
They are saved to a disk cache so that they only have to be downloaded again
if new versions have been released.

 * On Windows, the cache directory is
   ``%USERPROFILE%\Application Data\Sun\Java\Deployment\cache``

Rave IDE files
^^^^^^^^^^^^^^

Rave IDE saves additional files in ``$HOME/.jedit (%USERPROFILE%/.jedit`` on Windows XP).

User profiles on XenApp
^^^^^^^^^^^^^^^^^^^^^^^

There should not be any limit to the size of the user profiles. When running
Java applications on a XenApp server, make sure that the server does not have
the ``Limit Profile Size`` option enabled. This option is available in the
Group Policy Object Editor (``gpedit.msc``) in ``User
configuration\Administrative Templates\System\User
profiles``.

Python IDE
^^^^^^^^^^

When Python IDE is started from Launcher, a log file called
``pythonidestartup.<username>.log`` is created in
``$CARMTMP/logfiles``.

.. _session_server.configuration_overview:

Configuration overview
----------------------

Session Server uses the Common Configuration API to retrieve configuration
settings. The configuration root is at
``SessionServerSYS/etc/system_config.xml``, and it may be subdivided into several files.

The configuration is read the first time Session Server, Server Factory, and
CarmFileServlet are started. Then the configuration is re-read every time any
of the configuration files is modified.

The ``SessionServerSYS/etc/system_config.xml`` file is read-only.
Definition of the actual systems (available CARMSYS and CARMUSR) must be
done in ``SessionServerSYS/user/etc/systems.xml`` 

Global configuration properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Systems
+++++++

Session Server retrieves the available systems from the included file
``SessionServerSYS/user/etc/systems.xml``.

Example of a sample system definition::

  <system name="sample1">
    <CARMUSR>/opt/Carmen/sample_system/carmusr</CARMUSR>
    <CARMSYS>/opt/Carmen/sample_system/carmsys</CARMSYS>
    <CARMTMP>/opt/Carmen/sample_system/carmtmp</CARMTMP>
  </system>

For more information about system settings, see "Defining dynamic systems".

.. note::

  Use only A-Z, a-z, - (dash) and _ (underscore) characters in system names.

CarmFileServlet uses the name of the system as the root in the exported file
structure (``/carmfileservlet/<system_name>``). CarmFileServlet needs
at least CARMSYS, but will also look for CARMUSR and CARMTMP when
creating the exported file structure.

Session Server and the Server Factory remember the name and will make it
available as an environment variable when retrieving configurations from the
named system. All elements defined in ``<systems>/<system
name="xxx">`` will be used as environment variables when retrieving the
configuration for the system. This only works if at least one CARMSYS is
defined.

Reloading the configuration
+++++++++++++++++++++++++++

The configuration is reloaded when the Session Server's ``systems.xml`` file
(or any of the included files) is changed. The configuration is reloaded at
most every 10 seconds. If reading the configuration fails for some reason, the
most recent previous working configuration is used.


General system configuration
----------------------------

Users
^^^^^

Each user has a name and contains one or more roles and applications. These
applications, specified either explicitly or indirectly through roles, are the
applications available to the user. They will appear in Launcher in the same
order as they are found here.

The system defines the following environment variables.

``user``
   The user name used in Launcher.
``CARMROLES``
   A list of all roles for the user, if any.

Note that all of the above are defined late, that is, they cannot be used in files
that are included. "``user``" is used instead of "``USER``" since the latter is
used for the user of the Session Server process (Tomcat).

Applications
^^^^^^^^^^^^

Each application has a name and must contain the following subelements.

``name``
   User-readable name.
``icon``
   Path to a suitable icon to show in Launcher.
``tooltip``
   The tooltip to use in Launcher.
``bundle.url``
   Path to JAR file.
``group``
   Launcher UI groups applications in bordered areas based on this property.

**Optional**

``requires``
   Specifies requirements for an application.

It is possible to use ``${SYSTEM}`` and ``${APPLICATION}`` in the entries of an
application. They are initiated with system name and application name
respectively. The system will define the entry bundle.id as ``${SYSTEM}.${APPLICATION}``.
Note that ``${APPLICATION}`` is defined late, that
is, an include cannot use ``${APPLICATION}`` in the file path.

Example::

  <application name="tableeditor">
    <name>Table Editor</name>
    <icon>%{filepath}/data/config/XResources/table.png</icon>
    <tooltip>Start Table Editor - ${SYSTEM}</tooltip>
    <bundle.url>%{jarpath}/tableeditor-all.jar</bundle.url>
    <modelserver>${SYSTEM}.modelserver</modelserver>
    <arg>-o</arg>
    <arg>-q</arg>
    <arg>-c</arg>
    <arg>%{dbconnect}</arg>
    <arg>-s</arg>
    <arg>%{dbschema}</arg>
  </application>

**Special elements**

One or several ``<arg>`` elements may be used. They will be translated into one
args-property, with the number of ``arg`` elements, and a series of ``arg.x``
properties where ``i`` goes from ``0`` to ``args-1``.

Properties are flat, but there is a special syntax for ``<start_server>`` and
``<environment>``.

.. admonition:: Example 1

  ::

    <start_servers>
    <server_key_A>server name A</server_key_A>
    <server_key_B>server name B</server_key_B>
    ...
    </start_servers>

  is translated into
  
  ::

    start_servers/server_key_A = server name A
    start_servers/server_key_B = server name B

.. admonition:: Example 2

  ::

    <environment>
    <var>environment variable A</var>
    <var>environment variable B</var>
    ...
    </environment>

  is translated into:

  ::

    environment/var.0 = environment variable A
    environment/var.1 = environment variable B
    ...
    environment/vars = number of var

Server Factory
^^^^^^^^^^^^^^

When the Server Factory reads the config for a system it looks for configuration
of services: ``serverfactory/services/service``.

Example::

  <serverfactory>
    <services>
      <service name="studio">
        <isHost/>
        <sge>
        <host>%{default_sge_host}</host>
        </sge>
      </service>
      <service name="modelserver">
        <isServer/>
        <sge>
          <server>%{default_sge_server}</server>
        </sge>
        <tmpdir>/carm/proj/ay/tmp</tmpdir>
        <cwdir>${CARMUSR}</cwdir>
        <command>${CARMUSR}/bin/startMirador.sh</command>
        <arg>--watchdog</arg>
        <arg>--linkfile</arg>
        <arg>${tmpfile}</arg>
      </service>
        ...
    <services>
  <serverfactory>

Service
+++++++

Each service has a name attribute. Services can be of two kinds, host or
spawn. The former is used when the application starts the server on its own,
for example, using ``sshlib``, and needs a suitable host. The latter is when the
Server Factory starts the server and returns a link to the running server. A
service can be of both kinds at the same time.

Host
++++

A service with the ``<isHost/>`` element needs no other elements if no load
scheduling is used (the server running the Server Factory will be returned in
this case.)

If basic load scheduling is used then a list of suitable hosts is given as ``basic/hosts/\*``.
If Oracle Grid Engine is used then the entry ``sge/host`` contains a
command that will return a suitable host. This command may refer to variables
that are submitted in the call to the host, for example, ``${user}``.

Server
++++++

A service with the ``<isServer/>`` element must contain at least the entry
``<command>``. Server Factory expects that the command starts the server and
writes a link to the running server in ``${tmpfile}``. The ``${tmpfile}`` can be
defined by the user, if not then the Server Factory will define it. The element
tmpdir can be used to tell the Server Factory where to create the tmpfile.

Other useful entries are:

``cwdir``
   The current working directory for the server, not used when Oracle
   Grid Engine is used.
``arg``
   Adds one or more arguments to the command.

If basic load scheduling is used then a list of suitable hosts is given as
``basic/hosts/\*``. If Oracle Grid Engine is used, then the entry ``sge/server``
contains a command that will run the command on a suitable host. This command
may refer to variables that are submitted in the call to the server, for
example, ``${user}``.

CarmFileServlet and file access control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CarmFileServlet by default exports all files in the Session Server
CARMSYS/CARMUSR using HTTP. It is possible to restrict which files that
can be read by adding ``<carmfileservlet>`` to the top level of the Session
Server configuration. However, all directories will still be accessible; it is
only files that can be restricted. A file is accessible if:

 * at least one path segment in a show element is a substring of the path to
   the file
 * and no path segment in a hide element is a substring of the path to the
   file.

Example::

  <carmfileservlet>
    <show>path_segment_1</show>
    <show>path_segment_2</show>
    ...
    <hide>path_segment_3</hide>
    <hide>path_segment_4</hide>
    ...
  </carmfileservlet>

Roles
+++++

It is also possible to control file access by using roles.

Example::

  <show role="SalaryAdmin">output/SALARY</show>

This example illustrates how the ``output/SALARY`` path will only be accessible
to authenticated users that can assume the SalaryAdmin role.

It is possible to supply a comma-separated role list, for example
"``SalaryAdmin,Administrator``". Note that there is no role-selection step in
CarmFileServlet. If you can select at least one of the required roles, you are
considered authorized for accessing the files.

There is a special role, open, that enables unencrypted HTTP access to the
exact path specified.

Example::

  <show role="open"></show>


Configuration for Jeppesen Crew Management
------------------------------------------

This section describes the standard Session Server and system configuration.

Session Server CARMSYS
^^^^^^^^^^^^^^^^^^^^^^

Directories and files are listed in this section. Files that may be modified after
installation are in the user subdirectory.

``bin/``
   ``get_host``

   Default script for locating a host on which to run Studio. This script
   first checks if the ``$CARMUSR/bin/get_host`` script exists. If so, that script
   is used instead.

   ``check_installation``

   Script that checks the Session Server installation to see if it is complete
   and correctly configured.

   ``sessionserverctl``

   Session Server start/stop/restart script.

``bin/$ARCH``
   ``auth_validator``

   Helper binary used for username-password authentication (not used
   with Kerberos authentication).

   ``tomcat_serverlauncher``

   The binary that Session Server uses to launch model server instances.

``etc/``
   ``cacspolicy.xml``

   CACS permissions.

   ``cacspolicy_default.xml``

   Default CACS permissions.

   ``system_config.xml``

   This read-only file is the root of the whole configuration. It contains an
   include of ``$CARMUSR/etc/system.xml``, and defines properties for the
   Session Server itself as well as some default configuration settings for
   the systems.

   ``SessionServer-release``

   Information about the installed Session Server version.

   ``users.xml``

   Default users.

``lib/classes/``
   Session Server Java libraries.

``user/bin/``
   ``get_host.template``

   Template script for locating a host on which to run Studio. Enable the
   script by following the instructions inside it.

``user/data/``
   ``Launcher.po.template``

   Gettext template for localization of Launcher GUI.

   ``launcher.cfg.template``

   Template for site-wide system default properties for the Launcher client application.

``user/etc/``
   ``application_launcher.xml``

   Settings for Launcher.

   ``sessionservers.xml``

   Alternate Session Servers.

   ``systems.xml``

   Contains definitions of CARMSYS, CARMUSR, etc. for one or more
   systems.

   ``tomcat5.conf``

   Tomcat configuration file.

   ``users.xml``

   File defining the system default users. May be overridden by defining
   other users in CARMUSR, see ``CARMSYS/etc/system_config.xml``.

Crew planning CARMSYS
^^^^^^^^^^^^^^^^^^^^^

In a CARMSYS, the common configuration files are stored in the ``etc`` directory.

``etc/``

   This directory contains several files defining the default configuration
   for applications, roles, and users.

   ``application_pythonide.xml``

   Configuration for Python IDE.

   ``application_raveide.xml``

   Configuration for Rave IDE.

   ``application_scenarioanalyzer.xml``

   Configuration for Scenario Analyzer.

   ``application_studio.xml``

   Configuration for Studio.

   ``application_tableeditor_dtable_las.xml``

   Configuration for Table Editor for editing database tables.

   ``application_tableeditor_etable_las.xml``

   Configuration for Table Editor for editing etables (file based).

   ``application_tableeditor_standalone_dtable_las.xml``

   Configuration for Standalone Table Editor for editing database tables.

   ``application_xterm.xml``

   Configuration for xterm.

   ``config.xml``

   Configuration file for the CARMSYS.

   ``release_info.xml``

   File with CARMSYS release information.

   ``roles.xml``

   Configuration of roles.

   ``server_factory.xml``

   Server factory configuration.

   ``system_config.xml``

   Top-level configuration file. It only contains includes of
   ``$CARMUSR/etc/config.xml`` and ``$CARMSYS/etc/config.xml``.

   ``users.xml``

   Configuration of users.

``etc/scripts/``
    ``xmlconfig``

    Script for command line query of the XML configuration.

    ``functions``

    Shell script utilities.

Default roles and users
^^^^^^^^^^^^^^^^^^^^^^^

Roles ($CARMSYS/etc/roles.xml)
++++++++++++++++++++++++++++++

The default role in a CARMSYS is ``DefaultRole``. That role is given permissions
to use applications as in the following example.

Example::

  <roles>
    <role name="DefaultRole">
      <application>studio</application>
      <application>raveide</application>
      <application>pythonide</application>
      <application>scenarioanalyzer</application>
    </role>
  </roles>

Users ($CARMSYS/etc/users.xml)
++++++++++++++++++++++++++++++

The default user configuration allows all users to log in to the system. The
``any_user`` user is a wildcard representing any user.

Example::

  <users>
    <comment>Default users</comment>
    <user name="carmen" fullname="System support account">
      <role>DefaultRole</role>
    </user>
    <user name="any_user" fullname="Any user">
      <role>DefaultRole</role>
    </user>
  </users>

Defining dynamic systems
^^^^^^^^^^^^^^^^^^^^^^^^

Instead of using a system as defined in the Session Server's
``user/etc/systems.xml`` (shared system), it is possible to define a local system by
supplying settings as Java system properties in a custom configuration file.

User and role settings are always read from the default configuration and are
not affected by the use of local system definitions.

The Session Server hostname should be given as a qualified URL, for example ``hostname.domainname.com``.

Launcher configuration files
++++++++++++++++++++++++++++

In a configuration file (``*.cfg``), there is one line for each setting. A setting is
given as ``-D`` immediately followed by a name=value pair::

  -Dname=value

Only lines beginning with ``-D`` are considered. Lines starting with ``#`` or ``[`` are
silently ignored. Any other line beginnings generate a warning, but are still
ignored.

Example::

  # C17.cfg: sample config file that bypasses system settings
  -DCARMSYS=/opt/Carmen/Systems/standard_gpc_15.1.2_CARMSYS
  -DCARMUSR=/opt/Carmen/Users/Pac/v15_prod
  -DCARMDATA=/opt/Carmen/Data/Pac/Prod
  -DCARMTMP=/opt/Carmen/Tmp/Pac/Prod/15_1.2
  -DCARMSYSTEM=ProdPac
  -DCARMARCH=x86_64_linux
  -Dsessionserver=https://academyserver.academy.carmen.se:8443

The standard location for custom configuration files is the ``user/cfg``
subdirectory in the cache directory (``C:\Documents and
Settings\john\Application Data\Jeppesen\Launcher\user\cfg`` on Windows XP). See also Java
client application cache on page 74). Launcher includes a configuration file
editor that saves files in this directory. This editor is available to users
assigned to the role ``admin_persistent_systems``.

Host and platform selection
---------------------------

Studio Server selection
^^^^^^^^^^^^^^^^^^^^^^^

The ``SessionServerSYS/bin/get_host`` script is normally used to select
the Studio server. If there is a ``SessionServerSYS/user/bin/get_host``
script, it is used instead.

.. note::

   If fully qualified domain names are needed to reach the servers from the
   clients, you must create your own ``get_host`` script that returns the full names.

The following is an example of a custom ``get_host`` script that returns a fully
qualified host name::

  #!/bin/sh
  HOST=`(
  qhost $* | tail +3 | sort -n +3 | \
  grep -v " - " | awk '{print $1}'
  hostname
  ) 2>/dev/null | head -1`
  
  echo $HOST.got.jeppesensystems.com

Platform selection
^^^^^^^^^^^^^^^^^^

It is possible to specify what platform to spawn a process on from Session
Server. This is done by specifying a value for the ``CARMARCH`` variable. This
option is used in addition to the ones specified by
``<default_sge_host_options>`` and
``<default_sge_server_options>`` in the Session Server's
``server_factory.xml`` file.

Valid values for ``CARMARCH`` are:

 * ``x86_64_linux`` (default)
 * ``x86_64_suse``
 * ``x86_64_solaris``.

``CARMARCH`` can be specified in two ways:

 * By specifying ``<CARMARCH>[arch]</CARMARCH>`` for the system in the
   Session Server's ``user/etc/systems.xml`` file.
 * As a property in the Launcher configuration file if a local system is used.
   The ``CARMARCH`` value is passed to the ``get_host`` script.

Univa Grid Engine options
^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to add options to the Univa Grid Engine when a process is
spawned. This is done using the ``CARMSGE`` variable. The options are used in
addition to the ones specified by ``<default_sge_host_options>`` and
``<default_sge_server_options>`` in the Session Server's
``server_factory.xml`` file.

``CARMSGE`` can be specified in two ways:

 * By specifying ``<CARMSGE>[options]</CARMSGE>`` for the system in the
   Session Server's ``user/etc/systems.xml`` file.
 * As a Java property in the Launcher start script if the bypass mechanism is
   used. The Java property specification should be inside single quotes, to
   allow for spaces in the Univa Grid Engine options.

.. note::

   Currently, ``qsub``, ``qrsh``, and ``qhost`` are used as Univa Grid Engine commands.
   These commands have a slightly different set of available options.
   The contents of ``CARMSGE`` should be limited to options understood by all these
   commands. If you specify something unknown, the command invocation will
   likely fail.

Overriding system settings in CARMUSR
-------------------------------------

The default configuration does not require any special CARMUSR settings to
work. However, it is possible to override some of the default settings by modifying files in ``CARMUSR``.

Restricting user access to a system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default configuration allows any user to access a system. To allow only
certain users, do as follows.

 1. Copy ``CARMSYS/etc/users.xml`` to ``CARMUSR/etc``.
 2. Add the allowed users to this file.

.. admonition:: Example

   The following ``$CARMUSR/etc/users.xml`` settings allow only users John
   and Jane to access the system.

   ::

     <users>
       <user name="john" fullname="John Doe">
         <role>DefaultRole</role>
       </user>
       <user name="jane" fullname="Jane Doe">
         <role>Planner</role>
       </user>
     </users>

Restricting user access to an application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default role (``DefaultRole``) allows all users with this role to use all
applications.

.. admonition:: Example

   The following ``CARMUSR/etc/roles.xml`` setting allows users with role
   Planner to use only the Studio application.

   ::

     <roles>
       <role name="Planner">
         <application>studio</application>
       </role>
     </roles>

Modifying Studio configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Extra Studio options can be passed by modifying the ``<cmd>`` element. You can
supply the name of a Python script to be executed, for example.

.. admonition:: Example

  ::

     <config>
       <applications>
         <application name="studio">
           <cmd mode="override">
             $CARMSYS/bin/studio -p "PythonRunFile(\"custom.py\")"
           </cmd>
         </application>
       </applications>
     </config>

Modifying tooltips and icons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default tooltips and icons for an application can be changed by overriding the
application in the user.

For icons there is a predefined iconpath variable whose value is
``%{filepath}/data/config/icons``. Put your custom icons in
``$CARMUSR/data/config/icons``, and refer to them using ``%{iconpath}``.
That will ensure that the paths work on all platforms.

.. admonition:: Example

   ::

     <application name="studio">
       <tooltip mode="override">Start Studio - ${CARMUSR}</tooltip>
       <icon mode="override">%{iconpath}/studio.gif</icon>
     </application>
        
.. _session_server.authentication_services:
        
