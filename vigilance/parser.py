"""@ingroup vigilance
@file
Contains functionality for reading coverage output and parsing it into the Vigilance internal representation.
"""
from abc import ABCMeta, abstractmethod
import six

@six.add_metaclass(ABCMeta)
class Parser(object):
    """Abstract interface for parsing test coverage output.
    The primary reponsibiliy of a Parser subclass is to convert output files into the Vigilance internal representation.
    """
    @abstractmethod
    def parse(self, fileContents):
        """Parses coverage output.
        @param fileContents The string contents of the coverage output file.
        @returns A vigilance.representation.QualityReport instance.
        @throws vigilance.error.ReportParsingError if an unrecoverable error is encountered during parsing.
        """
        pass
