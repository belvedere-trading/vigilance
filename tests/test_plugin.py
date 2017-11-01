#pylint: skip-file
import importlib
import os
import mock
from StringIO import StringIO

from util import VigilanceTestCase

class LoadSuitesTest(VigilanceTestCase):
    def setUp(self):
        super(LoadSuitesTest, self).setUp()
        global load_suites, QualitySuite
        from vigilance.suite import QualitySuite
        from vigilance.plugin import load_suites

    def test_load_suites_with_malformed_plugin_should_log_warning(self):
        load_suites(['nocolonhere'], disableDefaults=True)
        self.log.warning.assert_called_once_with('Skipping malformed plugin specifier "%s"', 'nocolonhere')

    @mock.patch.object(importlib, 'import_module')
    def test_load_suites_with_missing_plugin_module_should_log_warning(self, mockImport):
        mockImport.side_effect = ImportError('that is really not there')
        load_suites(['this.one:isright'], disableDefaults=True)
        self.log.warning.assert_called_once_with('Skipping missing plugin module "%s"', 'this.one')

    @mock.patch.object(importlib, 'import_module')
    def test_load_suites_with_missing_plugin_implementation_should_log_warning(self, mockImport):
        mockImport.return_value.goodguy = mock.PropertyMock(side_effect=AttributeError('this is just a mirage'))
        load_suites(['so.close.to:goodguy'], disableDefaults=True)
        self.log.warning.assert_called_once_with('Skipping missing plugin implementation "%s" within plugin "%s"', 'goodguy', 'so.close.to')

    def test_load_suites_should_load_default_suites(self):
        load_suites([])
        self.assertEqual(2, len(QualitySuite.available_suites()))

@mock.patch('vigilance.plugin.open', create=True)
@mock.patch.object(os, 'path')
class GetConfiguredPluginsTest(VigilanceTestCase):
    def setUp(self):
        super(GetConfiguredPluginsTest, self).setUp()
        global get_configured_plugins
        from vigilance.plugin import get_configured_plugins

    def test_get_configured_plugins_with_malformed_dotfile_should_log_warning(self, mockPath, mockOpen):
        mockPath.isfile.side_effect = lambda p: p == '.vigilance'
        mockOpen.return_value.__enter__.return_value = StringIO('{uh oh not ini}')
        self.assertEqual([], get_configured_plugins())
        self.log.warning.assert_called_once_with('Skipping malformed configuration file "%s"', '.vigilance')

    def test_get_configured_plugins_with_malformed_setupcfg_should_log_warning(self, mockPath, mockOpen):
        mockPath.isfile.side_effect = lambda p: p == 'setup.cfg'
        mockOpen.return_value.__enter__.return_value = StringIO('{uh oh not ini}')
        self.assertEqual([], get_configured_plugins())
        self.log.warning.assert_called_once_with('Skipping malformed configuration file "%s"', 'setup.cfg')

    def test_get_configured_plugins_with_no_plugins_should_return_empty_list(self, mockPath, _):
        mockPath.isfile.return_value = False
        self.assertEqual([], get_configured_plugins())
        self.log.warning.assert_not_called()

    def test_get_configured_plugins_with_environment_variable_set_should_return_plugins(self, mockPath, _):
        mockPath.isfile.return_value = False
        with mock.patch.dict(os.environ, {'VIGILANCE_PLUGINS': 'firstone:cool,another:one'}, clear=True):
            self.assertEqual(['firstone:cool', 'another:one'], get_configured_plugins())

    def test_get_configured_plugins_with_setupcfg_set_should_return_plugins(self, mockPath, mockOpen):
        mockPath.isfile.side_effect = lambda p: p == 'setup.cfg'
        mockOpen.return_value.__enter__.return_value = StringIO('[vigilance]\n'
                                                                'plugins = one,andtwo')
        self.assertEqual(['one', 'andtwo'], get_configured_plugins())

    def test_get_configured_plugins_with_dotfile_set_should_return_plugins(self, mockPath, mockOpen):
        mockPath.isfile.side_effect = lambda p: p == '.vigilance'
        mockOpen.return_value.__enter__.return_value = StringIO('[vigilance]\n'
                                                                'plugins = justone')
        self.assertEqual(['justone'], get_configured_plugins())
