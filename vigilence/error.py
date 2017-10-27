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

class QualityViolationsDetected(VigilenceException):
    """Raised when vigilence detects quality violations.
    """
    def __init__(self, message):
        super(QualityViolationsDetected, self).__init__(message, 1)
