#######################################################
# -*- coding: latin-1 -*-
#
# CarmException
#
# -----------------------------------------------------
#
#  File containing the Carmen specific exception. This
#  exception should be used in the Carmen specific
#  python code.
#
# ------------------------------------------------------
# Created:    2005-02-18
# By:         Björn Samuelsson
#
#######################################################
import sys

class CarmException(Exception):
    """
    This class should be used inside the Carmen python code when raising errors. It can be
    extended to contain more informaton than a regular exception. All handlers that are
    able to handle a standard python exception can also handle a CarmException.
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.wrapped_ex = sys.exc_info()


class PlanningProcessError(IOError):
    """
    Error rasied in the automated planning process
    Indicates that 
    """

class ApplicationError(AttributeError):
    """
    Error raised when the used functionality
    is not available for the current application
    """
