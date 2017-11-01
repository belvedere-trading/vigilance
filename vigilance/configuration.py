"""@ingroup vigilance
@file
Contains functionality for reading Vigilance configurations.
These configurations provide a simple format through which constraints can be applied to coverage reports.
"""
import logging
import re
from abc import ABCMeta, abstractmethod

from vigilance.constraint import PackageConstraint, FileConstraint, IgnoreFiles, ConstraintSet
from vigilance.error import ConfigurationParsingError

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

class BaseStanza(ConfigurationStanza):
    """The global configuration stanza.
    """
    def parse(self, stanza):
        constraints = []
        for label in self.suite.all_labels():
            if label in stanza:
                constraintType = self.suite.get_constraint(label)
                constraints.append(constraintType(stanza[label]))
        return constraints

class FileStanza(BaseStanza):
    """The file filter configuration stanza.
    """
    def parse(self, stanza):
        baseConstraints = super(FileStanza, self).parse(stanza)
        try:
            pathRegex = stanza['path']
        except KeyError:
            raise ConfigurationParsingError('File stanza requires "path" key')
        return [FileConstraint(baseConstraint, re.compile(pathRegex)) for baseConstraint in baseConstraints]

class PackageStanza(BaseStanza):
    """The package filter configuration stanza.
    """
    def parse(self, stanza):
        baseConstraints = super(PackageStanza, self).parse(stanza)
        try:
            name = stanza['name']
        except KeyError:
            raise ConfigurationParsingError('Package stanza requires "name" key')
        return [PackageConstraint(baseConstraint, name) for baseConstraint in baseConstraints]

class IgnoreStanza(ConfigurationStanza):
    """The ignore filter configuration stanza.
    """
    def parse(self, stanza):
        try:
            return [IgnoreFiles(stanza['paths'])]
        except KeyError:
            raise ConfigurationParsingError('Ignore stanza requires "paths" key')

## A sensible default that can be used for general configuration parsing.
DefaultStanzas = {'global': BaseStanza, 'file': FileStanza, 'package': PackageStanza, 'ignore': IgnoreStanza}

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
