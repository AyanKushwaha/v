"""
Menues implemented here in stead of in "menu files" for dynamic development/reload/testing
"""

from pprint import pprint
import os

import Csl
import utils.mnu as mnu
import adhoc.developer_menu as devmen

import crewinfoserver.util as rsu
import crewinfoserver.data.crew_profile as cis_cp
import crewinfoserver.data.crew_rosters as cis_cr
import hotel_transport.data.HotelMqHandler as ht_hotel
import hotel_transport.data.TransportMqHandler as ht_transport

ID_RSm = "RosterServer_topmenu"

csl = Csl.Csl()


def _studio_host_port():
    import carmensystems.studio.webserver.WebServer as WS
    import Names
    return "%s:%s" % (Names.hostname(), WS.portbase)


def _show_studio_host_port():
    rsu.show_message(_studio_host_port(), "Studio host:port")


def rosterserver_menu():
    return mnu.Menu(
        "RosterServer",
        title="RosterServer",
        identifier=ID_RSm,
        l=[


            # CrewInfoServer uses published data so push from a regular Studio in PROD is not allowed.
            mnu.Button("CIS: Publish visible crew ...",
                       sensitive=(os.getenv("CARMSYSTEMNAME") != "PROD"),
                       action=lambda: pprint(cis_cp.push_visible_crew())),

            # CrewInfoServer uses published data so push from a regular Studio in PROD is not allowed.
            mnu.Button("CIS: Publish all crew ...",
                       sensitive=(os.getenv("CARMSYSTEMNAME") != "PROD"),
                       action=lambda: pprint(cis_cp.push_all_crew())),

            mnu.Button("CIS: Show crew data for marked crew ...",
                       action=lambda: pprint(cis_cp.show_crew_profile_details())),

            # CrewInfoServer uses published data so push from a regular Studio in PROD is not allowed.
            mnu.Button("CIS: Publish visible crews roster ...",
                       sensitive=(os.getenv("CARMSYSTEMNAME") != "PROD"),
                       action=lambda: pprint(cis_cr.push_visible_crews_roster())),

            # CrewInfoServer uses published data so push from a regular Studio in PROD is not allowed.
            mnu.Button("CIS: Publish all crew rosters ...",
                       sensitive=(os.getenv("CARMSYSTEMNAME") != "PROD"),
                       action=lambda: pprint(cis_cr.push_all_rosters())),

            mnu.Button("CIS: Show roster for marked crew ...",
                       action=lambda: pprint(cis_cr.show_crew_rosters_data())),

            mnu.Separator(),

            mnu.Button("HOTEL: Show TEST Hotel booking... ",
                       action=lambda: pprint(ht_hotel.showTestHotels())),

            mnu.Button("TRANSPORT: Show TEST Transport booking... ",
                       action=lambda: pprint(ht_transport.showTestTransports())),

            mnu.Separator(),

            mnu.Button("DEV: Reload RosterServer modules ...",
                       accelerator="Ctrl<Key>R",
                       action=lambda: devmen.python_reload("crewinfoserver.reload_list")),

            mnu.Button("DEV: Evaluate Python code ...",
                       action=lambda: csl.evalExpr(
                        'PythonRunFile("/opt/Carmen/NiceToHaveIQ/lib/python/nth/studio/commands/py_evaluator.py")')),

            mnu.Separator(),

            mnu.Button("DEV: Reinstall this menu",
                       action=reinstall_RSm),

            mnu.Button("DEV: Uninstall this menu",
                       action=uninstall_RSm),

            mnu.Separator(),

            mnu.Button("Studio host:port is:  '%s'" % _studio_host_port(),
                       action=_show_studio_host_port),

            mnu.Button("Set Time",
                       action=devmen.set_time),
        ])


def install_RSm():
    rosterserver_menu().attach("TOP_MENU_BAR")


def reinstall_RSm():
    uninstall_RSm()
    install_RSm()


def uninstall_RSm():
    mnu.delete("TOP_MENU_BAR", identifier=ID_RSm)
