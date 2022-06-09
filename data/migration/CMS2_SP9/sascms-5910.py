# coding=latin-1
"""
* Add schengen countries to rave_paramset_set
* Add new region to geo_region_set
"""

import adhoc.fixrunner as fixrunner
from AbsTime import AbsTime
from AbsDate import AbsDate
import os
__version__ = '1'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    validfrom = int(AbsTime('01Jan1986'))/1440
    validto = int(AbsTime('31Dec2035'))/1440
    ops = []

    ## Add new region groups
    if len(fixrunner.dbsearch(dc, 'geo_region_set', "id='ES'")) ==0:
        ops.append(fixrunner.createOp('geo_region_set', 'N', {'id':'ES',
                                                              'si':'European Schengen'}))
    else:
        print "'ES' already exists in table geo_region_set"
        
    if len(fixrunner.dbsearch(dc, 'geo_region_set', "id='ENS'")) ==0:
       ops.append(fixrunner.createOp('geo_region_set', 'N', {'id':'ENS',
                                                             'si':'European None Schengen'}))
    else:
        print "'ENS' already exists in table geo_region_set"
     

    ## Add a parameter for the schengen_countries
    if len(fixrunner.dbsearch(dc, 'rave_paramset_set', "id='schengen_countries'")) ==0:
        ops.append(fixrunner.createOp('rave_paramset_set', 'N', {'id':'schengen_countries',
                                                                 'description':'Countries belonging to Schengen'}))
    else:
        print "'schengen_countries' already exists in table rave_paramset_set"

    # Insert the schengen countries
    #Belgien, Danmark, Estland, Finland, Frankrike, Grekland, Island, Italien, Lettland, Liechtenstein, Litauen, 
    #Luxemburg, Malta, Nederländerna, Norge, Polen, Portugal, Schweiz, Slovakien, Slovenien, Spanien, Sverige, 
    #Tjeckien, Tyskland, Ungern och Österrike
    schengen_countries = ['BE', 'DK', 'EE', 'FI', 'FR', 'GR', 'IS', 'IT', 'LV', 'LI', 'LT', 
                 'LU', 'MT', 'NL', 'NO', 'PL', 'PT', 'CH', 'SK', 'SI', 'ES', 'SE', 
                 'CZ', 'DE', 'HU', 'AT']
    for c in schengen_countries:
        if len(fixrunner.dbsearch(dc, 'rave_string_paramset', "ravevar='schengen_countries' and val='%s'" % c)) ==0:
            ops.append(fixrunner.createOp('rave_string_paramset', 'N', {'ravevar':'schengen_countries',
                                                                        'val':c,
                                                                        'validfrom':validfrom,
                                                                        'validto':validto,
                                                                        'si':''}))
        else:
            print "'%s' already exists in table rave_string_paramset" % c
    # Update the minimum_connection_times, replace E with ES/ENS
    l = fixrunner.dbsearch(dc, 'minimum_connection', "(arrtype='E' or deptype='E')")

    validfrom1 = int(AbsTime('01Jan1986'))/1440
    validto1 = int(AbsTime('31Oct2013'))/1440
    validfrom2 = int(AbsTime('01Nov2013'))/1440
    validto2 = int(AbsTime('31Dec2035'))/1440
    for i in xrange(0, len(l)):
        arrtype = False
        deptype = False
        if l[i]['arrtype'] == 'E':
            arrtype = True
        if l[i]['deptype'] =='E':
            deptype = True

        arrtypes = []
        deptypes = []
        trusted = []       
        vfrom = []
        vto= []
        cnxfc = []
        cnxcc = [] 
        if arrtype and not deptype:
            #old row E->ES
            arrtypes.append('ES')
            deptypes.append(l[i]['deptype'])
            trusted.append(l[i]['trusted'])
            vfrom.append(validfrom1)
            vto.append(validto1)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])

            # new row E->ES
            arrtypes.append('ES')
            deptypes.append(l[i]['deptype'])
            trusted.append(0)
            vfrom.append(validfrom2)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc']+5)
            cnxcc.append(l[i]['cnxcc']+5)

            # old row E->ENS
            arrtypes.append('ENS')
            deptypes.append(l[i]['deptype'])
            trusted.append(l[i]['trusted'])
            vfrom.append(validfrom1)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])
            
        if not arrtype and deptype:
            #old row E->ES
            deptypes.append('ES')
            arrtypes.append(l[i]['arrtype'])
            trusted.append(l[i]['trusted'])
            vfrom.append(validfrom1)
            vto.append(validto1)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])

            # new row E->ES
            deptypes.append('ES')
            arrtypes.append(l[i]['arrtype'])
            trusted.append(0)
            vfrom.append(validfrom2)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc']+5)
            cnxcc.append(l[i]['cnxcc']+5)

            # old row E->ENS
            deptypes.append('ENS')
            arrtypes.append(l[i]['arrtype'])
            trusted.append(l[i]['trusted'])
            vfrom.append(validfrom1)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])
 
        if arrtype and deptype:
            deptypes.append('ES')
            arrtypes.append('ES')
            trusted.append(1)
            vfrom.append(validfrom1)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])
            
            deptypes.append('ENS')
            arrtypes.append('ENS')
            trusted.append(l[i]['trusted'])
            vfrom.append(validfrom1)
            vto.append(validto2)
            cnxfc.append(l[i]['cnxfc'])
            cnxcc.append(l[i]['cnxcc'])
         
        if arrtype or deptype:
            #print "Delete %s" % l[i] 
            ops.append(fixrunner.createOp('minimum_connection', 'D', {'region': l[i]['region'],
                                                                  'place': l[i]['place'],
                                                                  'islonghaul': l[i]['islonghaul'],
                                                                  'arrtype': l[i]['arrtype'],
                                                                  'deptype': l[i]['deptype'],
                                                                  'validfrom': l[i]['validfrom']}))
        
            for j in xrange(0, len(deptypes)):
                #print "insert %s,%s,%s,%s,%s,%s,%s" % (l[i]['region'], l[i]['place'], arrtypes[j], deptypes[j], trusted[j],vfrom[j],vto[j])
                ops.append(fixrunner.createOp('minimum_connection', 'N', {'region': l[i]['region'],
                                                                  'place': l[i]['place'],
                                                                  'islonghaul': l[i]['islonghaul'],
                                                                  'arrtype': arrtypes[j],
                                                                  'deptype': deptypes[j],
                                                                  'validfrom': vfrom[j],
                                                                  'validto': vto[j],
                                                                  'cnxfc': cnxfc[j],
                                                                  'cnxcc': cnxcc[j],
                                                                  'trusted': trusted[j]}))
             
    
    return ops

fixit.program = 'sascms-5910.py (%s)' % __version__

if __name__ == '__main__':
    fixit()
