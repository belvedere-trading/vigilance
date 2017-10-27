#pylint: skip-file
import logging
import mock

from unittest import TestCase

class VigilenceTestCase(TestCase):
    @property
    def modulesToPatch(self):
        return {}

    def setUp(self):
        self.patcher = mock.patch.dict('sys.modules', self.modulesToPatch)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def run(self, result=None):
        with mock.patch.object(logging, 'getLogger', spec=logging.LoggerAdapter) as logger:
            self.log = logger.return_value
            super(VigilenceTestCase, self).run(result)
