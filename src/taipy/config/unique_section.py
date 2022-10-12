from abc import ABC

from .section import Section
from .common._validate_id import _validate_id


class UniqueSection(Section, ABC):
    """ A UniqueSection is a configuration Section^ that can have only one instance.

    A UniqueSection is only defined by the section name.
    """

    def __init__(self, **properties):
        super().__init__(_validate_id(self.name), **properties)

