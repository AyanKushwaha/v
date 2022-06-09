"""
Customized parser for exchange rates imported from RACER system.
"""

# imports ================================================================{{{1
from carmensystems.dig.framework import carmentime
from carmensystems.dig.framework.handler import MessageHandlerBase,CallNextHandlerResult
from carmensystems.dig.framework import dave
from carmensystems.dig.messagehandlers.dave import DaveContentType

# classes ================================================================{{{1

# CurrencyParser ---------------------------------------------------------{{{2
class CurrencyParser(MessageHandlerBase):
    """
    The CurrencyParser gets one line at the time. Each line contains conversion
    factors for the three nordic currencies.  The validto field has to be reset
    for older entries.
    """
    def __init__(self, name=None):
        super(CurrencyParser,self).__init__(name)

    def handle(self, message):
        line = message.content
        self._services.logger.debug("Parsing line: %s" % line)
        self.ops = []

        year = int(line[7:9])
        month = int(line[9:11])
        day = int(line[11:13])
        curr = line[13:16]
        f1 = int(line[16])
        sek = int(line[18:26])
        dkk = int(line[26:34])
        nok = int(line[34:42])

        # This will be 'validfrom' date
        date = carmentime.convertTime('%d-%02d-%02dT00:00Z' %(2000 + year, month, day))

        # Let next 'validto' be 30 days ahead
        nextdate = date + (30 * 1440)

        # Reset old 'validto' dates, to 1 day before next validfrom
        self.__reset(curr, date - 1440)

        base = {
            'cur': curr,
            'validfrom': date,
            'validto': nextdate,
            'unit': 10 ** (f1 + 3),
        }
        currencies = [{'reference': 'SEK', 'rate': sek},
                      {'reference': 'DKK', 'rate': dkk},
                      {'reference': 'NOK', 'rate': nok}]

        for c in currencies:
            c.update(base)
            self.ops.append(dave.createOp('exchange_rate', "W", c))

        message.setContent((None,None, self.ops), DaveContentType())
        return CallNextHandlerResult()

    def __reset(self, currency, cdate):
        search = dave.DaveSearch('exchange_rate', [ ('cur', '=', currency), "reference IN ('SEK', 'DKK', 'NOK') AND (validto IS NULL OR validto > %d) AND validfrom < %d" % (cdate,cdate)])

        for r in self._services.getDaveConnector().runSearch(search):
            r['validto'] = cdate
            self.ops.append(dave.createOp('exchange_rate', "U", r))


# format ================================================================={{{1

# spec -------------------------------------------------------------------{{{2
# message ::= { records }
# record:
#
# felt1         CHR(1)     Always 'B'
# felt2         NUM(6)     N/A
# year          NUM(2)     Year
# month         NUM(2)     Month
# day           NUM(2)     Day
# code          CHR(3)     Currency ID
# factor-1      NUM(1)     Number of decimals (- 3)
# factor-2      NUM(1)     Unknown stuff
# sek           NUM(8)     Currency in SEK
# dkK           NUM(8)     Currency in DKK
# nok           NUM(8)     Currency in NOK
# gb            NUM(8)     Currency in GBP
# us            NUM(8)     Currency in USD

# sample ------------------------------------------------------------------{{{2
#         1         2         3         4         5
# 1234567890123456789012345678901234567890123456789012345687
# ----------------------------------------------------------
#
# B010362060201AUD120005737500046382000505280002356800013302

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
