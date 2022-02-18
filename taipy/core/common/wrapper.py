from collections import UserDict


class Properties(UserDict):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def __setitem__(self, key, value):
        super(Properties, self).__setitem__(key, value)
        from taipy.core import Taipy as tp

        if hasattr(self, "parent"):
            tp.set(self.parent)
