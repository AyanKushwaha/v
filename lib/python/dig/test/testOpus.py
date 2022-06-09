# -*- coding: utf-8 -*-

"""Opus testing"""
__metaclass__ = type

import unittest
import sys
import os

from carmensystems.dig.framework.handler import Message,CallNextHandlerResult,Services,TextContentType
from carmensystems.dig.framework.logging import Logger
from carmensystems.dig.framework.dave import NewDaveOperation,DaveSearch

from test.carmensystems.dig.framework.utils import TestDaveBase
#import test.carmensystems.dig.framework.utils
#test.carmensystems.dig.framework.utils.FirebirdDb._dbOrigDir = '/users/acosta/src/dig/build/test_schemas'

from dig.opusxmlparser import OPUSParser
#__file__ = "."

class TestOpus(TestDaveBase):

    _dbSchema='digairtest'
    _dbOrigDir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')

    def testSimpleMvt(self):
        handler = OPUSParser()
        handler.start(Services('TestChannel',handler,Logger(),self._connector))
        opusXML = open(self._getFileRelativePath(__file__,'opus_mvt1.xml')).read()
        msg = Message(opusXML)
        result = handler.handle(msg)
        self.assertTrue(isinstance(result,CallNextHandlerResult))
        sourceId,transId,ops = msg.content
        self.assertEquals(1,len(ops))

    def testSimpleRot(self):
        handler = OPUSParser()
        handler.start(Services('TestChannel',handler,Logger(),self._connector))
        opusXML = open(self._getFileRelativePath(__file__,'opus_rot1.xml')).read()
        msg = Message(opusXML)
        result = handler.handle(msg)
        self.assertTrue(isinstance(result,CallNextHandlerResult))
        sourceId,transId,ops = msg.content
        self.assertEquals(20,len(ops))

    def testSimpleTrainingMvt(self):
        handler = OPUSParser()
        handler.start(Services('TestChannel',handler,self._connector))
        #opusXML = open(self._getFileRelativePath(__file__,'opus_mvttr1.xml')).read()
        opusXML = open('opus_mvttr1.xml').read()
        msg = Message(opusXML, TextContentType('latin1'))
        result = handler.handle(msg)
        self.assertTrue(isinstance(result,CallNextHandlerResult))
        sourceId,transId,ops = msg.content
        self.assertEquals(2,len(ops))
        flightUpdate = ops[0]
        landingWrite = ops[1]
        if flightUpdate.entity != 'flight_leg':
            swap = flightUpdate
            flightUpdate = landingWrite
            landingWrite = swap
        self.assertTrue(5,landingWrite.values['nr_landings'])


    def testFullChannel(self):
        op = NewDaveOperation('flight_leg',
                               {
                                'udor':7552,
                                'fd':'SK 000152 ',
                                'adep':'GOT',
                                'ades':'ARN',
                                'aibt':0,
                                'aldt':0,
                                'statcode':'A',
                                'sobt':0,
                                'sibt':0,
                                })
        self._connector.getStorer().store([ op ])
        config = """
        <dig>
        <channel name="TestChannel" dbConn="%(dbConn)s" dbSchema="%(dbSchema)s" continueOnMessageError="False">
          <reader class="carmensystems.dig.readers.file.BinaryFileReader" filename="%(inputFileName)s"/>
          <messagehandlers>
            <messagehandler class="dig.opusxmlparser.OPUSParser"/>
            <messagehandler class="carmensystems.dig.messagehandlers.dave.DaveWriter"
               cacheSize="%(cacheSize)d"
               ignoreOutOfOrder="True"/>
          </messagehandlers>
        </channel>
        </dig>
        """

        testInputFileName = self._getFileRelativePath(__file__,'opus_mvt1.xml')
        self._runApp(config % {'inputFileName': testInputFileName, 'cacheSize': 0,
                               'dbConn': self._dbConn, 'dbSchema': self._dbSchema })

        flight_legs = self._connector.runSearch(DaveSearch('flight_leg', [ ('fd', '=','SK 000152 ') ]))
        self.assertEqual(1,len(flight_legs))
        leg = flight_legs[0]
        self.assertEqual(10875474, leg['aibt'])
        self.assertEquals(10875467, leg['aldt'])



if __name__ == "__main__":
    singleTestName = None

    #singleTestName = 'TestOpus.testFullChannel'
    singleTestName = 'TestOpus.testSimpleTrainingMvt'

    if singleTestName:
        unittest.main(argv = [sys.argv[0], singleTestName])
    else:
        unittest.main()

