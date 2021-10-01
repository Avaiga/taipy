class _MapDictionary(object):
    """
    Provide class binding, can utilize getattr, setattr functionality
    Also perform update operation
    """

    local_vars = ("_dict", "_update_var")

    def __init__(self, dict_import, app_update_var=None):
        self._dict = dict_import
        # Bind app update var function
        self._update_var = app_update_var
        # Verify if dict_import is a dictionary
        if not isinstance(dict_import, dict):
            raise TypeError("should have a dict")

    def __len__(self):
        return self._dict.__len__()

    def __length_hint__(self):
        return self._dict.__length_hint__()

    def __getitem__(self, key):
        value = self._dict.__getitem__(key)
        if isinstance(value, dict):
            if self._update_var:
                return _MapDictionary(value, lambda s, v: self._update_var(key + "." + s, v))
            else:
                return _MapDictionary(value)
        return value

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)
        if self._update_var:
            self._update_var(key, value)

    def __delitem__(self, key):
        self._dict.__delitem__(key)

    def __missing__(self, key):
        return self._dict.__missing__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __reversed__(self):
        return self._dict.__reversed__()

    def __contains__(self, item):
        return self._dict.__contains__(item)

    # to be able to use getattr
    def __getattr__(self, attr):
        return self._dict.get(attr)

    def __setattr__(self, attr, value):
        if attr in _MapDictionary.local_vars:
            super().__setattr__(attr, value)
        else:
            self.__setitem__(attr, value)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def get(self):
        return self._dict.get()

    def clear(self):
        return self._dict.clear()

    def setdefault(self):
        return self._dict.setdefault()

    def pop(self):
        return self._dict.pop()

    def popitem(self):
        return self._dict.popitem()

    def copy(self):
        return _MapDictionary(self._dict.copy(), self._update_var)

    def update(self):
        return self._dict.update()
