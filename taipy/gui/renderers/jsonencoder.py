from datetime import datetime
from json import JSONEncoder
import warnings

from ..taipyimage import TaipyImage
from ..utils import _MapDictionary, TaipyBase, dateToISO


class TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, TaipyImage):
            return o.to_dict()
        elif isinstance(o, _MapDictionary):
            return o._dict
        elif isinstance(o, TaipyBase):
            return o.get()
        elif isinstance(o, datetime):
            return dateToISO(o)
        try:
            return JSONEncoder.default(self, o)
        except Exception as e:
            warnings.warn(f"JSONEncoder has thrown {e}")
            return None
