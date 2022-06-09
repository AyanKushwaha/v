# Calculate average trip length
# Assumes that there is a trip.days variable in the
# ruleset.
 
import carmensystems.rave.api as r
import carmensystems.kpi as k

class CustomKPI(k.KPI):
    def create(self):
        bags = self.get_bags() # Can only be called once
        trips_bag = bags['trips']
        # Calculate trip lengths
        lengths = []
        for atrip in trips_bag.iterators.trip_set():
            days = atrip.trip.days()
            lengths.append(days)
        # Create the actual KPI value
        avg = sum(lengths)/float(len(lengths))
        self.add(k.KpiValue("Avg. trip length", "%.2f" % avg))
