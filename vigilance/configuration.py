"""@ingroup vigilance
@file
Contains functionality for reading Vigilance configurations.
These configurations provide a simple format through which constraints can be applied to coverage reports.
"""
import logging
from abc import ABCMeta, abstractmethod

from vigilance.constraint import ConstraintSet

class ConfigurationStanza(object):
    """Represents a single stanza within a vigilance configuration file.
    These stanzas exist to easily allow configuration of vigilance constraints that should be applied to a codebase.
    """
    __metaclass__ = ABCMeta
    def __init__(self, suite):
        self.suite = suite

    @abstractmethod
    def parse(self, stanza):
        """Parses a single configuration stanza into its constituent constraints.
        @param stanza A dictionary (obtained from parsing vigilance configuration YAML).
        @returns A list of vigilance.constraint.Constraint instances.
        @throws vigilance.error.ConfigurationParsingError if the configuration stanza cannot be parsed.
        """
        pass

class ConfigurationParser(object):
    """Parsers vigilance configuration files based upon an arbitrary set of configuration stanzas.
    """
    def __init__(self, stanzas, constraintSuite):
        self.stanzas = stanzas
        self.constraintSuite = constraintSuite

    def parse(self, constraints):
        """Parses a vigilance configuration file into a constraint set.
        @param constraints A dictionary containing constraint configurations.
        @returns A vigilance.constraint.ConstraintSet instance."""
        globalConstraints = []
        otherConstraints = []
        for entry in constraints:
            entryType = entry['type']
            try:
                stanza = self.stanzas[entryType]
            except KeyError:
                logging.getLogger(__name__).warning('Skipping malformed constraint stanza; unknown type "%s"', entryType)
                continue
            constraints = stanza.parse(entry)
            if entryType == 'global':
                if globalConstraints:
                    logging.getLogger(__name__).warning('Skipping duplicate global configuration stanza')
                    continue
                else:
                    globalConstraints = constraints
            else:
                otherConstraints.extend(constraints)
        return ConstraintSet(self.constraintSuite, globalConstraints, otherConstraints)
