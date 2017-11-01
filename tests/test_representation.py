#pylint: skip-file
import mock

from util import VigilanceTestCase

class QualityReportTest(VigilanceTestCase):
    def setUp(self):
        super(QualityReportTest, self).setUp()
        from vigilance.constraint import ConstraintSet, Constraint
        from vigilance.representation import QualityReport, Satisfaction
        self.mockConstraints = mock.MagicMock(spec=ConstraintSet)
        constraint = mock.MagicMock(**{'satisfied_by.side_effect': lambda i: Satisfaction(i != 7, i)})
        self.mockConstraints.constraints_for.return_value = [constraint]
        self.report = QualityReport([6, 7, 8])

    def test_scrutinize_should_return_dissatisfactions(self):
        dissatisfaction, = self.report.scrutinize(self.mockConstraints)
        self.assertEqual(7, dissatisfaction.message)
