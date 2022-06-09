# coding: latin1
"""
This modules defines and sets servers.

Servers are defined by dicts with the keys: 'host', 'protocol' (optional), and 'port' (optional).

In PROD_TEST and PROD, the predefined servers can't (easily) be overridden.

In DEV, they may (and should) be overridden to suit your perticular set-up.

The server can be overridden by exporting the name of your predefined server as "ROSTERSERVER_SERVER".
For that to work, you need to predefine it bellow.
Alternatively you can use the function 'set_server' somewhere in your code or in an interactive console, passing in
the key (str) to a predifined sever, or a map representing a server as per specification.
"""

import os


RSDEV = dict(
    protocol="https",
    host="triptradeserver-dev.hiqcloud.net")
RSTEST = dict(
    protocol="https",
    host="triptradeserver-test.hiqcloud.net")
RSUAT = dict(
    host="rosterserver-uat.sasuat.local")
RSPROD = dict(
    host="rosterserver.sas.local")
SEIPDEV = dict(
    host="seipdev.sasuat.local",
    port="10020")
SEIPTEST = dict(
    host="seiptest.sasuat.local",
    port="10020")
SEIPPROD = dict(
    host="seip.sas.local",
    port="10020")


SERVERS = dict(
    CMSDEV=RSTEST,
    PROD_TEST=RSUAT,
    PROD=RSPROD
)


_server = None  # A global which may hold an overriding server for CMSDEV


def get_server():
    """
    :return: A map representing a server.
    """
    csys = os.getenv("CARMSYSTEMNAME")

    if csys in ["PROD_TEST", "PROD"]:
        return SERVERS.get(csys)

    # this comes after the previous one - to prevent accidentally leaving a set_server somewhere
    # in case of specific override
    if _server:
        return _server

    if csys == "CMSDEV":
        return SERVERS.get(csys)


def set_server(str_or_dict):
    """Allow specific override of server or server-map - only in developement.
    Can also be controlled (in DEV) by setting environment variable "ROSTERSERVER_SERVER"
    """
    global _server
    if isinstance(str_or_dict, dict):
        _server = str_or_dict
    elif str_or_dict in SERVERS:
        _server = SERVERS.get(str_or_dict)
    else:
        raise Exception("server doesn't exist or is wrong type: %s" % str_or_dict)

    print("   Server used: %s" % get_server())
    return get_server()
