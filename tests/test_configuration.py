#pylint: skip-file
import mock
import re

from util import VigilenceTestCase

class BaseStanzaTest(VigilenceTestCase):
    def setUp(self):
        super(BaseStanzaTest, self).setUp()
        from vigilence.constraint import ConstraintSuite
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite, **{'get_constraint.return_value': lambda label: label})
        from vigilence.configuration import BaseStanza
        self.stanza = BaseStanza(self.mockSuite)

    def test_parse_with_no_labels_should_return_no_constraints(self):
        self.mockSuite.all_labels.return_value = []
        self.assertEqual([], self.stanza.parse({}))

    def test_parse_with_labels_should_return_applicable_constraints(self):
        self.mockSuite.all_labels.return_value = ['neat', 'cool', 'bad', 'good']
        self.assertEqual(['neatvalue', 'coolthing', 'goodguy'], self.stanza.parse({'neat': 'neatvalue', 'cool': 'coolthing', 'good': 'goodguy'}))

class FileStanzaTest(VigilenceTestCase):
    def setUp(self):
        super(FileStanzaTest, self).setUp()
        global ConfigurationParsingError, FileConstraint
        from vigilence.error import ConfigurationParsingError
        from vigilence.constraint import ConstraintSuite, FileConstraint
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite)
        from vigilence.configuration import FileStanza
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

class PackageStanzaTest(VigilenceTestCase):
    def setUp(self):
        super(PackageStanzaTest, self).setUp()
        global ConfigurationParsingError, PackageConstraint
        from vigilence.error import ConfigurationParsingError
        from vigilence.constraint import ConstraintSuite, PackageConstraint
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite)
        from vigilence.configuration import PackageStanza
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

class IgnoreStanzaTest(VigilenceTestCase):
    def setUp(self):
        super(IgnoreStanzaTest, self).setUp()
        global ConfigurationParsingError
        from vigilence.error import ConfigurationParsingError
        from vigilence.configuration import IgnoreStanza
        self.stanza = IgnoreStanza(None) # The stanza should not use the suite; using None ensures an error if it does

    def test_parse_without_paths_key_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError):
            self.stanza.parse({})

    def test_parse_should_return_ignore_result(self):
        result, = self.stanza.parse({'paths': ['one', 'three', 'shoe']})
        self.assertEqual(result.paths, ['one', 'three', 'shoe'])


class ConfigurationParserTest(VigilenceTestCase):
    def setUp(self):
        super(ConfigurationParserTest, self).setUp()
        global ConfigurationParsingError
        from vigilence.error import ConfigurationParsingError
        from vigilence.configuration import ConfigurationParser, ConfigurationStanza
        from vigilence.constraint import ConstraintSuite
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite, **{'group_constraints.side_effect': lambda c: c})
        self.globalMock = mock.MagicMock(spec=ConfigurationStanza)
        self.filteredMock = mock.MagicMock(spec=ConfigurationStanza, **{'parse.return_value': ['asdf']})
        self.parser = ConfigurationParser({'nicetype': self.filteredMock, 'global': self.globalMock}, self.mockSuite)

    def test_parse_with_malformed_yaml_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError) as ctx:
            self.parser.parse('"badyaml')
        self.assertEqual('Vigilence configuration could not be parsed as yaml', ctx.exception.message)

    def test_parse_without_constraints_key_should_raise_ConfigurationParsingError(self):
        with self.assertRaises(ConfigurationParsingError) as ctx:
            self.parser.parse('wrong: key')
        self.assertEqual('Vigilence configuration must begin with "constraints" key', ctx.exception.message)

    def test_parse_with_malformed_entry_should_skip_and_log_warning(self):
        constraintSet = self.parser.parse('{"constraints": [{"notypehere": "mydude"}]}')
        self.assertEqual([], constraintSet.globalConstraints)
        self.assertEqual([], constraintSet.filteredConstraints)
        self.log.warning.assert_called_once_with('Skipping malformed constraint stanza; missing "type" key')

    def test_parse_with_unknown_stanza_type_should_skip_and_log_warning(self):
        constraintSet = self.parser.parse('{"constraints": [{"type": "weirdo"}]}')
        self.assertEqual([], constraintSet.globalConstraints)
        self.assertEqual([], constraintSet.filteredConstraints)
        self.log.warning.assert_called_once_with('Skipping malformed constraint stanza; unknown type "%s"', 'weirdo')

    def test_parse_should_parse_stanzas(self):
        constraintSet = self.parser.parse('{"constraints": [{"type": "global"}, {"type": "nicetype"}, {"type": "global"}]}')
        self.assertEqual(self.globalMock.parse.return_value, constraintSet.globalConstraints)
        self.assertEqual(['asdf'], constraintSet.filteredConstraints)
        self.log.warning.assert_called_once_with('Skipping duplicate global configuration stanza')
