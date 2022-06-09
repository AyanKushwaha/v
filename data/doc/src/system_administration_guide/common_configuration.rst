.. _common_configuration:

Common Configuration
====================

The Common Configuration component defines a universal configuration
structure for Jeppesen products. The configuration is defined in XML files.

The configuration files are read and queried using an API provided by the
Common Configuration component. The API is divided into a Config part
doing the parsing of the XML files and reading of properties/attributes, and a
``ServiceConfig`` extension to the former that implements a service concept.
The API is separately implemented in Python, Java and C++, and is accessible from the command line.

Configuration files
-------------------

A configuration file defines properties. The full name of a property is the
name of an XML element, and the value is the content of the element. Some
elements also have attributes, but these are not used to define properties.

Using <include> elements
^^^^^^^^^^^^^^^^^^^^^^^^

The configuration file for a system can be modularized by using ``<include>``
elements that are interpreted as in XInclude.

The default location of the main configuration file (the one with ``<system>`` as
the root element) is ``${CARMSYS}/etc/system_config.xml``. That file can
contain one or several ``<include>`` elements with href attributes pointing to
other configuration files. When the system configuration is parsed by the
Common Configuration API, all referenced files are included and merged
into a single structure with all the data.

The ``<include>`` element may also contain an optional ``<fallback>`` element:

 * Simply using ``<fallback/>`` means that the included file is considered
   optional (it is included if it exists and is readable).
 * If the fallback element also has a href attribute, it will be used if the file
   specified by the ``<inlude>`` element's href attribute does not exist.

.. note::

   Common Configuration allows zero or more ``<fallback>`` inside ``<include>``
   and it does not allow content in ``<fallback>`` (only the href attribute is con-
   sidered).

Variables
^^^^^^^^^

A property defined in a configuration file can contain two types of variables:
environment variables and property variables. These variables are returned
expanded when a configuration query is made.

An environment variable ``VAR`` is defined outside of the configuration. It is
referenced using ``$(VAR)`` or ``${VAR}``. Any undefined environment variable is
passed as is (unexpanded) to the component that made the query.

The value of a property configuration variable ``VAR`` is defined in the
configuration, and it is referenced using ``%(VAR)`` or ``%{VAR}``.

Example of a top level file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The start tag of the root element of the configuration of a system is ``<system name="abc">``,
where ``abc`` is the name of the system.

Example::

  <system name="abc">
    <preferences>
      <include href="${USERPREFERENCES}/.carmen/preferences.xml">
      <fallback/>
      </include>
    </preferences>
    <include href="${CARMUSR}/etc/config.xml" />
    <directories>
      <log>${CARMTMP}/logfiles</log>
      <pid>${CARMTMP}/run</pid>
    </directories>
  </system>

The example above defines two properties and their values:

 * ``abc/directories/log`` = ``${CARMTMP}/logfiles``
 * ``abc/directories/pid`` = ``${CARMTMP}/run``

If the ``preferences.xml`` file can be found, it will be included in the
configuration. A CARMUSR configuration file is required in the ``${CARMUSR}/etc/``
directory.

As can be seen from this example, the complete name of a property includes
all elements from the top node in the XML tree down to the property itself.

Reserved elements and attributes
--------------------------------

There is currently no schema for the XML configuration, and components
can use almost any legal element name.

However, there are some elements and attributes that have special significance
for the Common Configuration API.

List of reserved elements
^^^^^^^^^^^^^^^^^^^^^^^^^

``system``
  The root element of a configuration. Required attribute: ``name``.
``program``
   A program. Required attribute: ``name``.
``parameter``
   A program parameter. Required attribute: ``name``.
``process_group``
   A grouping of processes. Required attribute: ``name``.
``process``
   A process. Required attribute: ``name``.
``service``
   A service. Required attributes: ``name``, ``protocol``, (``nr_ports="1"``).
``hosts``
   A grouping of hosts. No required attributes.
``host``
   A host. Required attributes: ``name``, ``hostname``, ``portbase``.
``data_model``
   A planning data model. No required attributes.
``interface``
   A database connection. Required attributes: ``name``, ``url``.

Context rules
^^^^^^^^^^^^^

The following rules specify the context (element hierarchy) in which the
elements must occur to be considered by Common Configuration. The elements
may still appear elsewhere in the configuration, but in that case they will not
be recognized when specifying services.

 * The ``<interface>`` element must exist inside a ``<data_model>`` element.
 * The ``<process>`` element must exist inside a ``<program>`` element.
 * The ``<service>`` element must exist inside a ``<process>`` element.
 * The ``<user>`` element must exist inside a ``<users>`` element.
 * The ``<host>`` element must exist inside a ``<system>`` element or a ``<hosts>``
   element.
 * The ``<process_group>`` element must exist inside either a ``<system>``
   element or a ``<process_groups>`` element.

Services
--------

A service is defined by a URL with the following parts::

  protocol://[user[:password]@]hostname[:port]/[location]

In order for a service to be registered and recognized, the context rules
described above must be observed. This is illustrated by the following sample
excerpt from a configuration file.

.. admonition:: Example

  Configuration example::

    <hosts>
      <host name="mainnode" hostname=h1cms07a" portbase="11000">
       <start>SAS_ARPC</start>
      </host>
    </hosts>
    ...
    <program name="alertrpcserver">
      <process name="SAS_ARPC">
        <service name="alertrpc" protocol="http" nr_ports="1"/ location="RPC2"/>
      </process>
    </program>

  In a ``<hosts>/<host>`` context is a ``<start>`` element, which contains the
  string ``SAS_ARPC``.

  The same ``SAS_ARPC`` string is identified as a ``<process>`` (which is inside
  ``<program>``). The service tag defines it as a service.

Database services
^^^^^^^^^^^^^^^^^

Database services are recognized by the ``data_model/interface`` context.

Here is one example::

  <data_model>
    <file_prefix>tracking/200703</file_prefix>
    <dbschema>db_stefanle_0319</dbschema>
    <schema>%{dbschema}</schema>
    <period_start>now_month_start+0</period_start>
    <period_end>now_month_end+2</period_end>
    <plan_path>%(file_prefix)/%(dbschema)/%(dbschema)
    </plan_path>
    <interface name="%{dbprefix}"
    url="%{dbprefix}%{dbschema}/%{dbschema}@%{dbhost}:%{dbport}/
  %{dbsid}"/>
    <!-- Config used by the sessionserver and launcher-->
    <dbconnect>%{data_model/interface@url}</dbconnect>
    <database>%{dbschema}</database>
  </data_model>

Making queries
--------------

A configuration query is made using search keys with a syntax similar to
XPath::

  tag/path/to/property
  tag/path/to/property[nr]
  tag/path/to/property[nr]@attr

Here ``tag/path/to`` specifies the context (element hierarchy) in the XML file
in which ``property`` exists.

The ``[nr]`` part is a positional argument (starting from 1). This only works on a
leaf element node.

``@attr`` refers to the ``attr`` attribute of ``property``.

An element with a name attribute can be searched with either the element
name or the value of the element's name attribute as the key.

The "``*``" wildcard can be used to match any element or attribute.

Here are some query examples:

.. admonition:: Example 1

  ::

    some/path

  Returns the value of the first path child of the some element (if it exists).

  ::

    users/user[2]@name

  Returns the value of the ``name`` attribute of the second ``user`` child of ``users``.

.. admonition:: Example 2

  ::

    users/user[3]@

  Returns all attributes of the third user child of ``users``. Note that there is no
  slash between ``user[3]`` and ``@``.

  ::

    users/[4]@

  Returns all attributes of the fourth child element of ``users``.

.. admonition:: Example 3

  ::

    roles/role/application

  Returns all applications defined for all roles.

  ::

    roles/Administrator/application

  Returns all applications defined for the Administrator role. Here is assumed
  that the ``role`` element has a ``name`` attribute with a value of ``Administrator``.

Command line configuration queries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``$(CARMSYS)/etc/scripts/xmlconfig`` can be used to query the configuration from
the command line. It is used as follows::

  xmlconfig [-d] [config.xml] [command]

or::

  xmlconfig [-d] [config.xml] [query1] [query2] [...]

where the available commands are:

``--help, -h``
   Prints this help.
``-d``
   Enable printouts of debugging information.
``--xml``
   Dump the full XML tree after all files have been
   included.
``--all``
   Shows a list of all configuration settings, with
   variables expanded.
``--list``
   Shows a list of all configuration settings, with
   variables unexpanded.
``--srv``
   Shows a list of all services.
``--url service [host]``
   Get the URL for service service [on host ``host``].
``--port service [host]``
   Get the port number for service service [on host
   ``host``].
``query``
   A query string (see above).

API query
^^^^^^^^^

There is a special type of query string that is the command-line equivalent of
using the ServiceConfig API from a program::

  API/getServiceConfig/service[/host[/process]]
  API/getServicePort/service[/host[/process]]

The bold part of the string is literal text that should be written exactly as
shown. The rest are names of services (required), hosts, or processes
(optional) separated by slashes.

.. note::
  When using the command line tool, positional and wildcard arguments must
  be enclosed in single quotes (for example ``'[4]'``).

API reference
-------------

The API consists of two classes, Config and ServiceConfig. There are
implementations in Python, Java, and C++.

Config
^^^^^^

``Config`` has the following methods:

``getProperty(key)``
   Returns a "path" and property value pair (first match).
``getProperties(key)``
   Returns a list of "path" and property value pairs (all matches).

The ``key`` argument is a string using the query syntax described above.

ServiceConfig
^^^^^^^^^^^^^

ServiceConfig

has the following methods:

``getServiceUrl(service, host="", process="")``
   Returns the URL of a service as a text string.
``getServicePort(service, host="", process="")``
   Returns the port number.
``isChanged()``
   Returns True if anything in the configuration has changed.
``refresh()``
   Re-reads the configuration if ``isChanged()`` returns True.

Redefinitions and overrides
---------------------------

The configuration can be modified in various ways. Since a configuration
property can be defined in more than one place (the same name/xpath, but
with different values), the mode attribute is used to indicate its validity.

The following modes can be used:

``freeze`` (or ``stick``)
   A property with ``mode="freeze"`` cannot be modified.
``drop``
   A property with ``mode="drop"`` is dropped from the configuration and
   not used at all. It is not possible to drop an xpath that has a parent or
   child with ``mode="freeze"``.
``override``
   A property with ``mode="override"`` overrides (hides) earlier declared
   values for the property.
``merge``
   A property with ``mode="merge"`` is merged with another node with the
   same xpath in the XML tree. This is the default if no mode attribute is
   present.

Configuration examples
----------------------

Some examples can be found in Configuration overview on page 75.
