"""
Test CrewManifests
"""

# ../../../report_sources/hidden/rs_crew_manifest.py
# ../../../report_sources/hidden/rs_33_9_master_crew_list.py
# ../../../report_sources/hidden/CrewManifestCN.py
# ../../../carmusr/paxlst/crew_manifest.py

from carmtest.framework import *

import os, stat

class crew_001_CrewManifests(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)
        self._now = None
        self.old_now = self.getNowTime()
        self.start, self.interval = self.rave().eval('fundamental.%pp_start%', 'fundamental.%pp_start% + 480:00')
        self.setNowTime(self.start)
        self.flight_to_china = self.flight_to('CN')
        #Disable since there are no flights to TH during summer
        self.flight_to_thailand = self.flight_to('TH') 
        self.flight_to_japan = self.flight_to('JP')
        self.flight_to_usa = self.flight_to('US')
        
    def flight_to(self, country):
        class Flight(object):
            def __init__(self, adep, udor, fd, flight_id):
                self.adep = adep
                self.udor = udor
                self.fd = fd
                self.flight_id = flight_id

        for _, adep, udor, fd, flight_id in self.rave().eval('sp_crew',
                               self.rave().foreach(self.rave().iter('iterators.flight_leg_set',
                                                   where=('leg.%is_flight_duty%',
                                                          'report_crewlists.%%leg_end_country%% = "%s"' % (country))),
                                                        #  'report_crewlists.%leg_start_utc% > fundamental.%pp_start%')),
                                                   'report_crewlists.%leg_adep%',
                                                   'report_crewlists.%leg_udor%',
                                                   'leg.%flight_descriptor%',
                                                   'report_crewlists.%leg_flight_id%',
                                                   ))[0]:
        
            return Flight(adep, udor, fd, flight_id)
        
        self.dataError("Did not find a flight to '%s'" % country)
        
    def _stdtest(self, values):
        rlist, use_delta = values
        self.assert_(use_delta, 'use_delta was not True')
        self.assert_(len(rlist) > 0, 'empty report list')
        for report in rlist:
            self.assert_('content' in report, 'no content')
            self.assert_(isinstance(report['content'], str), 'content not a string')
            self.assert_(len(report['content']) > 0, 'empty report')
            self.assert_('content-type' in report, 'no content-type')
            self.assertEqual(report['content-type'], 'text/plain')
            self.assert_('destination' in report, 'no destination')
            self.assertEqual(report['destination'], [('default', {})])

    def test_001_crewmanifest_cn_rs(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_china
        result = report.generate(((), {'fd': data.fd,
                                       'adep': data.adep,
                                       'udor': self.udor2str(data.udor),
                                       'country': 'CN'}))
        self._stdtest(result)

    def test_002_crewmanifest_cn_sched(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_china
        result = report.generate({'fd': data.fd,
                                  'adep': data.adep,
                                  'udor': self.udor2str(data.udor),
                                  'country': 'CN'})
        self._stdtest(result)

    def test_003_crewmanifest_us_rs(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_usa
        result = report.generate(((), {'fd': data.fd,
                                       'adep': data.adep,
                                       'udor': self.udor2str(data.udor),
                                       'country': 'US'}))
        self._stdtest(result)

    def test_004_crewmanifest_us_sched(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_usa
        result = report.generate({'fd': data.fd,
                                  'adep': data.adep,
                                  'udor': self.udor2str(data.udor),
                                  'country': 'US'})
        self._stdtest(result)

    def test_005_crewmanifest_jp_rs(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_japan
        result = report.generate(((),
                                  {'fd': data.fd,
                                   'adep': data.adep,
                                   'udor': self.udor2str(data.udor),
                                   'country': 'JP'}))
        self._stdtest(result)

    def test_006_crewmanifest_jp_sched(self):
        import report_sources.report_server.rs_crew_manifest as report
        data = self.flight_to_japan
        result = report.generate({'fd': data.fd,
                                  'adep': data.adep,
                                  'udor': self.udor2str(data.udor),
                                  'country': 'JP'})
        self._stdtest(result)

# There are no flights to Thailand between April-Oct,
#===============================================================================
#    def test_007_crewmanifest_th_rs(self):
#        import report_sources.report_server.rs_crew_manifest as report
#        data = self.flight_to_thailand
#        if data == None:
#            result = report.generate()
#        else:
#            result = report.generate(((), {'fd': data.fd,
#                                       'adep': data.adep,
#                                       'udor': self.udor2str(data.udor),
#                                       'country': 'TH'}))
#        self._stdtest(result)
# 
#    def test_008_crewmanifest_th_sched(self):
#        import report_sources.report_server.rs_crew_manifest as report
#        data = self.flight_to_thailand
#        if data == None:
#            result = report.generate()
#        else:
#            result = report.generate({'fd': data.fd,
#                                  'adep': data.adep,
#                                  'udor': self.udor2str(data.udor),
#                                  'country': 'TH'})
#        self._stdtest(result)
#===============================================================================

    def test_009_mcl_rs(self):
        import report_sources.report_server.rs_33_9_master_crew_list as mcl
        result = mcl.generate(((), {'start': self.start, 'interval': self.interval, 'incremental':False}))
        self._stdtest(result)
  
    def test_010_mcl_sched(self):
        import report_sources.report_server.rs_33_9_master_crew_list as mcl
        result = mcl.generate({'start': self.start, 'interval': self.interval, 'incremental':False})
        self._stdtest(result)

    def udor2str(self, t):
        return "%04d%02d%02d" % t.split()[:3]

    def tearDown(self):
        self.setNowTime(self.old_now)
    
