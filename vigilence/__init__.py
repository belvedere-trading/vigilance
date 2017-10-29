"""@defgroup vigilence vigilence
"""

import logging

Log = logging.getLogger(__name__)
Log.addHandler(logging.StreamHandler())

from vigilence.default_suites import * #pylint: disable=wildcard-import,wrong-import-position
