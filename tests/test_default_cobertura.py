#pylint: skip-file
import mock
from nose_parameterized import parameterized

from util import VigilenceTestCase

class FileUnderTestTest(VigilenceTestCase):
    def setUp(self):
        super(FileUnderTestTest, self).setUp()
        from vigilence.default_suites.cobertura import FileUnderTest
        self.item = FileUnderTest('/my/file')

    def test_identifier_should_return_human_readable_representation(self):
        self.assertEqual('file /my/file', self.item.identifier)

class PackageUnderTestTest(VigilenceTestCase):
    def setUp(self):
        super(PackageUnderTestTest, self).setUp()
        from vigilence.default_suites.cobertura import PackageUnderTest
        self.item = PackageUnderTest('package_name')

    def test_identifier_should_return_human_readable_representation(self):
        self.assertEqual('package package_name', self.item.identifier)

class CoberturaParserTest(VigilenceTestCase):
    def setUp(self):
        super(CoberturaParserTest, self).setUp()
        global ReportParsingError, FileUnderTest, PackageUnderTest
        from vigilence.error import ReportParsingError
        from vigilence.default_suites.cobertura import CoberturaParser, FileUnderTest, PackageUnderTest
        self.parser = CoberturaParser()

    def test_parse_with_invalid_xml_should_raise_ReportParsingError(self):
        with self.assertRaises(ReportParsingError):
            self.parser.parse('<xml? not really')

    def test_parse_with_no_elements_should_return_no_items(self):
        report = self.parser.parse('<report></report>')
        self.assertEqual([], report.items)

    def test_parse_should_return_items(self):
        reportText = ('<report>\n'
                      '<class filename="asdf" line-rate="15"></class>\n'
                      '<package name="packman" line-rate="15"></package>\n'
                      '</report>')
        report = self.parser.parse(reportText)
        self.assertEqual([FileUnderTest('asdf'), PackageUnderTest('packman')], report.items)

class LineCoverageTest(VigilenceTestCase):
    def setUp(self):
        super(LineCoverageTest, self).setUp()
        from vigilence.default_suites.cobertura import LineCoverage
        self.constraint = LineCoverage(22)

    @parameterized.expand([
        ('low coverage should return False', 10, False),
        ('high coverage should return True', 25, True)
    ])
    def test_satisfied_by_with_(self, _, coverage, expected):
        item = mock.MagicMock()
        item.metrics.lineCoverage = coverage
        result = self.constraint.satisfied_by(item)
        self.assertEqual(expected, result.satisfied)

class BranchCoverageTest(VigilenceTestCase):
    def setUp(self):
        super(BranchCoverageTest, self).setUp()
        from vigilence.default_suites.cobertura import BranchCoverage
        self.constraint = BranchCoverage(22)

    @parameterized.expand([
        ('low coverage should return False', 10, False),
        ('high coverage should return True', 25, True)
    ])
    def test_satisfied_by_with_(self, _, coverage, expected):
        item = mock.MagicMock()
        item.metrics.branchCoverage = coverage
        result = self.constraint.satisfied_by(item)
        self.assertEqual(expected, result.satisfied)

class ComplexityText(VigilenceTestCase):
    def setUp(self):
        super(ComplexityText, self).setUp()
        from vigilence.default_suites.cobertura import Complexity
        self.constraint = Complexity(10)

    @parameterized.expand([
        ('low complexity should return True', 5, True),
        ('high complexity should return False', 25, False)
    ])
    def test_satisfied_by_with_(self, _, coverage, expected):
        item = mock.MagicMock()
        item.metrics.complexity = coverage
        result = self.constraint.satisfied_by(item)
        self.assertEqual(expected, result.satisfied)
