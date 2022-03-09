from importlib import util


def _is_in_notebook():  # pragma: no cover
    try:
        if not util.find_spec("IPython"):
            return False

        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:
            return False
    except (ImportError, AttributeError):
        return False
    return True
