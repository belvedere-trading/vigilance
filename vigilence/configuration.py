"""@ingroup vigilence
@file
Contains functionality for reading Vigilence configurations.
These configurations provide a simple format through which constraints can be applied to coverage reports.
"""
import re
from abc import ABCMeta, abstractmethod
from logging import getLogger

import yaml

from vigilence.constraint import PackageConstraint, FileConstraint, IgnoreFiles, ConstraintSet

Log = getLogger(__name__)

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
        pathRegex = stanza['path']
        return [FileConstraint(baseConstraint, re.compile(pathRegex)) for baseConstraint in baseConstraints]

class PackageStanza(BaseStanza):
    """The package filter configuration stanza.
    """
    def parse(self, stanza):
        baseConstraints = super(PackageStanza, self).parse(stanza)
        name = stanza['name']
        return [PackageConstraint(baseConstraint, name) for baseConstraint in baseConstraints]

class IgnoreStanza(ConfigurationStanza):
    """The ignore filter configuration stanza.
    """
    def parse(self, stanza):
        return [IgnoreFiles(stanza['paths'])]

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
        parsed = yaml.load(config)
        globalConstraints = []
        otherConstraints = []
        for entry in parsed['constraints']:
            stanza = self.stanzas[entry['type']]
            constraints = stanza.parse(entry)
            if entry['type'] == 'global':
                if globalConstraints:
                    Log.warning('Skipping duplicate global configuration stanza')
                    continue
                else:
                    globalConstraints = constraints
            else:
                otherConstraints.extend(constraints)
        return ConstraintSet(self.constraintSuite, globalConstraints, otherConstraints)
