"""@ingroup plugin
@file
Contains tooling to facilitate the authoring of Vigilance plugins.
"""
import re

from vigilance.configuration import ConfigurationStanza
from vigilance.constraint import FileConstraint, PackageConstraint, IgnoreFiles
from vigilance.error import ConfigurationParsingError

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
