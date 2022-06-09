from AbsTime import AbsTime
from RelTime import RelTime
ABSTIME = 'AbsTime'
BOOLEAN = 'Boolean'
INTEGER = 'Integer'
RELTIME = 'RelTime'
STRING = 'String'

class DataConverter(object):
    @staticmethod
    def convertToType(type, data):
        if type == INTEGER:
            return int(data)
        if type == STRING:
            return data
        elif type == BOOLEAN:
            return bool(data)
        elif type == ABSTIME:
            return AbsTime(data)
        elif type == RELTIME:
            return RelTime(data)
        else:
            raise ValueError('Unsuported type to convert to')
      
    @staticmethod  
    def convertToData(type, data):
        if type == INTEGER:
            return str(data)
        if type == STRING:
            return data
        elif type == BOOLEAN:
            return str(data)
        elif type == ABSTIME:
            return str(data)
        elif type == RELTIME:
            return str(data)
        else:
            raise ValueError('Unsuported type to convert from')
