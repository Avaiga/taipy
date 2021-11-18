class CycleAlreadyExists(Exception):
    """
    Exception raised if it is trying to create a Cycle that has already exists
    """

    pass


class NonExistingCycle(Exception):
    """
    Exception raised if we request a cycle not known by the cycle manager.
    """
