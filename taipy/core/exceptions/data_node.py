class MissingRequiredProperty(Exception):
    """
    Raised if a required property is missing when creating a Data Node.
    """

    pass


class InvalidDataNodeType(Exception):
    """
    Raised if a data node storage type does not exist.
    """

    pass


class MultipleDataNodeFromSameConfigWithSameParent(Exception):
    """
    Raised if there are multiple data nodes from the same data node configuration and the same parent identifier.
    """

    pass


class NoData(Exception):
    """
    Raised when reading a data node before it has been written.
    """

    pass


class UnknownDatabaseEngine(Exception):
    """
    Exception raised when creating a connection with a SQLDataNode
    """

    pass


class NonExistingDataNode(Exception):
    """
    Raised if a requested DataNode is not known by the DataNode Manager.
    """

    def __init__(self, data_node_id: str):
        self.message = f"DataNode: {data_node_id} does not exist."


class NonExistingExcelSheet(Exception):
    """
    Raised if a requested Sheet name does not exist in the provided Excel file.
    """

    def __init__(self, sheet_name: str, excel_file_name: str):
        self.message = f"{sheet_name} does not exist in {excel_file_name}."


class NotMatchSheetNameAndCustomObject(Exception):
    """
    Raised if a provided list of sheet names does not match with the provided list of custom objects.
    """

class MissingReadFunction(Exception):
    """
    Raised if no read function is provided for the GenericDataNode
    """
    
class MissingWriteFunction(Exception):
    """
    Raised if no write function is provided for the GenericDataNode
    """