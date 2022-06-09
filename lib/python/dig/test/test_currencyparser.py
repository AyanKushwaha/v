import unittest
import currencyparser
import currencyparser_old

#Run with "python -m test.test_currencyparser" from the parent directory

TESTDATA_LOCATION = 'testdata/CUR140401.TXT'


class MockMessage(object):
    def setContent(self, value, t=None):
        self.content = value
        self.contentType = t

    def __str__(self):
        return str(self.content) + str(self.t)



class MockServices(object):
    def __init__(self):
        self.logger = MockLogger()


class MockLogger(object):
    def debug(self, *args, **kwds):
        pass


def mock_reset(*args, **kwds):
    pass


class TestCurrencyParserOldNew(unittest.TestCase):
    """
    Tests to verify that the new currency parser produces the same output as
    the old parser.
    """
    def setUp(self):
        with open(TESTDATA_LOCATION) as td:
            self.message_text = td.read().strip()

        #instantiate the new parser
        self.parser = currencyparser.CurrencyParser()
        self.parser._services = MockServices()

        #we need to intercept calls to __reset(self, currency, cdate) to test
        #the unit in isolation, the name __reset gets mangled by python, hence
        #the following weird assignment
        self.parser._CurrencyParser__reset = mock_reset

        #instantiate the old version of the parser to use as reference
        self.old_parser = currencyparser_old.CurrencyParser()
        self.old_parser._services = MockServices()
        self.old_parser._CurrencyParser__reset = mock_reset

    def tearDown(self):
        pass
    
    def test_parse_line_old_new(self):
        """
        Let both the old and new currency parsers handle a single line
        message and compare the result, both parsers should generate the 
        same dave operations in the message
        """
        m_text = self.message_text.split('\n')[0]
        m_old = MockMessage()
        m_old.setContent(m_text)
        
        m_new = MockMessage()
        m_new.setContent(m_text)
        
        self.old_parser.handle(m_old)
        self.parser.handle(m_new)
        
        for o, n in zip(m_old.content[2], m_new.content[2]):
            self.assertEquals(o, n)

    def test_parse_line_old_new_multiple_lines(self):
        """
        Check that the new parser handles every line of the sample data
        the same as the old parser
        """
        for line in self.message_text.split('\n'):
            m_old = MockMessage()
            m_old.setContent(line)

            m_new = MockMessage()
            m_new.setContent(line)

            self.old_parser.handle(m_old)
            self.parser.handle(m_new)

            for o, n in zip(m_old.content[2], m_new.content[2]):
                self.assertEquals(o, n)
    
    def test_content_type_equality(self):
        m_text = self.message_text.split('\n')[0]
        m_old = MockMessage()
        m_old.setContent(m_text)

        m_new = MockMessage()
        m_new.setContent(m_text)

        self.parser.handle(m_new)
        self.old_parser.handle(m_old)

        self.assertEquals(m_old.contentType, m_new.contentType)

    def test_content_type_not_none(self):
        m_text = self.message_text.split('\n')[0]
        m = MockMessage()
        m.setContent(m_text)

        self.parser.handle(m)
        self.assertTrue(m.contentType is not None)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
