#########################################
# Copyright Jeppesen Systems AB
"""
Various file utility dig handlers
"""
__docformat__ = 'restructuredtext en'
__metaclass__ = type

# imports ================================================================{{{1
import os, shutil, glob, tarfile
import time, datetime, sys, traceback
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult
from carmensystems.dig.framework import errors, utils
from carmensystems.dig.messagehandlers import reports, dave, file

# Message Handlers ======================================================={{{1
# FileCopy ==============================================================={{{2
class FileCopy(MessageHandlerBase):
    """
    Copy a named file. Optionally attach datestamp to filename.

    Options:
        filename        Path to the file that should be copied

        toDir           Directory where to put the copy

        timestamp       Optional. Format of timestamp to append to the
                        copied file. Timestamp is taken from the file
                        modification time and will be appended before
                        the file extension. E.g. '%y%m%d'

        move            Optional. Default "False". If True, original
                        file is removed.
    """
    def __init__(self, filename, toDir, timestamp=None, move='False', name=None):
        super(FileCopy, self).__init__(name)
        self.filename = filename
        self.toDir = toDir
        self.timestamp = timestamp
        self.move = False
        if move.upper() in ("TRUE","YES","1"):
            self.move = True

    def handle(self, message):
        self._services.logger.debug("Started...")
        try:
            filename = os.path.basename(self.filename)
            if not self.timestamp is None:
                (base, ext) = os.path.splitext(filename)
                mtime = os.path.getmtime(self.filename)
                datestamp = time.strftime(self.timestamp, time.gmtime(mtime))
                filename = base + datestamp + ext
            target = os.path.join(self.toDir, filename)
            if not os.path.exists(self.toDir):
                os.makedirs(self.toDir)
            if self.move:
                shutil.move(self.filename, target)
                self._services.logger.debug("Moved '%s' to '%s'" % (self.filename, target))
            else:
                shutil.copy2(self.filename, target)
                self._services.logger.debug("Copied '%s' to '%s'" % (self.filename, target))
        except Exception, e:
            raise errors.MessageError("Failed copying %s" % self.filename)
        self._services.logger.debug("Finished")
        return CallNextHandlerResult()

# FilePacker ============================================================={{{2
class FilePacker(MessageHandlerBase):
    """
    Checks the total number of stored files against the expected
    number. If not all files have arrived it just exits. Otherwise it
    packs all report files together into one file (tgz) and returns it
    as 'ReportsContentType' to the next handler in the call chain
    (normally an AddressInjector).

    Options:
        directory       Path to the directory where the files are stored.
                        The directory must exist.
                        Default: $CARMTMP/dig_temp

        pattern         Match pattern of the stored files. Complies with
                        the shell-style 'glob' method. Default: '*'

        numberOfFiles   Expected (minimum) number of files. If ommitted,
                        the handler attempts to get expected number from
                        message metadata [dig.xhandlers][NumberOfFiles]

        outputName      Name of temporary output (.tgz) as well as logical
                        output report name. Default: 'archive'.

        outputTimestamp Append timestamp (YYYYMMDD_hhmmss) to output
                        report file name e.g. archive20080715_092240.tgz
                        Valid values are "True","False". Default "False".
    """
    def __init__(self, directory=None, pattern='*', numberOfFiles=None, outputName='archive', outputTimestamp="False", name=None):
        super(FilePacker,self).__init__(name)
        if not directory:
            directory = os.path.join(os.path.expandvars("$CARMTMP"),"dig_temp")
        self.__path = directory
        self.__pattern = pattern
        self.__outputName = outputName
        self.__outputTimestamp = utils.convertToBoolean(outputTimestamp)
        self.__numberOfFiles = None
        if numberOfFiles:
            self.__numberOfFiles = int(numberOfFiles)

    def handle(self, message):
        self._services.logger.info("Started...")

        if self.__numberOfFiles:
            numberOfFiles = self.__numberOfFiles
        else:
            if not message.metadata.has_key('dig.xhandlers'):
                raise errors.ChannelConfigError("Cannot find metadata key 'dig.xhandlers'")
            metadata = message.metadata['dig.xhandlers']
            if not metadata.has_key('NumberOfFiles'):
                raise errors.MessageError("Cannot find metadata 'NumberOfFiles'")
            numberOfFiles = int(metadata['NumberOfFiles'])

        # Check if all reports have arrived
        try:
            os.chdir(self.__path)
            reportFiles = glob.glob(self.__pattern)
            # Exclude previously created archive(s) if available
            for reportFile in reportFiles:
                if reportFile.startswith(self.__outputName):
                    reportFiles.remove(reportFile)
        except Exception, e:
            raise errors.MessageError("Failed finding files in %s: %s" % (self.__path, str(e)))
        self._services.logger.debug("%d out of expected %d number of files have arrived" % (len(reportFiles), numberOfFiles))
        if len(reportFiles) < numberOfFiles:
            return ExitResult()

        # Pack all files together
        self._services.logger.info("Archiving files...")
        if self.__outputTimestamp:
            timestamp = self._services.now().strftime("%Y%m%d_%H%M%S")
            tmpTarFileName =  self.__outputName + timestamp + ".tar.gz"
        else:
            tmpTarFileName = self.__outputName + ".tar.gz"

        actualTarFileName = tmpTarFileName.replace(".tar.gz", ".tgz")
            
        try:
            tar = tarfile.open(tmpTarFileName, 'w:gz')
            for reportFile in reportFiles:
                tar.add(reportFile, reportFile)
                os.remove(reportFile)
            tar.close()
        except Exception, e:
            raise errors.MessageError("Failed packaging files in %s: %s" % (self.__path, str(e)))

        os.rename(tmpTarFileName, actualTarFileName)

        # Prepare ReportsContentType output
        message.setContent([{'content-type': "application/x-gzip",
                            'content-location': actualTarFileName,
                            'destination': [(self.__outputName,{})]
                            }], reports.ReportsContentType())
        self._services.logger.info("Finished")
        return CallNextHandlerResult()

# MessageRecorder ========================================================{{{2
class MessageRecorder(MessageHandlerBase):
    """
    This message handler writes down 'raw' messages from a dig-channel to file.
    Each message is prepended with a SKLogEntry header which makes it possible
    to later use the SKLogParser or sklogreplayfilter to play back messages
    in correct sequence.

    Parameters:
        log_directory   -   Directory to write files with recorded messages

        log_file_name   -   Static name of file with recorded messages. 
                            Cannot be used in combination with log_file_prefix.

        log_file_prefix -   If specified, file with recorded messages will
                            be constructed as <prefix>YYYYMMDD.log. Name
                            is changed at day shift. This parameter cannot
                            be used in combination with log_file_name.

        log_append      -   File is opened in append mode. Default "True".

        use_mq_timestamp-   Tries to create SKLogEntry timestamp based on
                            incoming MQ put time. Default "True". Note that
                            this is only meaningful in channles with MQReader.
    """
    def __init__(self,
                log_directory='',
                log_file_name=None,
                log_file_prefix=None,
                log_append="True",
                use_mq_timestamp="True",
                name=None):
        super(MessageRecorder, self).__init__(name)
        self.active = True

        self.logdir_name = log_directory
        self.logfile_name = log_file_name
        self.logfile_prefix = log_file_prefix
        self.use_mq_timestamp = use_mq_timestamp
        self.log_append = log_append

        if not self.logfile_name and not self.logfile_prefix:
            self.active = False

        if self.logfile_name and self.logfile_prefix:
            raise errors.ChannelConfigError("Cannot use both log_file_name and log_file_prefix")

        self.openStatic = True
        if self.logfile_prefix:
            self.openStatic = False

    def start(self, services):
        super(MessageRecorder, self).start(services)
        self._services.logger.debug("Started")
        if self.active and self.openStatic:
            # Try to open file for output
            try:
                if self.log_append.upper() not in ('0','FALSE'):
                    mode = "a"
                else:
                    mode = "w"
                self.logfile = open(os.path.join(self.logdir_name,self.logfile_name), mode)
            except IOError, io_e:
                self._services.logger.error("Could not open '%s' for output" % self.logfile_name)
                self.active = False
                traceback.print_exc()


    def handle(self, message):
        """ Log the call. Data is forwarded after logging. """
        self._services.logger.debug("Received %s message" % message.contentType)
        if not self.active:
            return CallNextHandlerResult()

        if not self.openStatic:
            # Try to open file for output
            utcdate_str = time.strftime("%Y%m%d",time.gmtime(time.time()))
            filename = "%s%s.log" % (self.logfile_prefix, utcdate_str)
            try:
                self.logfile = open(os.path.join(self.logdir_name,filename), 'a')
            except IOError, io_e:
                self._services.logger.error("handle Could not open '%s' for output" % filename).exception(io_e)
                self.active = False
                return CallNextHandlerResult()

        self._services.logger.debug("Writing to replay log")
        # Current time
        system_utc_str = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))
        if self.use_mq_timestamp.upper() not in ('0','FALSE'):
            # Try get puttime from mq header
            mqputtime = self.getPutTime(message.metadata)
            if mqputtime:
                system_utc_str = mqputtime.strftime("%Y-%m-%dT%H:%M:%S")

        # Write log
        if hasattr(message, 'rptfile'):
            self.logfile.write(("\nSKLogEntry;%s\n"%system_utc_str) + \
                               utils.toStringIfUnicode(message.rptfile))        
        elif message.contentType == dave.DaveContentType():
            self.logfile.write(("\nSKLogEntry;%s\n"%system_utc_str) + "Dave message logging is not supported")
        else:
            self.logfile.write(("\nSKLogEntry;%s\n"%system_utc_str) + \
                               str(utils.toStringIfUnicode(message.content)))
        self.logfile.flush()
        if not self.openStatic:
            self.logfile.close()

        return CallNextHandlerResult()

    def getPutTime(self, metadata):
        putTime = None
        key = 'carmensystems.dig.jmq.RequestMessage'
        if metadata.has_key(key):
            putTime = metadata[key].putDateTime
        return putTime

# MessageRecorder ========================================================{{{2
class ReportRecorder(MessageHandlerBase):
    """
    This message handler writes down message.reports to a file

    Parameters:
        log_directory   -   Directory to write files with recorded messages

        log_file_name   -   Static name of file with recorded messages.
                            Cannot be used in combination with log_file_prefix.

        log_file_prefix -   If specified, file with recorded messages will
                            be constructed as <prefix>YYYYMMDD.log. Name
                            is changed at day shift. This parameter cannot
                            be used in combination with log_file_name.

        log_append      -   File is opened in append mode. Default "True".

        use_timestamp   -   If set a timestamp is put into the file before
                            the reports are written to the file
    """
    def __init__(self,
                log_directory='',
                log_file_name=None,
                log_file_prefix=None,
                log_append="True",
                use_timestamp="True",
                name=None):
        super(ReportRecorder, self).__init__(name)
        self.active = True

        self.logdir_name = log_directory
        self.logfile_name = log_file_name
        self.logfile_prefix = log_file_prefix
        self.use_timestamp = use_timestamp
        self.log_append = log_append

        if not self.logfile_name and not self.logfile_prefix:
            self.active = False

        if self.logfile_name and self.logfile_prefix:
            raise errors.ChannelConfigError("Cannot use both log_file_name and log_file_prefix")

        self.openStatic = True
        if self.logfile_prefix:
            self.openStatic = False

    def start(self, services):
        super(ReportRecorder, self).start(services)
        self._services.logger.debug("Started")
        if self.active and self.openStatic:
            # Try to open file for output
            try:
                if self.log_append.upper() not in ('0','FALSE'):
                    mode = "a"
                else:
                    mode = "w"
                self.logfile = open(os.path.join(self.logdir_name,self.logfile_name), mode)
            except IOError, io_e:
                self._services.logger.error("Could not open '%s' for output"%self.logfile_name)
                self.active = False
                traceback.print_exc()


    def handle(self, message):
        """ Log the call. Data is forwarded after logging. """
        self._services.logger.debug("Received %s message" % message.contentType)
        if not self.active:
            return CallNextHandlerResult()

        if not self.openStatic:
            # Try to open file for output
            utcdate_str = time.strftime("%Y%m%d",time.gmtime(time.time()))
            filename = "%s%s.log" % (self.logfile_prefix, utcdate_str)
            try:
                self.logfile = open(os.path.join(self.logdir_name,filename), 'a')
            except IOError, io_e:
                self._services.logger.error("handle Could not open '%s' for output" % filename)
                self.active = False
                return CallNextHandlerResult()

        self._services.logger.debug("Writing to replay log")
        # Current time
        system_utc_str = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.time()))
        # Write log
        if self.use_timestamp :
            self.logfile.write("\n################ %s #####################\n"%system_utc_str)

        for r in message.content:
            self.logfile.write(r['content'])

        self.logfile.flush()
        if not self.openStatic:
            self.logfile.close()

        return CallNextHandlerResult()

class TimestampSequenceFileWriter(file.TimestampFileWriter):
    """
       A variant of carmensystems.dig.messagehandlers.file.TimestampFileWriter
       It overrides the _getFileName function in order to create timestamped
       filenames without ':' characters which is not supported in for example Windows.
    """
    def __init__(self, path, prefix='dig_', suffix='.msg',
                 name='', encoding='latin-1', seqfile_path='.sequence'):
        super(TimestampSequenceFileWriter, self).__init__(path=path,
            prefix=prefix,
            suffix=suffix,
            name=name,
            encoding=encoding)
        self.seqfile_path = seqfile_path

    def _getFileName(self, idx):
        with open(self.seqfile_path,'r') as seqfile_reader:
            seq_num = int(seqfile_reader.read()) + 1
        with open(self.seqfile_path,'w') as seqfile_writer:
            seqfile_writer.write(str(seq_num))
        idx = idx.replace(':', '')
        return '%s%s-%s%s' % (self._prefix, idx, seq_num, self._suffix)

# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=0:
# eof
