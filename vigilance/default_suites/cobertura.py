"""@ingroup default_suites
@file
Contains the quality suite definitions necessary for cobertura code coverage enforcement.
"""
import logging
from StringIO import StringIO
from xml.etree import ElementTree

from vigilance.plugin.tooling import DefaultStanzas
from vigilance.constraint import Constraint
from vigilance.error import ReportParsingError
from vigilance.parser import Parser
from vigilance.plugin import AbstractPlugin, SuiteComponents
from vigilance.representation import QualityItem, QualityReport, Satisfaction

class TestMetrics(object):
    """Holds data about a previous code quality run (test run, linting, etc).
    """
    def __init__(self, lineCoverage, branchCoverage, complexity):
        self.lineCoverage = lineCoverage
        self.branchCoverage = branchCoverage
        self.complexity = complexity

class FileUnderTest(QualityItem):
    """Represents a single file from a test coverage report.
    """
    def __init__(self, filePath, lineCoverage=0, branchCoverage=0, complexity=0):
        super(FileUnderTest, self).__init__(TestMetrics(lineCoverage, branchCoverage, complexity))
        self.filePath = filePath

    @property
    def identifier(self):
        return 'file {}'.format(self.filePath)

    def __eq__(self, other):
        return self.filePath == other.filePath

    def __hash__(self):
        return hash(self.filePath)

class PackageUnderTest(QualityItem):
    """Represents a single package from a test coverage report.
    """
    def __init__(self, name, lineCoverage=0, branchCoverage=0, complexity=0):
        super(PackageUnderTest, self).__init__(TestMetrics(lineCoverage, branchCoverage, complexity))
        self.name = name

    @property
    def identifier(self):
        return 'package {}'.format(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class CoberturaParser(Parser):
    """A Parser implementation for Cobertura-compatible coverage reports.
    For details, please see the Cobertura documentation at http://cobertura.github.io/cobertura/.
    """
    def parse(self, fileContents):
        stream = StringIO(fileContents)
        try:
            tree = ElementTree.parse(stream)
        except ElementTree.ParseError:
            logging.getLogger(__name__).exception('Parsing failed')
            raise ReportParsingError('Unable to parse Cobertura report as XML')
        classes = [self._xml_class_to_file(cls) for cls in tree.findall('.//class')]
        packages = [self._xml_package_to_package(pkg) for pkg in tree.findall('.//package')]
        return QualityReport(classes + packages)

    @staticmethod
    def _get_attribute(xml, attr, default=0):
        try:
            return float(xml.attrib[attr]) * 100
        except (KeyError, ValueError):
            logging.getLogger(__name__).warn('Failed to find attribute in XML element: %s', attr)
            return default

    @classmethod
    def _xml_class_to_file(cls, xml):
        lineCoverage = cls._get_attribute(xml, 'line-rate')
        branchCoverage = cls._get_attribute(xml, 'branch-rate')
        complexity = cls._get_attribute(xml, 'complexity')
        try:
            filePath = xml.attrib['filename']
        except KeyError:
            filePath = 'Parse failed; unknown'
        return FileUnderTest(filePath, lineCoverage, branchCoverage, complexity)

    @classmethod
    def _xml_package_to_package(cls, xml):
        lineCoverage = cls._get_attribute(xml, 'line-rate')
        branchCoverage = cls._get_attribute(xml, 'branch-rate')
        complexity = cls._get_attribute(xml, 'complexity')
        try:
            name = xml.attrib['name']
        except KeyError:
            name = 'Parse failed; unknown'
        return PackageUnderTest(name, lineCoverage, branchCoverage, complexity)

class LineCoverage(Constraint):
    """A Constraint that enforces a line coverage minimum.
    """
    def __init__(self, minimumCoverage):
        self.minimumCoverage = minimumCoverage

    def satisfied_by(self, item):
        actual = item.metrics.lineCoverage
        if actual < self.minimumCoverage:
            return Satisfaction(False, 'Line coverage too low for {} ({}/{})'.format(item.identifier, actual, self.minimumCoverage))
        return Satisfaction(True)

class BranchCoverage(Constraint):
    """A Constraint that enforces a branch coverage minimum.
    """
    def __init__(self, minimumCoverage):
        self.minimumCoverage = minimumCoverage

    def satisfied_by(self, item):
        actual = item.metrics.branchCoverage
        if actual < self.minimumCoverage:
            return Satisfaction(False, 'Branch coverage too low for {} ({}/{})'.format(item.identifier, actual, self.minimumCoverage))
        return Satisfaction(True)

class Complexity(Constraint):
    """A Constraint that enforces a maximum complexity.
    """
    def __init__(self, maximumComplexity):
        self.maximumComplexity = maximumComplexity

    def satisfied_by(self, item):
        actual = item.metrics.complexity
        if actual > self.maximumComplexity:
            return Satisfaction(False, 'Complexity too high for {} ({}/{})'.format(item.identifier, actual, self.maximumComplexity))
        return Satisfaction(True)

class Default(AbstractPlugin):
    """The AbstractPlugin implementation for coverage.
    """
    def get_suite_components(self):
        return SuiteComponents('cobertura',
                               CoberturaParser(),
                               {'line': LineCoverage, 'branch': BranchCoverage, 'complexity': Complexity},
                               DefaultStanzas)
