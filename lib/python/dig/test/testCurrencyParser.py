# -*- coding: utf-8 -*-

"""Opus testing"""
__metaclass__ = type

import unittest
import sys
import os

from carmensystems.dig.framework.handler import Message,CallNextHandlerResult,Services
from carmensystems.dig.framework.logging import Logger
from carmensystems.dig.framework.dave import NewDaveOperation,DaveSearch

from test.carmensystems.dig.framework.utils import TestDaveBase

from sas.currencyparser import CurrencyParser

class TestCurrency(TestDaveBase):

    _dbSchema='digairtest'

    data= """
    B017842060201AED120002175700017588000191600006215200035080
    B015322060201ANG320448766003627857039521440003013200017007
    B019732060201AOA320009918200080179000873460136340200769544
    B010322060201ARS120002646300021392000233050005109900028842
    B010362060201AUD120005737500046382000505280002356800013302
    B015332060201AWG120004462500036075000393000003030100017103
    B010522060201BBD120004033800032609000355240003352200018921
    """
    currencies = [ l.strip()[13:16] for l in data.split("\n") if l.strip() ]
    sekRates = [ int(l.strip()[18:26]) for l in data.split("\n") if l.strip() ]
    ddkRates = [ int(l.strip()[26:34]) for l in data.split("\n") if l.strip() ]
    nokRates = [ int(l.strip()[34:42]) for l in data.split("\n") if l.strip() ]
    rates = { 'SEK':sekRates, 'DKK':ddkRates, 'NOK':nokRates }

    def testSimpleMvt(self):
        handler = CurrencyParser()
        handler.start(Services('TestChannel',handler,Logger(),self._connector))
        dataLines = [ l.strip() for l in self.data.split("\n") if l.strip() ]
        for i,line in enumerate(dataLines):
            msg = Message(line)
            result = handler.handle(msg)
            self.assertTrue(isinstance(result,CallNextHandlerResult))
            sourceId,transId,ops = msg.content
            for o in ops:
                self.assertEquals(self.currencies[i], o.values['cur'])
                refCur = o.values['reference']
                self.assertEquals(self.rates[refCur][i], o.values['rate'])
            self.assertEquals(3,len(ops))

if __name__ == "__main__":
    singleTestName = None

    #singleTestName = 'TestOpus.testFullChannel'

    if singleTestName:
        unittest.main(argv = [sys.argv[0], singleTestName])
    else:
        unittest.main()

