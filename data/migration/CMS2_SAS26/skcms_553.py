import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2015_06_03_a'


JUL1 = int(AbsTime.AbsTime('01JUL2015'))


def addPGRow(exist,ops, id, desc):
    if id in exist:
        dbrow = exist[id]
        if dbrow['si'] != desc:
            dbrow['si'] = desc
            ops.append(fixrunner.createOp('planning_group_set','U',dbrow))
        exist[id] = None # mark as handled
    else:
        ops.append(fixrunner.createOp('planning_group_set', 'N', {
            'id': id,
            'si': desc
        }))

def clrPGRows(exist,ops):
    for row in exist.values():
        if row is not None:
            ops.append(fixrunner.createOp('planning_group_set','D',row))


CIMBER_APRIL = [23044, 23079, 23111, 23259, 23264, 23278, 23295, 23306, 23313, 23369, 24952, 24975,
     24979, 25056, 25069, 25070, 25074, 25841, 25843, 24121, 25441, 20761, 25578, 27600]
CIMBER_MAY = [ 25850, 25862, 25866, 25870, 25881, 25899, 25910, 25929, 25935, 25982, 25986, 25995,
     25996, 25999, 26000, 26008, 26017, 26023, 26026, 26028, 26023, 26026, 26028,
     25571, 26044]


SAS = [
    85172, 87975, 87974, 87902, 87824, 87106, 86946, 86936, 86226, 86215, 86114, 85896, 85895, 85894,
    85854, 85852, 85707, 85706, 85698, 85693, 85640, 85635, 85628, 85328, 85180, 85175, 85162, 84177, 84175,
    84174, 84173, 84156, 84039, 84015, 44137, 38937, 38732, 38729, 29879, 29875, 29869, 29866, 29803, 29802,
    29773, 29770, 29729, 29717, 29713, 28819, 28818, 28814, 28813, 28792, 28777, 28734, 28726, 28659, 28657,
    28651, 28649, 28645, 28631, 28621, 28610, 28607, 28000, 27962, 27597, 27264, 26457, 26436, 26428, 26424,
    26240, 25799, 25746, 25731, 25622, 25429, 25399, 25303, 25250, 25168, 24216, 24211, 24193, 24143, 23002,
    23001, 22998, 22990, 22981, 22963, 22957, 22956, 22947, 22942, 22941, 22903, 22865, 22862, 22856, 22825,
    22779, 22777, 22761, 22756, 22728, 22411, 22241, 22235, 21962, 21954, 21899, 21696, 21186, 21175, 21112,
    21089, 20881, 20728, 20676, 20656, 20647, 20641, 17624, 17621, 17613, 17612, 16674, 14909, 14671, 14521, 11950,
    14783, 20418, 20456, 20510, 20528, 20578, 20994, 21103, 21605, 21946, 22015, 22260, 22352, 22357, 22385, 22446,
    22456, 22527, 22536, 22590, 22678, 22896, 22938, 22966, 22983, 23150, 23185, 23232, 23361, 23364, 23514,
    23581, 23713, 23743, 23859, 23860, 23940, 24129, 24145, 24429, 24438, 24506, 24648, 24695, 24723, 24865, 24951,
    25476, 25636, 25654, 25683, 25694, 25909, 25979, 26203, 26284, 26288, 26313, 26345, 26388, 26531, 26629,
    26633, 26641, 26664, 26674, 26724, 26769, 26779, 26816, 26839, 26901, 27071, 27221, 27242, 27262, 27263, 27307,
    27456, 27541, 27542, 27672, 27685, 27727, 27804, 27870, 27882, 27888, 27901, 27925, 27934, 27945, 27952, 27989,
    28004, 28016, 28053, 28078, 28100, 28220, 28262, 28398, 28463, 28476, 28514, 28546, 28569, 28583, 28641, 29007,
    29115, 29518, 29545, 29553, 29588, 29659, 29676, 29782, 29867, 42918, 49128, 61657, 84079, 84083,
    27927 ]


def init_ar(dic, ar, dt, company):
    for i in ar:
        dic[format(i,"05d")] = (dt,company,'QA','QA') # startdate, company, carrier, planning group
   
def process_hist_row(row,ops):
    v = row['region']
    if v=='SKL':
        v='SKN'
    if row['planning_group'] != v:
        row['planning_group'] = v
        ops.append(fixrunner.createOp('crew_employment','U',row)) 

def process_row(dic, row, ops):
    if row['crew'] in dic:
        st, cp, cr, pg  = dic[row['crew']]
        if cp is None:
            cp = row['company'] # not changed
        if row['validfrom'] > st:
            process_hist_row(row,ops)
            print "Cannot fix crew ",row['crew'],' which has later changes'
        elif row['validto'] <= st:
            process_hist_row(row,ops)
            print "Cannot fix crew ",row['crew'],' which has passed date'
        elif row['validfrom'] == st:
           if cp!=row['company'] or cr!=row['carrier'] or pg!=row['planning_group']:
               row['company'] = cp
               row['carrier'] = cr
               row['planning_group'] = pg
               ops.append(fixrunner.createOp('crew_employment','U',row))
	else: #split last period
            new_row = row.copy()
            row['validto'] = st
            v = row['region']
            if v=='SKL':
                v = 'SKN'
            row['planning_group'] = v
            ops.append(fixrunner.createOp('crew_employment','U',row))
            new_row['validfrom'] = st
            new_row['company'] = cp
            new_row['carrier'] = cr
            new_row['planning_group'] = pg
            new_row['si'] = 'Cimber migration'
            ops.append(fixrunner.createOp('crew_employment','N',new_row))
    else:
        process_hist_row(row,ops)
         

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    #print "starting"
    dic = {}
    ops = []
    cr_cimber_april = init_ar(dic,CIMBER_APRIL,JUL1,"QA") 
    cr_cimber_may = init_ar(dic,CIMBER_MAY,JUL1,"QA")
    cr_sas = init_ar(dic,SAS,JUL1,None)
    count=0
    exist = {}
    for pg_row in fixrunner.dbsearch(dc,'planning_group_set'):
        exist[pg_row['id']] = pg_row
    addPGRow(exist, ops,'SKS','SAS Sweden')
    addPGRow(exist, ops,'SKD','SAS Denmark')
    addPGRow(exist, ops,'SKN','SAS Norway')
    addPGRow(exist, ops,'SKI','SAS Intercontinental')
    addPGRow(exist, ops,'SKJ','SAS Japan')
    addPGRow(exist, ops,'SKK','SAS China')
    addPGRow(exist, ops,'QA','Cimber Air')
    clrPGRows(exist,ops)

    last_row = None 
    for row in fixrunner.dbsearch(dc,'crew_employment'):
        count += 1
        #if count<10 or row['crew']=='34913':
        #    print "row",count,row
        if last_row is not None:
            if  row['crew'] != last_row['crew']:
                process_row(dic,last_row,ops)
                last_row = None
        if last_row is None:
            last_row = row
        elif row['validfrom']>last_row['validfrom']:
            process_hist_row(last_row,ops)
            last_row = row
        else:
            process_hist_row(row,ops)
            
    if last_row is not None:
        process_row(dic,last_row,ops)
    #for o in ops:
    #    print o
    print "done,updates=",len(ops)
    return ops


fixit.program = 'skcms_553.py (%s)' % __version__

if __name__ == '__main__':
    fixit()


