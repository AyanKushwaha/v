"""
Similar to ZZReload.py, but used from RosterServer,
ensuring easy loading of all modules relevant to Rosterserver/TripTrade."""


modlist = [
    "carmusr.tracking.informedtemptable",
    "carmusr.tracking.Publish",

    "crewinfoserver.util",

    "crewinfoserver.menues",

    "crewinfoserver.common.util",
    "crewinfoserver.data.crew_profile",
    "crewinfoserver.data.crew_rosters",
    "crewinfoserver.data.check_in",
    "crewinfoserver.data.data_handler",
    "crewinfoserver.server.api_handler",
    "crewinfoserver.server.endpoint_builder",
    "crewinfoserver.server.servers",
    "report_sources.report_server.rs_crewinfoserver",

    "hotel_transport.data.HotelMqHandler",
    "hotel_transport.data.TransportMqHandler",
    "hotel_transport.common.util",
]
