from __future__ import absolute_import, division, print_function

import sys
import codecs


PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2


if PY2:
    bytes = str
    text_type = unicode
    string_types = basestring
    range_type = xrange
    iteritems = lambda x: x.iteritems()
    # b = lambda x: x
else:
    text_type = str
    string_types = str,
    range_type = range
    iteritems = lambda x: iter(x.items())
    # b = lambda x: codecs.latin_1_encode(x)[0]
