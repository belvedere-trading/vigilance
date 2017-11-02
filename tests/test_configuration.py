#pylint: skip-file
import mock
import re

from util import VigilanceTestCase

class ConfigurationParserTest(VigilanceTestCase):
    def setUp(self):
        super(ConfigurationParserTest, self).setUp()
        global ConfigurationParsingError
        from vigilance.error import ConfigurationParsingError
        from vigilance.configuration import ConfigurationParser, ConfigurationStanza
        from vigilance.constraint import ConstraintSuite
        self.mockSuite = mock.MagicMock(spec=ConstraintSuite, **{'group_constraints.side_effect': lambda c: c})
        self.globalMock = mock.MagicMock(spec=ConfigurationStanza)
        self.filteredMock = mock.MagicMock(spec=ConfigurationStanza, **{'parse.return_value': ['asdf']})
        self.parser = ConfigurationParser({'nicetype': self.filteredMock, 'global': self.globalMock}, self.mockSuite)

    def test_parse_with_unknown_stanza_type_should_skip_and_log_warning(self):
        constraintSet = self.parser.parse([{"type": "weirdo"}])
        self.assertEqual([], constraintSet.globalConstraints)
        self.assertEqual([], constraintSet.filteredConstraints)
        self.log.warning.assert_called_once_with('Skipping malformed constraint stanza; unknown type "%s"', 'weirdo')

    def test_parse_should_parse_stanzas(self):
        constraintSet = self.parser.parse([{"type": "global"}, {"type": "nicetype"}, {"type": "global"}])
        self.assertEqual(self.globalMock.parse.return_value, constraintSet.globalConstraints)
        self.assertEqual(['asdf'], constraintSet.filteredConstraints)
        self.log.warning.assert_called_once_with('Skipping duplicate global configuration stanza')
