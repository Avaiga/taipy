import warnings
from datetime import date, datetime, time
from json import JSONEncoder
from pathlib import Path

from ..icon import Icon
from ..utils import _date_to_ISO, _MapDict, _TaipyBase


class _TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Icon):
            return o._to_dict()
        elif isinstance(o, _MapDict):
            return o._dict
        elif isinstance(o, _TaipyBase):
            return o.get()
        elif isinstance(o, (datetime, date, time)):
            return _date_to_ISO(o)
        elif isinstance(o, Path):
            return str(o)
        try:
            return JSONEncoder.default(self, o)
        except Exception as e:
            warnings.warn(f"JSONEncoder has thrown {e}")
            return None
