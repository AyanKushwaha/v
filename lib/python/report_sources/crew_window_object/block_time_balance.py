"""
Block Time Balance Report
------------------------------------------

The report is grouped by base and rank.

@date: 22Feb2016
@author: Fredrik Sjunnesson
@org: Jeppesen Systems AB
"""

import report_sources.include.block_time_balance as block_time_balance


class Report(block_time_balance.Report):

    def get_scope(self):
        """
        Should return the scope of the report, .i.e. 'window', 'margin'(, or 'plan')
        """
        return "margin"

    def get_type(self):
        """
        Should return the type of the report, i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        return "roster"

if __name__ == "__main__":
    import carmstd.report_generation as rg
    #reload(block_time_balance)
    rg.reload_and_display_report()
