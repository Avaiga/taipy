from datetime import datetime
from json import JSONEncoder
from pathlib import Path
import warnings

from ..icon import Icon
from ..utils import _MapDict, TaipyBase, date_to_ISO


class TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Icon):
            return o.to_dict()
        elif isinstance(o, _MapDict):
            return o._dict
        elif isinstance(o, TaipyBase):
            return o.get()
        elif isinstance(o, datetime):
            return date_to_ISO(o)
        elif isinstance(o, Path):
            return str(o)
        try:
            return JSONEncoder.default(self, o)
        except Exception as e:
            warnings.warn(f"JSONEncoder has thrown {e}")
            return None
