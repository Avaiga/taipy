from collections import UserList


class _ListAttributes(UserList):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    def __add_iterable(self, iterable):
        for i in iterable:
            super(_ListAttributes, self).append(i)

    def __add__(self, value):
        if hasattr(value, "__iter__"):
            return self.__add_iterable(value)
        else:
            return self.append(value)

    def extend(self, value) -> None:
        return self.__add_iterable(value)

    def append(self, value) -> None:
        super(_ListAttributes, self).append(value)

        import taipy.core as tp

        if hasattr(self, "parent"):
            tp.set(self.parent)
