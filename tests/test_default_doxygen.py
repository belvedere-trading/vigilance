#pylint: skip-file
import mock

from util import VigilenceTestCase

class DocumentationErrorTest(VigilenceTestCase):
    def setUp(self):
        super(DocumentationErrorTest, self).setUp()
        from vigilence.default_suites.doxygen import DocumentationError
        self.item = DocumentationError('this was the error')

    def test_identifier_should_return_error_message(self):
        self.assertEqual('documentation failure: this was the error', self.item.identifier)

class DoxygenParserTest(VigilenceTestCase):
    def setUp(self):
        super(DoxygenParserTest, self).setUp()
        from vigilence.default_suites.doxygen import DoxygenParser
        self.parser = DoxygenParser()

    def test_parse_should_return_documentation_error_per_line(self):
        report = self.parser.parse('a\nb\nc\n\n\n')
        self.assertEqual(['a', 'b', 'c'], [item.metrics for item in report.items])

class DocumentationTest(VigilenceTestCase):
    def setUp(self):
        super(DocumentationTest, self).setUp()
        global DocumentationError
        from vigilence.default_suites.doxygen import Documentation, DocumentationError
        self.constraint = Documentation()

    def test_satisfied_by_should_return_False(self):
        result = self.constraint.satisfied_by(DocumentationError('bad'))
        self.assertFalse(result.satisfied)
        self.assertEqual('documentation failure: bad', result.message)

class DocumentationStanzaTest(VigilenceTestCase):
    def setUp(self):
        super(DocumentationStanzaTest, self).setUp()
        global Documentation
        from vigilence.default_suites.doxygen import DocumentationStanza, Documentation
        self.configuration = DocumentationStanza(None)

    def test_parse_should_return_single_documentation_constraint(self):
        constraint, = self.configuration.parse(None)
        self.assertTrue(isinstance(constraint, Documentation))
