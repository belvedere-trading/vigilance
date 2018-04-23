#pylint: skip-file
import logging
import mock
from functools import wraps

from unittest import TestCase

class VigilanceTestCase(TestCase):
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
            super(VigilanceTestCase, self).run(result)

def mock_decorator(*args, **kwargs):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator