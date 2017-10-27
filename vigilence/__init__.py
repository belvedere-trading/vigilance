"""@defgroup vigilence vigilence
"""

from logging import getLogger, StreamHandler

Log = getLogger(__name__)
Log.addHandler(StreamHandler())

from vigilence.default_suites import * #pylint: disable=wildcard-import
