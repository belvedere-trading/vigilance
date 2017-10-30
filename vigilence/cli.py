"""@ingroup vigilence
@file
Contains the console API for Vigilence.
"""
import click
import yaml
from voluptuous import Schema, Required, ALLOW_EXTRA
from voluptuous.error import Invalid

from vigilence.error import ConfigurationParsingError, UnknownSuite, ReportParsingError
from vigilence.plugin import get_configured_plugins, load_suites
from vigilence.suite import QualitySuite

load_suites(get_configured_plugins())

ConfigurationSchema = Schema({Required('suites'): {str:
                                                   Schema({Required('report'): str,
                                                           Required('constraints'):
                                                           Schema([Schema({Required('type'): str}, extra=ALLOW_EXTRA)])})}})

@click.command(short_help='Verify code coverage metrics against a set of constraints')
@click.option('--config', 'configFile', type=click.File(), default='vigilence.yaml', help='Path to the vigilence configuration file')
def main(configFile): #pylint: disable=missing-docstring, invalid-name
    """Runs Vigilence with the specified configuration file.
    The default configuration file if no options are passed is vigilence.yaml within the current working directory.
    """
    try:
        suites = ConfigurationSchema(yaml.load(configFile))['suites']
    except yaml.YAMLError:
        raise ConfigurationParsingError('Could not load configuration file as yaml')
    except Invalid as ex:
        raise ConfigurationParsingError('Invalid configuration schema: {}'.format(ex.message))
    unknownSuites = [suite for suite in suites.iterkeys() if suite not in QualitySuite.available_suites()]
    if unknownSuites:
        raise UnknownSuite('Suites were configured but not available: ' + ', '.join(unknownSuites))
    for suiteType, suiteConfig in suites.iteritems():
        suite = QualitySuite.get_suite(suiteType)
        try:
            with open(suiteConfig['report'], 'r') as qualityReport:
                suite.run(suiteConfig['constraints'], qualityReport.read())
        except IOError:
            raise ReportParsingError('Could not open report "{}" for reading'.format(suite['report']))
