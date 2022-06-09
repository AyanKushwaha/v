
#

"""
Create and handle temporary table used for displaying Rudobs and to set
interval for publication (TRACKING_INFORMED)
"""

import Cui
import carmensystems.rave.api as R
import modelserver as M

from tm import TM, TempTable


class InformedTempTable(TempTable):
    """
    A temporary table that is used to display periods that are marked INFORMED.
    This table is used from Rave, to display Rudobs, it is also iterated in the
    save process, and then emptied.
    """
    def __init__(self, table_name_param='publish.%tmp_inform_table%'):
        TempTable.__init__(self,
            R.param(table_name_param).value(),
            # Has to use StringColumn, since Rave does not understand RefColumn
            # for temporary tables.
            [
                M.StringColumn('crew'),
                M.TimeColumn('start_time'), 
            ],
            [
                M.TimeColumn('end_time'),
                M.StringColumn("si"),
            ])
            
    def is_informed(self, crew, utc):
        for r in self.search('(crew=%s)' % crew):
            t = self.to_utc(r)
            if t[0] <= utc < t[1]:
                return True
        return False
        
    def clear(self):
        self.removeAll()
        Cui.CuiReloadTable(self.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)

    def to_utc(self, rec):
        """Return tuple (start_time, end_time) with UTC times for given crew."""
        return R.eval(
            'publish.%%hb_date_to_utc_time%%("%s", %s)' % (rec.crew, rec.start_time),
            'publish.%%hb_date_to_utc_time%%("%s", %s)' % (rec.crew, rec.end_time))


class InformedTempTableRowCreator:
    """
    Handle updates and iterations of temporary table for INFORMED periods.
    """

    def __init__(self, crew):
        self.crew = crew
        self.table = InformedTempTable()

    def __iter__(self):
        return iter(self.table.search('(crew=%s)' % self.crew))

    def create(self, st, et, si=None):
        rec = self.table.create((self.crew, st))
        rec.end_time = et
        if si:
            rec.si = str(si)
        return rec

    def reload(self):
        Cui.CuiReloadTable(self.table.table_name(), Cui.CUI_RELOAD_TABLE_SILENT)


def init(table_name_param='publish.%tmp_inform_table%'):
    """Initialization code, creates informed temporary table. The function has
    to be loaded in e.g. FileHandlingExt."""
    _ = InformedTempTable(table_name_param)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
