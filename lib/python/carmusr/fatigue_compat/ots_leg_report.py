import carmusr.fatigue_compat.ots_standardreport


class LegReport(carmusr.fatigue_compat.ots_standardreport.StandardReport):

    def get_scope(self):
        """
        Should return the scope of the report, .i.e. 'window', 'margin'(, or 'plan')
        """
        return "window"

    def get_type(self):
        """
        Should return the type of the report, i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        return "leg"
