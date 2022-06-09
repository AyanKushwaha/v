""" splits lines of incoming message with length exceeding 'linesize'
characters into lines of size 'linesize' )each terminated by a by a new line
character) """ 

import re, string
import types
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors

class MessageSplitFilter(MessageHandlerBase):
    """ splits message into lines of specified max. length """
    def __init__(self, linesize, skipIfStartsWith='<?xml |*|<mvt |*|<rot ', name=None):
        super(MessageSplitFilter, self).__init__(name)

        # read configuration;
        # 1) get line length from config
        self.linesize = int(linesize, 10)

        # prepare list of patterns for hands off
        self.handsOff = skipIfStartsWith.split('|*|')
        
    def handle(self, message):
        # Ignore if linesize not feasible
        if self.linesize <= 0:
            return CallNextHandlerResult()

        # Keep hands off certain messages
        for pattern in self.handsOff:
            if message.content.startswith(pattern):
                return CallNextHandlerResult()

        # first, split message at natural line breaks
        split_lines = []
        data_lines = message.content.splitlines()
        
        # second, split too long lines
        for line in data_lines:
            if len(line) == 0:
                continue
            elif len(line) <= self.linesize:
                split_lines.append(line)
            else:
                self._services.logger.debug("Splitting message. Line is %d chars" % len(line))
                i = 0
                while i < len(line):
                    split_lines.append(line[i:i+self.linesize])
                    i += self.linesize

        message.setContent(string.join(map(lambda f: string.strip(f, '\n'), split_lines), '\n'), message.contentType)

        return CallNextHandlerResult()
