"""
This file contains handlers for the following integration interfaces:
* X1/X2 - Replicate Perkey and Name.
* X3    - Vacation Trade Snapshot
* Noncore Statistics
"""

# imports ================================================================{{{1
import os
import commands
from carmensystems.dig.framework import errors
from carmensystems.dig.framework.utils import convertToBoolean
from carmensystems.dig.framework.handler import MessageHandlerBase, CallNextHandlerResult, TextContentType, BinaryContentType
from carmensystems.dig.messagehandlers.reports import ReportsContentType
import utils.datadump


# classes ================================================================{{{1
# MiradorHandler ---------------------------------------------------------{{{2
class MiradorHandler(MessageHandlerBase):
    """
    Calls external Mirador script for handling incoming and outgoing
    replication messages. For outgoing (publish) interfaces X1/X2
    and X3, the Mirador script will produce a report file in exportDir.

    Options:

        interface       -   Valid values: 'X1'|'X2'|'X3'

        exportFilename  -   Name of exported report file. 
                            Applies to all interfaces except TI1.

        exportDir       -   Path where report file is stored. 
                            Applies to all interfaces except TI1.
                            Default: $CARMTMP/ftp/out

    """
    def __init__(self, interface, exportFilename=None, exportDir=None, name=None):
        super(MiradorHandler,self).__init__(name)
        if interface:
            self.__interface = interface.upper()
            if self.__interface == 'X1' or self.__interface == 'X2':
                self.__script = "X12.py"
            elif self.__interface == 'X3':
                self.__script = "X3.py"
            else:
                raise errors.ChannelConfigError("Interface '%s' not supported." % interface)
        else:
            raise errors.ChannelConfigError("Parameter 'interface' must be specified.")

        self.__filename = exportFilename
        if not self.__filename:
            raise errors.ChannelConfigError("Parameter 'exportFilename' must be specified for publish interfaces.")

        self.__exportDir = exportDir
        if not exportDir:
            self.__exportDir = os.path.join(os.path.expandvars("$CARMTMP"),"ftp/out")
        if not os.path.exists(self.__exportDir):
            os.makedirs(self.__exportDir, 0775)
        self.__exportPath = os.path.join(self.__exportDir, self.__filename)


    def handle(self, message):
        self._services.logger.info("Handling interface %s..." % self.__interface)

        # Assemble command to start Mirador script
        db = self._services.getDaveConnector()
        cmd = os.path.join(os.path.expandvars("$CARMSYS"),
                "bin/carmrunner replication/%s -c %s -s %s" % 
                (self.__script,
                 db._DaveConnector__connectionString,
                 db._DaveConnector__schema))
        cmd = "%s -o %s" % (cmd, self.__exportPath)

        self._services.logger.debug("Starting process: %s" % (cmd))
        (status, output) = commands.getstatusoutput(cmd)
        self._services.logger.info(output)
        if status != 0:
            raise errors.MessageError("Command failed (status %d): %s" % (status,cmd))

        # Get report
        try:
            f = open(self.__exportPath)
            report = f.read()
            f.close()
        except:
            raise errors.MessageError("Failed reading report file '%s'" % self.__exportPath)
        message.setContent(report, TextContentType(encoding='iso-8859-1'))

        return CallNextHandlerResult()


# StatisticsHandler ------------------------------------------------------{{{2
class StatisticsHandler(MessageHandlerBase):
    """
    Calls external datadump program for creating statistics files.

    Options:

        directory   - Path where to store statistics files. 

        incremental - Get only changes since last run. Default "True"

        use_bt_dt   - Create XSD for entity block_time_duty_time. Default "True".

    """
    def __init__(self, directory, incremental="True", use_bt_dt="True", name=None):
        super(StatisticsHandler, self).__init__(name)
        self.__directory = directory
        self.__incremental = convertToBoolean(incremental)
        self.__use_bt_dt = convertToBoolean(use_bt_dt)


    def handle(self, message):
        self._services.logger.info("Started...")
        db = self._services.getDaveConnector()
        try:
            utils.datadump.run( schema=db._DaveConnector__schema,
                                connect=db._DaveConnector__connectionString,
                                dir=self.__directory,
                                incremental=self.__incremental,
                                use_bt_dt=self.__use_bt_dt)
        except Exception, e:
            raise errors.MessageError("Statistics datadump failed: %s" % str(e))
        self._services.logger.info("Finished")

        return CallNextHandlerResult()

# format ================================================================={{{1
# spec -------------------------------------------------------------------{{{2
#------------------------------------------------------------------------

# sample ------------------------------------------------------------------{{{2
#         1         2         3         4         5         
# 1234567890123456789012345678901234567890123456789012345687
# ----------------------------------------------------------
#
