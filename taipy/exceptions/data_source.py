class MissingRequiredProperty(Exception):
    """
    Exception raised if a required property is missing when creating a Data Source.
    """

    pass


class InvalidDataSourceType(Exception):
    """
    Exception raised if a data entity entity does not exist
    """

    pass
