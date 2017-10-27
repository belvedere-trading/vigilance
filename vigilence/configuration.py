"""@ingroup vigilence
@file
Contains functionality for reading Vigilence configurations.
These configurations provide a simple format through which constraints can be applied to coverage reports.
"""
import logging
import re
from abc import ABCMeta, abstractmethod

import yaml

from vigilence.constraint import PackageConstraint, FileConstraint, IgnoreFiles, ConstraintSet
from vigilence.error import ConfigurationParsingError

class ConfigurationStanza(object):
    """Represents a single stanza within a vigilence configuration file.
    These stanzas exist to easily allow configuration of vigilence constraints that should be applied to a codebase.
    """
    __metaclass__ = ABCMeta
    def __init__(self, suite):
        self.suite = suite

    @abstractmethod
    def parse(self, stanza):
        """Parses a single configuration stanza into its constituent constraints.
        @param stanza A dictionary (obtained from parsing vigilence configuration YAML).
        @returns A list of vigilence.constraint.Constraint instances.
        @throws vigilence.error.ConfigurationParsingError if the configuration stanza cannot be parsed.
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
    """Parsers vigilence configuration files based upon an arbitrary set of configuration stanzas.
    """
    def __init__(self, stanzas, constraintSuite):
        self.stanzas = stanzas
        self.constraintSuite = constraintSuite

    def parse(self, config):
        """Parses a vigilence configuration file into a constraint set.
        @param config The string contents of a vigilence config file.
        @returns A vigilence.constraint.ConstraintSet instance."""
        try:
            parsed = yaml.load(config)
        except yaml.YAMLError:
            raise ConfigurationParsingError('Vigilence configuration could not be parsed as yaml')
        globalConstraints = []
        otherConstraints = []
        if 'constraints' not in parsed:
            raise ConfigurationParsingError('Vigilence configuration must begin with "constraints" key')
        for entry in parsed['constraints']:
            try:
                entryType = entry['type']
            except KeyError:
                logging.getLogger(__name__).warning('Skipping malformed constraint stanza; missing "type" key')
                continue
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
