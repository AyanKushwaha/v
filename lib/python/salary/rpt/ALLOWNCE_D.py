from salary.rpt import EmailReport
import salary.api as api

class S3(EmailReport):
    
    def __init__(self, rd):
        dict.__init__(self)
        self.rundata = rd
        records = api.getDailyRecordsFor(rd.runid)
        # repacking the dictionary
        for extperkey in records:
            for extartid in records[extperkey]:
                for offset, amount in records[extperkey][extartid]:
                    if not extartid in self.keys():
                        self[extartid] = [1, amount]
                    else:
                        self[extartid][0] += 1
                        self[extartid][1] += amount


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
