import Cui
from report_sources.hidden import TPMSCrew, TPMSRoster


def TPMSCrewReport():
    try:
        TPMSCrew.main()
    except:
        import traceback
        traceback.print_exc()
    finally:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)


def TPMSRosterReport():
    try:
        TPMSRoster.main()
    except:
        import traceback
        traceback.print_exc()
    finally:
        Cui.CuiExit(Cui.gpc_info, Cui.CUI_EXIT_SILENT)
