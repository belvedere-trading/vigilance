#pylint: skip-file
import mock
import re

from util import VigilanceTestCase

class BaseStanzaTest(VigilanceTestCase):
    def setUp(self):
        super(BaseStanzaTest, self).setUp()
        from vigilance.constraint import ConstraintSuite
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite, **{'get_constraint.return_value': lambda label: label})
        from vigilance.plugin.tooling import BaseStanza
        self.stanza = BaseStanza(self.mockSuite)

    def test_parse_with_no_labels_should_return_no_constraints(self):
        self.mockSuite.all_labels.return_value = []
        self.assertEqual([], self.stanza.parse({}))

    def test_parse_with_labels_should_return_applicable_constraints(self):
        self.mockSuite.all_labels.return_value = ['neat', 'cool', 'bad', 'good']
        self.assertEqual(['neatvalue', 'coolthing', 'goodguy'], self.stanza.parse({'neat': 'neatvalue', 'cool': 'coolthing', 'good': 'goodguy'}))

class FileStanzaTest(VigilanceTestCase):
    def setUp(self):
        super(FileStanzaTest, self).setUp()
        global ConfigurationParsingError, FileConstraint
        from vigilance.error import ConfigurationParsingError
        from vigilance.constraint import ConstraintSuite, FileConstraint
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite)
        from vigilance.plugin.tooling import FileStanza
        self.stanza = FileStanza(self.mockSuite)

    def test_parse_without_path_key_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError):
            self.stanza.parse({})

    def test_parse_with_no_labels_should_return_no_constraints(self):
        self.mockSuite.all_labels.return_value = []
        self.assertEqual([], self.stanza.parse({'path': 'path'}))

    @mock.patch.object(re, 'compile')
    def test_parse_with_labels_should_return_constraints(self, reCompile):
        reCompile.side_effect = lambda reg: reg
        self.mockSuite.all_labels.return_value = ['working', 'not']
        result, = self.stanza.parse({'working': 'thing', 'path': 'regex'})
        self.assertTrue(isinstance(result, FileConstraint))
        self.assertEqual('regex', result.pathRegex)

class PackageStanzaTest(VigilanceTestCase):
    def setUp(self):
        super(PackageStanzaTest, self).setUp()
        global ConfigurationParsingError, PackageConstraint
        from vigilance.error import ConfigurationParsingError
        from vigilance.constraint import ConstraintSuite, PackageConstraint
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite)
        from vigilance.plugin.tooling import PackageStanza
        self.stanza = PackageStanza(self.mockSuite)

    def test_parse_without_name_key_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError):
            self.stanza.parse({})

    def test_parse_with_no_labels_should_return_no_constraints(self):
        self.mockSuite.all_labels.return_value = []
        self.assertEqual([], self.stanza.parse({'name': 'nicePackage'}))

    def test_parse_with_labels_should_return_constraints(self):
        self.mockSuite.all_labels.return_value = ['working', 'not']
        result, = self.stanza.parse({'working': 'thing', 'name': 'niceman'})
        self.assertTrue(isinstance(result, PackageConstraint))
        self.assertEqual('niceman', result.packageName)

class IgnoreStanzaTest(VigilanceTestCase):
    def setUp(self):
        super(IgnoreStanzaTest, self).setUp()
        global ConfigurationParsingError
        from vigilance.error import ConfigurationParsingError
        from vigilance.plugin.tooling import IgnoreStanza
        self.stanza = IgnoreStanza(None) # The stanza should not use the suite; using None ensures an error if it does

    def test_parse_without_paths_key_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError):
            self.stanza.parse({})

    def test_parse_should_return_ignore_result(self):
        result, = self.stanza.parse({'paths': ['one', 'three', 'shoe']})
        self.assertEqual(result.paths, ['one', 'three', 'shoe'])
