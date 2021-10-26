#pylint: skip-file
import mock
from nose_parameterized import parameterized
from StringIO import StringIO

from util import VigilanceTestCase, mock_decorator

@mock.patch('yaml.full_load')
@mock.patch('vigilance.cli.open', create=True)
class CliTest(VigilanceTestCase):
    @property
    def modulesToPatch(self):
        self.suite = mock.MagicMock()
        return {'click': mock.MagicMock(ClickException=Exception,
            command=mock_decorator,
            option=mock_decorator),
        'vigilance.suite': self.suite,
        'vigilance.plugin': mock.MagicMock()}

    def setUp(self):
        super(CliTest, self).setUp()
        global ConfigurationParsingError, UnknownSuite, ReportParsingError, YAMLError, Invalid, main
        from vigilance.error import ConfigurationParsingError, UnknownSuite, ReportParsingError
        from voluptuous.error import Invalid
        from yaml import YAMLError
        from vigilance.cli import main

    def test_main_raises_ConfigurationParsingError_on_load_YAMLError(self, mockOpen, mockYamlLoad):
        mockYamlLoad.side_effect = YAMLError('boom')
        with self.assertRaises(ConfigurationParsingError):
            main('file')

    def test_main_raises_ConfigurationParsingError_on_load_Invalid(self, mockOpen, mockYamlLoad):
        mockYamlLoad.side_effect = Invalid('boom')
        with self.assertRaises(ConfigurationParsingError):
            main('file')

    def test_main_raises_UnknownSuite_when_not_in_availble_suites(self, mockOpen, mockYamlLoad):
        mockYamlLoad.return_value = {'suites': {'test': {'report': 'test.txt', 'constraints': [{'type': 'bob'}]}}}
        self.suite.available_suites.return_value = ['otherNonTest']
        with self.assertRaises(UnknownSuite):
            main('file')

    def test_main_raises_ReportParsingError_on_IOError(self, mockOpen, mockYamlLoad):
        mockYamlLoad.return_value = {'suites': {'test': {'report': 'test.txt', 'constraints': [{'type': 'bob'}]}}}
        self.suite.QualitySuite.available_suites.return_value = ['test']
        self.suite.QualitySuite.get_suite.return_value = {}
        mockOpen.side_effect = IOError('boom')
        with self.assertRaises(ReportParsingError):
            main('file')

    def test_main_suite_runs_for_1_suite(self, mockOpen, mockYamlLoad):
        mockYamlLoad.return_value = {'suites': {'test': {'report': 'test.txt', 'constraints': [{'type': 'bob'}]}}}
        self.suite.QualitySuite.available_suites.return_value = ['test']
        mockOpen.return_value.__enter__.return_value = StringIO('reportTxt')
        main('file')
        self.suite.QualitySuite.get_suite.return_value.run.assert_called_once_with([{'type': 'bob'}], 'reportTxt')

    def test_main_suite_runs_for_multiple_suite(self, mockOpen, mockYamlLoad):
        mockYamlLoad.return_value = {'suites': 
                {'test': {'report': 'test.txt', 'constraints': [{'type': 'bob'}]},
                 'otherTest': {'report': 'yay.txt', 'constraints': [{'type': 'other'}]},
                 'lastTest': {'report': 'last.txt', 'constraints': [{'type': 'last'}]}}}
        self.suite.QualitySuite.available_suites.return_value = ['test', 'otherTest', 'lastTest']
        mockOpen.return_value.__enter__.side_effect = [StringIO('testTxt'), StringIO('lastTxt'), StringIO('otherTxt')]
        main('file')
        self.suite.QualitySuite.get_suite.return_value.run.assert_has_calls([
            mock.call([{'type': 'bob'}], 'testTxt'),
            mock.call([{'type': 'last'}], 'lastTxt'),
            mock.call([{'type': 'other'}], 'otherTxt'),
        ])
