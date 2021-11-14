class MissingRequiredProperty(Exception):
    """
    Exception raised if a required property is missing when creating a Data Source.
    """

    pass


class InvalidDataSourceType(Exception):
    """
    Exception raised if a data source does not exist
    """

    pass


class MultipleDataSourceFromSameConfigWithSameParent(Exception):
    """
    Exception raised if it exists multiple data sources from the same data source config and the same parent_id
    """

    pass


class NoData(Exception):
    """
    Exception raised when reading a data source before it has been written
    """

    pass


class UnknownDatabaseEngine(Exception):
    """
    Exception raised when creating a connection with a SQLDataSource
    """

    pass
