"""@defgroup plugin plugin
@file
Contains functionality for writing Vigilance plugins.
"""
import importlib
import logging
import os
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from ConfigParser import ConfigParser, Error

from vigilance.suite import QualitySuite

## The components necessary to construct a vigilance.suite.QualitySuite instance.
# key is the unique name of the quality suite; only one plugin for each key can be loaded by a single running instance of Vigilance.<br/>
# parser is an object instance that should be a subclass of vigilance.parser.Parser. Used to parse the quality report.<br/>
# constraints is a dictionary mapping constraint labels to their associated class objects
# (subclasses of vigilance.constraint.Constraint).<br/>
# configurations is a dictionary mapping configuration stanza labels to their
# associated stanza objects (subclasses of vigilance.configuration.ConfigurationStanza).
SuiteComponents = namedtuple('SuiteComponents', ['key', 'parser', 'constraints', 'configurations'])

class AbstractPlugin(object):
    """The external entrypoint for Vigilance plugins.
    """
    __metaclass__ = ABCMeta
    @abstractmethod
    def get_suite_components(self):
        """Returns the components necessary for the registration of a new vigilance.suite.QualitySuite.
        @returns A SuiteComponents instance.
        """
        pass

## The default suites that should be available to the Vigilance tool.
DefaultSuites = ['vigilance.default_suites.cobertura:Default',
                 'vigilance.default_suites.doxygen:Default']

def _read_config_file(filename, parser):
    try:
        if os.path.isfile(filename):
            with open(filename, 'r') as vFile:
                parser.readfp(vFile)
    except (IOError, Error):
        logging.getLogger(__name__).warning('Skipping malformed configuration file "%s"', filename)

def get_configured_plugins():
    """Retrieves a list of all plugins that the user has configured for availability within Vigilance.
    This list will prefer configurations from three sources in this order:
    1. The VIGILANCE_PLUGINS environment variable.
    2. A .vigilance file within the current working directory.
    3. A setup.cfg file within the current working directory.
    @returns A list of plugin specifier strings.
    @see load_suites
    """
    plugins = []
    parser = ConfigParser()
    parser.add_section('vigilance')
    _read_config_file('setup.cfg', parser)
    _read_config_file('.vigilance', parser)
    vEnv = os.getenv('VIGILANCE_PLUGINS', None)
    if vEnv:
        parser.set('vigilance', 'plugins', vEnv)
    if parser.has_option('vigilance', 'plugins'):
        plugins = parser.get('vigilance', 'plugins').split(',')
    return plugins

def load_suites(plugins, disableDefaults=False):
    """Loads all quality suites that should be made available to the Vigilance tool.
    @param plugins A list of strings specifying the plugins that should be loaded (e.g. 'vigilance.default_suites.doxygen:Default').
    @param disableDefaults Whether the default suites should be disabled from the suite load.
    """
    toLoad = plugins
    if not disableDefaults:
        toLoad += DefaultSuites
    for pluginSpecifier in toLoad:
        try:
            moduleName, cls = pluginSpecifier.split(':')
        except ValueError:
            logging.getLogger(__name__).warning('Skipping malformed plugin specifier "%s"', pluginSpecifier)
            continue
        try:
            module = importlib.import_module(moduleName)
        except ImportError:
            logging.getLogger(__name__).warning('Skipping missing plugin module "%s"', moduleName)
            continue
        try:
            plugin = getattr(module, cls)()
        except AttributeError:
            logging.getLogger(__name__).warning('Skipping missing plugin implementation "%s" within plugin "%s"', cls, moduleName)
            continue
        QualitySuite.add_suite(*plugin.get_suite_components())
