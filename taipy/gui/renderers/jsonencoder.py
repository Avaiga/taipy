from datetime import datetime
from json import JSONEncoder
from pathlib import Path
import warnings

from ..taipyimage import TaipyImage
from ..utils import _MapDict, TaipyBase, dateToISO


class TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, TaipyImage):
            return o.to_dict()
        elif isinstance(o, _MapDict):
            return o._dict
        elif isinstance(o, TaipyBase):
            return o.get()
        elif isinstance(o, datetime):
            return dateToISO(o)
        elif isinstance(o, Path):
            return str(o)
        try:
            return JSONEncoder.default(self, o)
        except Exception as e:
            warnings.warn(f"JSONEncoder has thrown {e}")
            return None
