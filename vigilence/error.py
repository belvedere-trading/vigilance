"""@ingroup vigilence
Contains Exception definitions.
"""
import click

class VigilenceException(click.ClickException):
    """Base Exception to be raised within vigilence.
    """
    def __init__(self, message, exitCode):
        super(VigilenceException, self).__init__(message)
        self.exit_code = exitCode #pylint: disable=invalid-name

class ReportParsingError(VigilenceException):
    """Raised when a quality report cannot be parsed.
    """
    def __init__(self, message):
        super(ReportParsingError, self).__init__(message, -2)

class ConfigurationParsingError(VigilenceException):
    """Raised when the vigilence configuration file contains errors.
    """
    def __init__(self, message):
        super(ConfigurationParsingError, self).__init__(message, -3)

class UnknownSuite(VigilenceException):
    """Raised when the user attempts to use a quality suite that has not yet been loaded.
    """
    def __init__(self, message):
        super(UnknownSuite, self).__init__(message, -4)

class QualityViolationsDetected(VigilenceException):
    """Raised when vigilence detects quality violations.
    """
    def __init__(self, message):
        super(QualityViolationsDetected, self).__init__(message, 1)
