.. _installation:

Installation
============

This chapter describes the main steps of installing a CMS2 system.

System structure
----------------

Software categories and responsibilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The necessary software is divided into three categories, with different responsibilities:
 * Basic Operating System. The customer is normally responsible for this,
   which includes installation, monitoring and upgrades.
 * Carmen System. This layer includes 3rd party application/tools and CARMUTIL, which is the glue between the operating system and our applications, and CARMSYS, which is the collective name for all server
   applications provided by Jeppesen.
 * Customer Implementation. A template CARMUSR is provided in the system package, but the the main part of the CARMUSR is created during the
   implementation project. CARMUSR will be maintained by the customer.

See also :ref:`system_overview.files_and_storage`.

Carmen home
^^^^^^^^^^^

In most environments, the main home directory where all Jeppesen specific
components are installed is located in the ``/opt/Carmen`` (NFS-mounted)
directory. This directory is referred to as ``CARMEN_HOME``.

Jeppesen components
^^^^^^^^^^^^^^^^^^^

A Jeppesen system is designed to run using four different directory structures.
Their roots are determined by the following environment variables (each corresponding to a file system directory):

 * ``$CARMSYS``
 * ``$CARMUSR``
 * ``$CARMDATA``
 * ``$CARMTMP``

In addition, a Jeppesen system must have full access to the directory ``/tmp``.

Most of the Jeppesen products can be set up using the "avocado structure" (the
core in CARMSYS, the customizations in CARMUSR). In many environments, the
different components are gathered as follows under ``CARMEN_HOME``.::

  CARMEN_HOME
   /CARMUSR
   /CARMTMP
   /CARMSYS
   /CARMDATA
   /SessionServer.<hostname>
   /sge
   /dist (area for delivered CARMSYS, CARMUSR etc)

.. note::
   These directories, except ``SessionServer.<hostname>`` should be NFS exported.

Prerequisites
-------------

Before getting started, check the following
 * Working DNS server, user catalogue, NIS LDAP etc.
 * RHEL subscription; SLES & Solaris equivalent

Terminology
^^^^^^^^^^^

The following terminology is used in the installation instructions:

CARMEN_HOME
   Placeholder name for the main installation directory (typically ``/opt/Carmen``).

SessionServerSYS
   Placeholder name for the main Session Server installation directory
   (typically ``$CARMEN_HOME/SessionServer.<hostname>``.

Installation steps
------------------

These are the main steps in an installation from scratch:

Step 1 Install OS + required packages.
   See :ref:`installation.os_installation_hints`.

Step 2 Install Univa Grid Engine.
   See :ref:`univa_grid_engine.univa_grid_engine_installation`.

Step 3 Install other third-party products, including database.
   See :ref:`installation.installation_of_third_party_products`.

Step 4 Install Carmen system.
   See :ref:`installation.installation_of_jeppesen_system`.

Step 5 Install Session Server.
   See :ref:`session_server.installation_upgrade_of_session_server`.

Step 6 Install Manpower client.
   See :ref:`installation.installation_of_manpower_client`.

.. _installation.os_installation_hints:

OS installation hints
---------------------

RHEL5
^^^^^

To install the operating system, use the graphical installer from the distribution medium. Deselect all packages, with the exception of the packages under
*'Base System -> Base'*. This means that the software groups *'@core'* and
*'@base'* are selected. This can be verified in the ``anaconda.cfg`` file following
the installation. This results in a minimal setup installation of approximately
430 packages.

.. _installation.installation_of_third_party_products:

Installation of third-party products
------------------------------------

This chapter contains instructions and hints for some of the additional required third-party
products that are not included in CARMUTIL. The use of third-party products depend on the platform and the deployment alternative.


Oracle database
^^^^^^^^^^^^^^^

Follow normal installation procedures from the manufacturer. For details see
http://www.oracle.com/database/index.html.

Notes
 * The FLM_DATA and FLM_TMP tablespaces are necessary
 * The database must use UTF-8 encoding
 * The NLS_LENGTH_SEMANTICS parameter must be CHAR

.. _installation.installation_of_jeppesen_system:

Installation of Jeppesen system
-------------------------------

Installation of CARMUTIL
^^^^^^^^^^^^^^^^^^^^^^^^

CARMUTIL is a collection of third-party tools and libraries that is distributed
by Jeppesen.

Prerequisites
+++++++++++++

 * Red Hat subscription (SLES and Solaris equivalent)
 * Access to carmutil repository (ftp.jeppesensystems.com/pub/carmutil)

Installation
++++++++++++

 1. Download and unpack the CARMUTIL repository.

    Example::

      rpm -Uvh ftp://ftp.jeppesensystems.com/pub/carmutil/rhel5/
      carmutil-release-5-2.noarch.rpm

 2. Use yum to install.
    
    Example::

      yum install carmutil17

Installation of CARMSYS
^^^^^^^^^^^^^^^^^^^^^^^

The CARMSYS (the product core) is distributed as a compressed bundle (tarball)
that needs to be uncompressed before usage. It is important to have the
correct package for the client specific platform.

Example::

  standard_gpc-17.5.0.x86_64_linux.tar.gz

A core can be used by several CARMUSRs and versions. It is important that
you do not remove cores which are in use.
In many systems, all cores are kept in ``$CARMEN_HOME/CARMSYS``. If there are
many cores available, some clients decide to keep cores in subdirectories,
such as ``$CARMEN_HOME/C17``.

Installation
++++++++++++

Install by uncompressing the bundle (tarball) into the designated CARMSYS
directory. Assuming that the bundle is in ``$CARMEN_HOME/distrib``:

Example::

  cd $CARMEN_HOME/CARMSYS
  tar -xzf ../distrib/standard_gpc-17.5.0.x86_64_linux.tar.gz

Installation of CARMUSR
^^^^^^^^^^^^^^^^^^^^^^^

The CARMUSR for SAS is in ``$CARMEN_HOME/CARMUSR/
<SERVICEPACK_VERSION>/``. A symlink is also created at 
``$CARMEN_HOME/CARMUSR/<CARMSYSTEMNAME>`` that points out the currently active CARMUSR.

The CARMUSR is kept under version control with Mercurial. 

.. admonition:: Brief example of how to check out the CARMUSR from Mercurial

   Check out a CARMUSR from Mercurial::

    cd /opt/Carmen/CARMUSR
    hg clone /mercurial/sk_cms_user.hg <SERVICEPACK_VERSION>
    cd <SERVICEPACK_VERSION>
    hg update <TAG>

   where:

   ``<SERVICEPACK_VERSION>``
     The current version of the service pack, e.g. ``cms2_sp6_1``.

   ``<TAG>``
     The tag set in Mercurial for the current release.

For more information about Mercurial and configuration management in the SAS
CMS system, please refer to the *Configuration Management Plan*.

Configure the CARMUSR
+++++++++++++++++++++

The SAS CARMUSR has the *major* parts of all configurations, for all different
sites such an production, test and development saved in the CARMUSR and the
configuration kept under version control. This means that configuring the
CARMUSR more is about setting up the CARMUSR for a specific site than to actually
make changes in configuration files.

Configuring CARMSYSTEMNAME
""""""""""""""""""""""""""

When changes are actually necessary, it is encouraged to check in these changes to
Mercurial since have local modifications can have negative effects or incidentially
be removed.

To setup the CARMUSR for a specific site, the variable `´CARMSYSTEMNAME` is used.
Instead of setting this variable manually, preconfigured files for different sites
have been created. In order to configure the system for a specific site a file
or symlink ``$CARMUSR/etc/local.xml`` that links to any of the preconfigured site files
is necessary.

.. admonition:: Example of setting up a CARMUSR for the site ``PROD_TEST``

   ::

     cd $CARMUSR/etc
     ln -s local_template_PROD_TEST.xml local.xml

If no site specific information has been added the system is configured in
"development" mode.

Creating links to CARMSYS
"""""""""""""""""""""""""

The CARMUSR uses a list of symlinks to figure out which CARMSYS:es to use for
different applications.

The following symlinks must be created in the CARMUSR:

``current_carmsys_cas``
   A symlink to the Planning CARMSYS

``current_carmsys_cct``
   A symlink to the Tracking CARMSYS

``current_carmsys_cmp``
   A symlink to the Manpower CARMSYS

Linking to CARMTMP
""""""""""""""""""
Each CARMSYS used in the CARMUSR  needs a separate CARMTMP directory. There
needs to be symbolic links from the CARMUSR to these.

A new CARMTPM directory shall be created when the CARMSYS is updated.

The following symlinks must exist in the CARMUSR:

 * ``current_carmtmp``
 * ``current_carmtmp_cas``
 * ``current_carmtmp_cct``
 * ``current_carmtmp_cmp``

It is important that all users have write access to the CARMTMP directories.
 
A sub-directory ``run`` and ``logfiles`` must be added to all the CARMTMP
directories, with  full acces rights for all users.

Linking to CARMDATA
"""""""""""""""""""

The CARMUSR needs information about where to find the ``$CARMDATA`` directory. This
is handled by a symlink from the CARMUSR to the CARMDATA directory. The symlink
shall be named ``current_carmdata``.

.. admonition:: Example of creating a CARMDATA symlink

   cd $CARMUSR
   ln -s /opt/Carmen/CARMDATA/cms2_sp5_1/ current_carmdata

.. _installation.installation_of_manpower_client:

Installation of Manpower client
-------------------------------

The Manpower client is installed using a standard Windows ``.msi`` installer.
The default installation directory is ``C:/Program Files/Jeppesen/Jeppesen Manpower``.

Configuration
^^^^^^^^^^^^^

The main configuration file is ``$CARMSYS/data/config/manpower.xml``
on the server.

If you would like to make local configuration changes (such as specifying a
different schema, username and password, you can copy ``<install_dir>/
user.config-sample`` to ``<install_dir>/Config/user.config`` and
make your changes to that file.

Running on Citrix
^^^^^^^^^^^^^^^^^

When using Manpower client on a Citrix machine, roaming profiles must be
