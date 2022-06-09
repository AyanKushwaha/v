#!/usr/bin/env python
# coding: utf-8

# Python imports
import logging
from pprint import pformat

# CARMSYS imports
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult

logger = logging.getLogger(__name__)

####################
# Use by adding the following to your DIG channel:
# <messagehandler
#  class="dig.messagehandlerdebugger.MessagePrinter"
#  name="debug_destinations"/>
################

class MessagePrinter(MessageHandlerBase):
    """Printing out info about an object"""

    def handle(self, message):
        if hasattr(message, 'meta'):
            logger.info('meta %s', pformat(message.meta))
        if hasattr(message, 'content'):
            logger.info('content %s', pformat(message.content))
        else:
            logger.info('message %s', pformat(message.content))
        return CallNextHandlerResult()
