class MissingRequiredProperty(Exception):
    """
    Raised if a required property is missing when creating a Data Source.
    """

    pass


class InvalidDataSourceType(Exception):
    """
    Raised if a data source does not exist.
    """

    pass


class MultipleDataSourceFromSameConfigWithSameParent(Exception):
    """
    Raised if there are multiple data sources from the same data source configuration and the same parent identifier.
    """

    pass


class NoData(Exception):
    """
    Raised when reading a data source before it has been written.
    """

    pass


class UnknownDatabaseEngine(Exception):
    """
    Exception raised when creating a connection with a SQLDataSource
    """

    pass


class NonExistingDataSource(Exception):
    """
    Raised if a requested DataSource is not known by the DataSource Manager.
    """

    def __init__(self, data_source_id: str):
        self.message = f"DataSource: {data_source_id} does not exist."
