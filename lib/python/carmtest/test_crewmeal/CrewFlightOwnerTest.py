"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *

from dig.fiaparser import FIAParser

from carmensystems.dig.framework.handler import Message, TextContentType
from carmensystems.dig.framework.dave import WriteDaveOperation, DeleteDaveOperation
from carmensystems.dig.messagehandlers.dave import DaveContentType 
from carmensystems.dig.messagehandlers.reports import metaReports, metaDelta


class LoggerMockup(object):
    """ The FIA Parser uses a logger that is not available, lets make one """
    
    def __init__(self):
        pass
    
    def info(self, msg):
        print msg
        
    def warning(self, msg):
        print msg

    def error(self, msg):
        print msg
    
    def debug(self, msg):
        print msg


class DaveConnectionMockup(object):
    """ The FIA Parser uses a DaveConnection that is not available, lets make one """
    
    def __init__(self):
        pass
    
    def runSearch(self, expr):
        return []
    
class SerivceMockup(object):
    """ The FIA Parser uses a a service class that is not available, lets make one """
        
    def __init__(self, logger, daveConnector):
        self.logger = logger
        self.daveConnector = daveConnector
    
    def getDaveConnector(self):
        return self.daveConnector


class crew_002_FlightOwnerTest(TestFixture):

    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)
        self.parser = FIAParser("UnitTest")
        self.parser._services = SerivceMockup(LoggerMockup(), DaveConnectionMockup())

    @staticmethod
    def count_dave_operations(message):
        """ Counts the different types of Dave operations""" 
        
        nofWrites = 0
        nofDeletes = 0
        nofUnknowns = 0
        
        for op in message.content[2]:
            if isinstance(op, WriteDaveOperation):
                nofWrites += 1
            elif isinstance(op, DeleteDaveOperation):
                nofDeletes += 1
            else:
                nofUnknowns += 1 
                
        return nofWrites, nofDeletes, nofUnknowns

    @staticmethod
    def get_errors(message):
        """ Gets a list of errors and returns them as a list """ 
                
        if len(message.metadata[metaReports]) == 0:
            return []
        
        # Get the dictionary
        errors = message.metadata[metaReports][0]
        errors = errors['content'].splitlines()        
        return errors


    def test_001_basic(self):
        """ Basic test that the the flight records are created properly """
        
        content = "A2012-03-252012-10-2812345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-10-299999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n"
        
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 7)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 0)
            

    def test_002_invalidLine(self):
        """ Verify that an error occurs when for malformed input line """
        
        content = "A2012-03-252012-10-28123457  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" 
        
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 0)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 1)
        for error in errors:
            self.assertNotEqual(error.find("Failed to parse line"), -1)

        
        
    def test_003_overlapping1(self):
        """ Verify that an error occurs when overlapping period """
        
        content = "A2012-03-252012-10-2812345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" 
        
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 6)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 1)
        for error in errors:
            self.assertNotEqual(error.find("Overlapping period"), -1)
        

    def test_004_overlapping2(self):
        """ Verify that an error occurs when overlapping period """
        
        content = "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-2812345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  001\n"
                           
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 1)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 2)
        for error in errors:
            self.assertNotEqual(error.find("Overlapping period"), -1)



    def test_005_overlapping3(self):
        """ Verify that an error occurs when overlapping period """
        
        content = "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-2712345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  001\n"
                           
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 6)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 1)
        for error in errors:
            self.assertNotEqual(error.find("Overlapping period"), -1)



    def test_006_double_leg_number(self):
        """ Verify that a different leg numbers do not produce error """
        
        content = "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-11-2812345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  002\n" + \
                  "A2012-03-252012-11-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  002\n"
                           
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 7)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 0)

    def test_007_different_stations(self):
        """ Verify that a different stations do not produce error """
        
        content = "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-11-2812345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MCPH  OSL  001\n" + \
                  "A2012-03-252012-11-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MCPH  OSL  001\n"
                           
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 7)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 0)


    def test_008_different_flight_types(self):
        """ Verify that an error does occurs when overlapping period with different flight types"""
        
        content = "A2012-10-289999-12-311234567SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 AOSL  CPH  001\n" + \
                  "A2012-03-252012-10-2712345  SASSAS             SKA  ROUTE SECT TOTALRSN  NORWAY          NS   NORWAY SCHED    2I   NO INTRASC SCHED2DN  NORWAY-DENMARK  728  NO OSL-CPH      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 AOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 MOSL  CPH  001\n" + \
                  "A2012-03-252012-10-28     6 SASSAS             SKA  ROUTE SECT TOTALRSD  DENMARK         DS   DENMARK SCHED   1I   DK INTRASC SCHED1DN  DENMARK-NORWAY  701  DK CPH-OSL      SK 1453 DOSL  CPH  001\n"
                           
        message = Message(content, TextContentType('latin-1'))
        
        self.parser.handle(message)

        nofWrites, nofDeletes, nofUnknowns = self.count_dave_operations(message)
                    
        self.assertEquals(nofWrites, 6)
        self.assertEquals(nofDeletes, 0)
        self.assertEquals(nofUnknowns, 0)
                
        errors = self.get_errors(message)
        self.assertEqual(len(errors), 0)


