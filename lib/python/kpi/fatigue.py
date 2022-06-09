import carmensystems.kpi as kpi
import carmusr.fatigue.kpi as fatigue_kpi

class CustomKPI(k.KPI):
    def create(self):
        bags = self.get_bags()['rosters']
        
        for kpi_element in fatigue_kpi.get_fatigue_kpis(bag):
            self.add(kpi_element)