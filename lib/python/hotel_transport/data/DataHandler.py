# coding: utf-8
# Python imports
import time
from datetime import datetime, timedelta
from uuid import uuid4

# Hotel and transport imports
import carmensystems.rave.api as rave


def structure_messages(built_objects, message_type, chunk_size=1):
    """
    Structures the messages to be put on the message queue

    :param built_objects: one dict or many dicts in a list
    :param message_type: hotel, transport
    :param chunk_size: limiting value for how many objects should be sent at a time
    :return: count: total number of hotels
    :return: messages: the message(s) to be put on the Message Queue
    """
    count = 0
    messages = []
    for chunk in chunks(built_objects, chunk_size):
        size = len(chunk)
        messages.append(
            {"request_id":str(uuid4()),
                message_type:chunk}
            )
        count += size
   
    return count, messages

def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    For Python3: Change xrange -> range
    """
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]
