#pylint: skip-file
import mock
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
