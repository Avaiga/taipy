class MapDictionary(dict):
    """
    Provide class binding, can utilize getattr, setattr functionality
    Also perform ws (websocket) operation
    """

    def __init__(self, ws, dict_import):
        # Verify if dict_import is a dictionary
        if isinstance(dict_import, dict):
            super(MapDictionary, self).__init__(dict_import)
            for k, v in dict_import.items():
                self[k] = v
        else:
            super(MapDictionary, self).__init__()
        # Bind websocket
        self._ws = ws

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(MapDictionary, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(MapDictionary, self).__delitem__(key)
        del self.__dict__[key]

    def get_dict(self):
        def without_keys(d, keys):
            return {x: d[x] for x in d if x not in keys}
        return without_keys(self.__dict__, {"_ws"})
    
    
