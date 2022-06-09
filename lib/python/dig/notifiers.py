import time
import os

from carmensystems.dig.framework import handler, notifier, errors
from carmensystems.dig.jmq import metaRequestMessage

class SKLogFormatter(object):
    """ This formatter outputs the original mq message received by the
        MQReader, formatted in SKLog format.
        If the message does not originate from an MQReader it falls back
        to the default formatter.
    """

    def format(self, now, message, error):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))
        if message is not None and message.metadata.has_key(metaRequestMessage):
            orgMsg = message.metadata[metaRequestMessage]
            try:
                # Use mq put time if available
                mqputtime = orgMsg.putDateTime
                timestamp = mqputtime.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))
            text = ("\nSKLogEntry;%s\n"%timestamp) + orgMsg.content
            if isinstance(text, unicode):
                contentType = handler.UnicodeContentType()
            else:
                contentType = handler.TextContentType(encoding='latin-1')
            return (text, contentType)
        else:
            default = notifier.DefaultFormatter()
            return default.format(timestamp, message, error)


class PerformanceFormatter(object):
    """ This formatter outputs the original mq message received by the
        MQReader, along with a performance error message.
        If the message does not originate from an MQReader it falls back
        to the default formatter.
    """

    def format(self, now, message, error):
        if message is not None and message.metadata.has_key(metaRequestMessage):
            orgMsg = message.metadata[metaRequestMessage]
            try:
                # Use mq put time if available
                mqputtime = orgMsg.putDateTime
                timestamp = mqputtime.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))
            text = "%s: %s %s\n" % (timestamp, orgMsg.content, str(error))
            contentType = handler.TextContentType(encoding='latin-1')
            return (text, contentType)
        else:
            default = notifier.DefaultFormatter()
            return default.format(now, message, error)


class TruncatingFormatter(object):
    """This formatter is identical to DefaultFormatter except that it
       truncates message content if larger than 10000 characters.
    """

    def format(self, now, message, error):
        text = '%s: %s' % (error.__class__.__name__, error)
        if message is not None:
            text += '\nContent: %s' % (message.content[:10000])
            if len(message.content) > 10000:
                text += ' ...\n(Content intentionally truncated)'
        text += '\n'

        if isinstance(text, unicode):
            contentType = handler.UnicodeContentType()
        else:
            contentType = handler.TextContentType(encoding='latin-1')
        return (text, contentType)


class TracebackFormatter(object):
    """This formatter is identical to DefaultFormatter but it also
       displays a traceback for an exception.
    """

    def format(self, now, message, error):
        text = 'Time: %s\n' % now
        text += '%s: %s\n' % (error.__class__.__name__, error)
        if message is not None:
            text += 'Content: %s\n' % (message.content,)
        text += "\n"
        import traceback
        if hasattr(error, 'causedBy'):
            text += "Caused by: %s\n" % error.causedBy
        text += traceback.format_exc()
        if isinstance(text, unicode):
            contentType = handler.UnicodeContentType()
        else:
            contentType = handler.TextContentType(encoding='latin-1')

        return (text, contentType)


class FileMover(notifier.NotifierBase):
    """An error handler that moves a file.

    -------------------------
     Configurable Parameters
    -------------------------
    filename (str)
      Path to file where output is written.
      If the path to the file does not exist, it is created.

    fromDir (str)
      Path to directory to move from.

    toDir (str)
      Path to directory to move to.

    """
    def __init__(self, filename, fromDir, toDir):
        super(FileMover, self).__init__()

        self.__filename = filename
        self.__fromDir = fromDir
        self.__toDir = toDir
        try:
            os.makedirs(self.__toDir)
        except OSError:
            pass

    def notify(self, message, error):
        try:
            os.rename("%s/%s" % (self.__fromDir, self.__filename), "%s/%s" % (self.__toDir, self.__filename))
        except:
            pass
