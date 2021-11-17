from json import JSONEncoder

from ..taipyimage import TaipyImage
from ..utils import _MapDictionary


class TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, TaipyImage):
            return o.to_dict()
        elif isinstance(o, _MapDictionary):
            return o._dict
        return o
