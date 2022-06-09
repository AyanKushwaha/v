

"""
Create report of Overlaps to be removed.
"""
import Cui
import carmensystems.publisher.api as prt
import carmusr.resolve_overlaps as ro

from report_sources.include.SASReport import SASReport


# Report ================================================================={{{1
class OverlapReport(SASReport):
    def create(self):
        SASReport.create(self, "Resolve Overlaps", showPlanData=False)
        save_mode = bool(int(self.arg('SAVE')))
        ops = ro.run(commit=save_mode)

        crew = {}
        for r in ops.removals:
            t = (r.start_hb, '-', r, None)
            if r.empno in crew:
                crew[r.empno].append(t)
            else:
                crew[r.empno] = [t]

        for r, interval in ops.additions:
            t = (interval.first, '+', r, interval)
            if r.empno in crew:
                crew[r.empno].append(t)
            else:
                crew[r.empno] = [t]

        for e in sorted(crew.keys()):
            first = True
            for _, status, obj, interval in sorted(crew[e]):
                if first:
                    self.add(
                        prt.Row(
                            prt.Column(obj.empno),
                            prt.Column(obj.logname, colspan=7),
                            border=prt.border(bottom=1)))
                    first = False

                if status == '-':
                    s = 'Remove'

                    if obj.rave_module == 'trip':
                        self.add(prt.Row(
                            prt.Column(s),
                            prt.Column('Trip'),
                            prt.Column(obj.code),
                            prt.Column(obj.start_station),
                            prt.Column(str(obj.start_hb)),
                            prt.Column('-'),
                            prt.Column(str(obj.end_hb)),
                            prt.Column(obj.end_station)))
                    else:
                        if obj.is_pact_or_off:
                            code = obj.code
                        else:
                            code = obj.flight_id
                        self.add(prt.Row(
                            prt.Column(s),
                            prt.Column('Leg'),
                            prt.Column(code),
                            prt.Column(obj.start_station),
                            prt.Column(str(obj.start_hb)),
                            prt.Column('-'),
                            prt.Column(str(obj.end_hb)),
                            prt.Column(obj.end_station)))

                else:
                    s = 'Add'
                    self.add(prt.Row(
                        prt.Column(s),
                        prt.Column('Leg'),
                        prt.Column(obj.code),
                        prt.Column(obj.start_station),
                        prt.Column(str(interval.first)),
                        prt.Column('-'),
                        prt.Column(str(interval.last)),
                        prt.Column(obj.end_station)))
                self.page0()
            self.add(prt.Row(height=24))
            self.page()

    @classmethod
    def run_report(cls, save=False):
        args = 'SAVE=%s' % int(save)
        Cui.CuiCrgDisplayTypesetReport(Cui.gpc_info, Cui.CuiWhichArea,
                'window', '%s.py' % cls.__name__, 0, args)


# run ===================================================================={{{1
run = OverlapReport.run_report


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    run()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
