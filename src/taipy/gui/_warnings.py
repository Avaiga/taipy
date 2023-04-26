import warnings


class TaipyGuiWarning(UserWarning):
    pass


def _warn(message: str):
    warnings.warn(message, TaipyGuiWarning, stacklevel=2)
