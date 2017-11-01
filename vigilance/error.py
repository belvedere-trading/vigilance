"""@ingroup vigilance
Contains Exception definitions.
"""
import click

class VigilanceException(click.ClickException):
    """Base Exception to be raised within vigilance.
    """
    def __init__(self, message, exitCode):
        super(VigilanceException, self).__init__(message)
        self.exit_code = exitCode #pylint: disable=invalid-name

class ReportParsingError(VigilanceException):
    """Raised when a quality report cannot be parsed.
    """
    def __init__(self, message):
        super(ReportParsingError, self).__init__(message, -2)

class ConfigurationParsingError(VigilanceException):
    """Raised when the vigilance configuration file contains errors.
    """
    def __init__(self, message):
        super(ConfigurationParsingError, self).__init__(message, -3)

class UnknownSuite(VigilanceException):
    """Raised when the user attempts to use a quality suite that has not yet been loaded.
    """
    def __init__(self, message):
        super(UnknownSuite, self).__init__(message, -4)

class QualityViolationsDetected(VigilanceException):
    """Raised when vigilance detects quality violations.
    """
    def __init__(self, message):
        super(QualityViolationsDetected, self).__init__(message, 1)
