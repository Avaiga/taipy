from .update_aware import UpdateAware


def stateUpdate(cls: type):
    """Decorator to mark a class as state update aware.

    This decorator is used to indicate that the decorated class can be registered to provide state updates.

    Example usage:

    ```python
    @stateUpdate
    class MyStateUpdate:
        # Code to update the state goes here
        pass
    ```

    Returns:
        The original class, unchanged.
    """
    if not issubclass(cls, UpdateAware):
        cls.__bases__ = (UpdateAware,) + cls.__bases__
    return cls
