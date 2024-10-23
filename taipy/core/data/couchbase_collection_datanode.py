# couchbase_collection_datanode.py

from datetime import datetime, timedelta
from inspect import isclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..data.operator import JoinOperator, Operator
from ..exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty
from .data_node import DataNode

from .data_node_id import DataNodeId, Edit


class CouchbaseDocument:
    """Class to define the structure of documents stored in Couchbase."""

    def __init__(self, field1: str, field2: int, **kwargs):
        self.field1 = field1  # Example field of type string
        self.field2 = field2  # Example field of type integer
        # Additional fields can be added dynamically
        for key, value in kwargs.items():
            setattr(self, key, value)

class CouchBaseCollectionDataNode(DataNode):
    """Data Node stored in a Couchbase collection.

    The *properties* attribute must contain the following mandatory entries:

    - *db_name* (`str`): The bucket name in Couchbase.
    - *collection_name* (`str`): The collection name in the Couchbase bucket to read from and to write the data to.

    The *properties* attribute can also contain the following optional entries:

    - *db_username* (`str`): The username for the Couchbase database.
    - *db_password* (`str`): The password for the Couchbase database.
    - *db_host* (`str`): The database host. The default value is *"localhost"*.
    - *db_port* (`int`): The database port. The default value is *8091*.
    """

    __STORAGE_TYPE = "couchbase_collection"

    __DB_NAME_KEY = "db_name"
    __COLLECTION_KEY = "collection_name"
    __DB_USERNAME_KEY = "db_username"
    __DB_PASSWORD_KEY = "db_password"
    __DB_HOST_KEY = "db_host"
    __DB_PORT_KEY = "db_port"

    __DB_HOST_DEFAULT = "localhost"
    __DB_PORT_DEFAULT = 8091

    _REQUIRED_PROPERTIES: List[str] = [
        __DB_NAME_KEY,
        __COLLECTION_KEY,
    ]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: List[Edit] = None,
        version: str = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Dict = None,
    ) -> None:
        if properties is None:
            properties = {}
        required = self._REQUIRED_PROPERTIES
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(missing)} were not informed and are required."
            )

        super().__init__(
            config_id,
            scope,
            id,
            owner_id,
            parent_ids,
            last_edit_date,
            edits,
            version or _VersionManagerFactory._build_manager()._get_latest_version(),
            validity_period,
            edit_in_progress,
            editor_id,
            editor_expiration_date,
            **properties,
        )


         # Create a Couchbase connection using the provided properties.
         # For more information on connecting to Couchbase, see:
    # https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html
        try:
            self.cluster = Cluster(
                f"couchbase://{properties.get(self.__DB_HOST_KEY, self.__DB_HOST_DEFAULT)}",
                ClusterOptions(
                    PsswordAuthenticator(
                        properties.get(self.__DB_USERNAME_KEY, ""),
                        properties.get(self.__DB_PASSWORD_KEY, "")
                    )
                )
            )
            bucket = self.cluster.bucket(properties.get(self.__DB_NAME_KEY))
            self.collection = bucket.collection(properties.get(self.__COLLECTION_KEY))

        except CouchbaseException as e:
            raise ConnectionError(f"Could not connect to Couchbase: {e}")

        self._TAIPY_PROPERTIES.update(
            {
                self.__COLLECTION_KEY,
                self.__DB_NAME_KEY,
                self.__DB_USERNAME_KEY,
                self.__DB_PASSWORD_KEY,
                self.__DB_HOST_KEY,
                self.__DB_PORT_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "couchbase_collection"."""
        return cls.__STORAGE_TYPE

    def _read(self):
        """Read all documents from the Couchbase collection."""
        try:
            query = f"SELECT * FROM `{self.collection.name}`"
            result = self.cluster.query(query)

            return [doc.content_as[dict] for doc in documents]
        except Exception as e:
             print(f"An error occurred: {e}")
             return []

    def _write(self,data : Union[Dict, List[Dict]]):
           """Write Documents to the Couchbase collection."""
        try:
            if isinstance(data, dict):
                self.collection.upsert(data['id'],data)
            elif isinstance(data, list):
                for item in data:
                   self.collection.upsert(item['id'], item)
       except CouchbaseException as e:
            print(f"An error occurred while writing:{e}")

   def _append(self,data: Union[Dict, List[Dict]]):
         """Append data to the Couchbase collection without overwriting."""
        try:
            if isinstance(data, dict):
              if not self.collection.exists(data['id']):
                  self.collection.insert(data['id'], data)
            elif isinstance(data, list):
               for item in data:
                  if not self.collection.exists(item['id']):
                      self.collection.insert(item['id'], item)
        except CouchbaseException as e:
            print(f"An error occurred while appending: {e}")
  def filter(self, criteria: Dict[str, Any]):
         """Filter documents in the Couchbase collection based on criteria"""
         try:
             where_clause = " AND ".join([f"{key} = '{value}'" for key, value in criteria.items()])
             query = f"SELECT * FROM `{self.collection.name}` WHERE {where_clause}"
             result = self.cluster.query(query)
             return [doc for doc in result]
        except CouchbaseException as e:
             print(f"An error occurred while filtering documents:{e}")
             return []
