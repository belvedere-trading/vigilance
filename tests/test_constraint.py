#pylint: skip-file
import mock
import re
from collections import namedtuple
from nose_parameterized import parameterized

from util import VigilenceTestCase

FakePackage = namedtuple('FakePackage', ['name'])

class PackageConstraintTest(VigilenceTestCase):
    def setUp(self):
        super(PackageConstraintTest, self).setUp()
        from vigilence.constraint import Constraint, PackageConstraint
        self.mockConstraint = mock.MagicMock(spec=Constraint)
        self.constraint = PackageConstraint(self.mockConstraint, 'vigilence')

    @parameterized.expand([
        ('with matching type should return True', str, True),
        ('with mismatched type should return False', int, False)
    ])
    def test_if_of_type_should_forward_comparison_to_inner_constraint(self, _, typ, expected):
        self.constraint.constraint = 'hi'
        self.assertEqual(expected, self.constraint.is_of_type(typ))

    def test_satisfied_by_should_forward_to_inner_constraint(self):
        self.mockConstraint.satisfied_by.return_value = 'totally satisfied'
        self.assertEqual('totally satisfied', self.constraint.satisfied_by('thing'))

    @parameterized.expand([
        ('return True when name matches', 'vigilence', True),
        ('return False when name mismatches', 'asdf', False),
        ('return False when no name', None, False)
    ])
    def test_applies_to_should(self, _, name, expected):
        item = None
        if name is not None:
            item = mock.MagicMock()
            item.name = name
        self.assertEqual(expected, self.constraint.applies_to(item))

class FileConstraintTest(VigilenceTestCase):
    def setUp(self):
        super(FileConstraintTest, self).setUp()
        from vigilence.constraint import Constraint, FileConstraint
        self.mockConstraint = mock.MagicMock(spec=Constraint)
        self.constraint = FileConstraint(self.mockConstraint, re.compile('Thing.*'))

    @parameterized.expand([
        ('with matching type should return True', str, True),
        ('with mismatched type should return False', int, False)
    ])
    def test_if_of_type_should_forward_comparison_to_inner_constraint(self, _, typ, expected):
        self.constraint.constraint = 'hi'
        self.assertEqual(expected, self.constraint.is_of_type(typ))

    def test_satisfied_by_should_forward_to_inner_constraint(self):
        self.mockConstraint.satisfied_by.return_value = 'totally satisfied'
        self.assertEqual('totally satisfied', self.constraint.satisfied_by('thing'))

    @parameterized.expand([
        ('return True when path regex matches', 'Thing one', True),
        ('return False when path regex mismatches', 'asdf', False),
        ('return False when no path regex', None, False)
    ])
    def test_applies_to_should(self, _, pathRegex, expected):
        item = None
        if pathRegex is not None:
            item = mock.MagicMock()
            item.filePath = pathRegex
        self.assertEqual(expected, self.constraint.applies_to(item))

class IgnoreFilesTest(VigilenceTestCase):
    def setUp(self):
        super(IgnoreFilesTest, self).setUp()
        from vigilence.constraint import IgnoreFiles
        self.constraint = IgnoreFiles(['one', 'another'])

    def test_is_of_type_should_return_True(self):
        self.assertTrue(self.constraint.is_of_type('anything'))

    def test_satisfied_by_should_return_true_satisfaction(self):
        result = self.constraint.satisfied_by('anything')
        self.assertTrue(result.satisfied)

    @parameterized.expand([
        ('return True when file path matches', 'another', True),
        ('return False when file path mismatches', 'asdf', False),
        ('return False when no file path', None, False)
    ])
    def test_applies_to_should(self, _, filePath, expected):
        item = None
        if filePath is not None:
            item = mock.MagicMock()
            item.filePath = filePath
        self.assertEqual(expected, self.constraint.applies_to(item))

class ConstraintSuiteTest(VigilenceTestCase):
    def setUp(self):
        super(ConstraintSuiteTest, self).setUp()
        from vigilence.constraint import ConstraintSuite
        self.suite = ConstraintSuite({'label1': 1, 'label2': 2})

    def test_all_types_should_return_all_types(self):
        self.assertEqual(set([1, 2]), set(self.suite.all_types()))

    def test_all_labels_should_return_all_labels(self):
        self.assertEqual(set(['label1', 'label2']), set(self.suite.all_labels()))

    def test_get_constraint_should_return_constraint(self):
        self.assertEqual(1, self.suite.get_constraint('label1'))

    def test_group_constraints_should_group_by_type(self):
        mock1 = mock.MagicMock(**{'is_of_type.side_effect': lambda t: t == 1})
        mock2 = mock.MagicMock(**{'is_of_type.side_effect': lambda t: t == 2})
        constraints = [mock1, mock2]
        grouped = self.suite.group_constraints(constraints)
        self.assertEqual(grouped, {1: [mock1], 2: [mock2]})
