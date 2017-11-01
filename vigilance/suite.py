"""@ingroup vigilance
@file
Contains glue that relates all vigilance concepts together into "quality suites".
These suites can be added by users as plugins and selected via the command line.
"""
from vigilance.configuration import ConfigurationParser
from vigilance.constraint import ConstraintSuite
from vigilance.error import QualityViolationsDetected

class QualitySuite(object):
    """Represents a full set of quality metrics that should be enforced upon a codebase.
    The QualitySuite consists of a combination of the lower-level vigilance concepts:
    1. Metrics: the raw data points that comprise the quality check
    2. Quality items: the individual unit for which metrics are collected (e.g. files, modules, classes, functions, etc.)
    3. Parsers: the translators that turn raw metrics into vigilance-compatible quality items.
    4. Constraints: the requirements for the metrics collected for the various quality items in the codebase.
    5. Configuration stanzas: the configurations necessary for a user to model all of the above in a simple configuration file.
    """
    Suites = {}
    def __init__(self, suiteType, parser, constraints, configurations):
        self.suiteType = suiteType
        self.reportParser = parser
        self.constraints = ConstraintSuite(constraints)
        stanzas = {key: config(self.constraints) for key, config in configurations.iteritems()}
        self.configurationParser = ConfigurationParser(stanzas, self.constraints)

    def run(self, constraints, report):
        """Runs the quality suite with the provided configuration on the provided quality report.
        @param constraints A dictionary containing the configured constraints for the suite.
        @param report The string contents of the quality report.
        @throws vigilance.error.QualityViolationsDetected
        """
        constraints = self.configurationParser.parse(constraints)
        quality = self.reportParser.parse(report)
        dissatisfactions = quality.scrutinize(constraints)
        for failure in dissatisfactions:
            print failure.message
        if dissatisfactions:
            raise QualityViolationsDetected('One or more quality violations detected')
        print 'Quality validation complete for {}'.format(self.suiteType)

    @classmethod
    def add_suite(cls, key, parser, constraints, configurations):
        """Adds a quality suite to the vigilance registry.
        This suite will be available via the vigilance command line utility.
        @param cls
        @param key The string identifier that should be used to access the quality suite.
        @param parser A vigilance.parser.Parser instance.
        @param constraints A dictionary mapping constraint labels to their corresponding class objects.
        @param configurations A dictionary mapping configuration keys to the corresponding class objects.
        @throws ValueError if @p key is already in use.
        @see vigilance.configuration.ConfigurationStanza
        @see vigilance.constraint.Constraint
        """
        if key in cls.Suites:
            raise ValueError('Quality suite "{}" already exists'.format(key))
        cls.Suites[key] = QualitySuite(key, parser, constraints, configurations)

    @classmethod
    def available_suites(cls):
        """Returns a list of all available quality suite names.
        """
        return cls.Suites.keys()

    @classmethod
    def get_suite(cls, key):
        """Returns the QualitySuite associated with @p key.
        """
        return cls.Suites[key]
