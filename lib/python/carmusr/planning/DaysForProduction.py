import carmensystems.rave.api as R
import Cui
from carmusr.ActivityManipulation import deleteActivityInPeriod
import carmusr.HelperFunctions as HF
import carmstd.cfhExtensions as cfhExtensions
from RelTime import RelTime

def RemoveFnMatchingDaysForProductionBids():
    """ Remove/trim FN activities that overlap Days available for production bids.
        The crew that are visible in window 1 are processed with data from the currently selected bids file. """

    # Collect all DaysForProduction bids
    Cui.CuiCrgSetDefaultContext(Cui.gpc_info, Cui.CuiArea0, "window")

    days_for_production_bids = []
    big_bag = R.context('current_context').bag()

    for chain_bag in big_bag.iterators.chain_set():
        crewid = chain_bag.crew.id()

        bid_nr = 0
        while True:
            bid_type = chain_bag.bid.type_tab(bid_nr, 0)
            if bid_type == "DaysForProduction":
                start_time_hb = chain_bag.bid.abs1_tab(bid_nr, 0)
                end_time_hb = chain_bag.bid.abs2_tab(bid_nr, 0)
                if end_time_hb.time_of_day() == RelTime(23, 59):
                    end_time_hb = end_time_hb + RelTime(0, 1)
                days_for_production_bids.append((crewid, start_time_hb, end_time_hb))
            elif bid_type == None:
                break
            bid_nr = bid_nr + 1

    # Remove/trim the activities that are overlapping the bids
    crew_kept_legs = []
    for crewid, start_time_hb, end_time_hb in days_for_production_bids:
        kept_legs = []
        deleteActivityInPeriod(crewid, start_time_hb, end_time_hb, area=Cui.CuiArea0, codesToDelete=['FN'], keptLegs=kept_legs)
        if len(kept_legs) > 0:
            crew_kept_legs.append((crewid, start_time_hb, end_time_hb, kept_legs))

    # If there were activities that could not be removed (i.e. non FN),
    # report them in a popup window.
    if len(crew_kept_legs) > 0:
        crew_lines = ["The following bids had activities that could not be removed.", '']
        for crewid, start_time_hb, end_time_hb, kept_legs in crew_kept_legs:
            crew_lines.append("Crew id %s, %s - %s:" % (crewid, start_time_hb, end_time_hb))
            for start, end, code, airport in kept_legs:
                if code == 'FLT':
                    crew_lines.append("%s, %s - %s" % (airport, start, end))
                else:
                    crew_lines.append("%s, %s - %s" % (code, start, end))
            crew_lines.append('')
        cfhExtensions.show("%s" % '\n'.join(crew_lines))

    return 0
