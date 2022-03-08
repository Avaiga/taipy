import keyword

from taipy.core.exceptions.configuration import InvalidConfigurationId


def _validate_id(name: str):
    if name.isidentifier() and not keyword.iskeyword(name):
        return name
    raise InvalidConfigurationId(f"{name} is not a valid identifier.")
