# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from datetime import datetime, timedelta
from importlib import util
from inspect import isclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..common._check_dependencies import _check_dependency_is_installed

if util.find_spec("pymongo"):
    from ..common._mongo_connector import _connect_mongodb

from ..data.operator import JoinOperator, Operator
from ..exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class MongoCollectionDataNode(DataNode):
    """Data Node stored in a Mongo collection.

    The *properties* attribute must contain the following mandatory entries:

    - *db_name* (`str`): The database name.
    - *collection_name* (`str`): The collection in the database to read from and to write the data to.

    The *properties* attribute can also contain the following optional entries:

    - *custom_document* (`Any`): The custom document class to store, encode, and decode data when reading
        and writing to a Mongo collection.
    - *db_username* (`str`): The database username.
    - *db_password* (`str`): The database password.
    - *db_host* (`str`): The database host. The default value is *"localhost"*.
    - *db_port* (`str`): The database port. The default value is *27017*.
    - *db_driver* (`str`): The database driver.
    - *db_extra_args* (`Dict[str, Any]`): A dictionary of additional arguments to be passed into
        database connection string.
    """

    __STORAGE_TYPE = "mongo_collection"

    __DB_NAME_KEY = "db_name"
    __COLLECTION_KEY = "collection_name"
    __DB_USERNAME_KEY = "db_username"
    __DB_PASSWORD_KEY = "db_password"
    __DB_HOST_KEY = "db_host"
    __DB_PORT_KEY = "db_port"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"
    __DB_DRIVER_KEY = "db_driver"

    __DB_HOST_DEFAULT = "localhost"
    __DB_PORT_DEFAULT = 27017

    _CUSTOM_DOCUMENT_PROPERTY = "custom_document"
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
        _check_dependency_is_installed("Mongo Data Node", "pymongo")
        if properties is None:
            properties = {}
        required = self._REQUIRED_PROPERTIES
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(missing)} were not informed and are required."
            )

        self._check_custom_document(properties[self._CUSTOM_DOCUMENT_PROPERTY])

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

        mongo_client = _connect_mongodb(
            db_host=properties.get(self.__DB_HOST_KEY, self.__DB_HOST_DEFAULT),
            db_port=properties.get(self.__DB_PORT_KEY, self.__DB_PORT_DEFAULT),
            db_username=properties.get(self.__DB_USERNAME_KEY, ""),
            db_password=properties.get(self.__DB_PASSWORD_KEY, ""),
            db_driver=properties.get(self.__DB_DRIVER_KEY, ""),
            db_extra_args=frozenset(properties.get(self.__DB_EXTRA_ARGS_KEY, {}).items()),
        )
        self.collection = mongo_client[properties.get(self.__DB_NAME_KEY, "")][
            properties.get(self.__COLLECTION_KEY, "")
        ]

        self.custom_document = properties[self._CUSTOM_DOCUMENT_PROPERTY]

        self._decoder = self._default_decoder
        custom_decoder = getattr(self.custom_document, "decode", None)
        if callable(custom_decoder):
            self._decoder = custom_decoder

        self._encoder = self._default_encoder
        custom_encoder = getattr(self.custom_document, "encode", None)
        if callable(custom_encoder):
            self._encoder = custom_encoder

        if not self._last_edit_date:  # type: ignore
            self._last_edit_date = datetime.now()

        self._TAIPY_PROPERTIES.update(
            {
                self.__COLLECTION_KEY,
                self.__DB_NAME_KEY,
                self._CUSTOM_DOCUMENT_PROPERTY,
                self.__DB_USERNAME_KEY,
                self.__DB_PASSWORD_KEY,
                self.__DB_HOST_KEY,
                self.__DB_PORT_KEY,
                self.__DB_DRIVER_KEY,
                self.__DB_EXTRA_ARGS_KEY,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "mongo_collection"."""
        return cls.__STORAGE_TYPE

    def filter(self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND) -> List:
        cursor = self._read_by_query(operators, join_operator)
        return [self._decoder(row) for row in cursor]

    def _read(self):
        cursor = self._read_by_query()
        return [self._decoder(row) for row in cursor]

    def _read_by_query(self, operators: Optional[Union[List, Tuple]] = None, join_operator=JoinOperator.AND):
        """Query from a Mongo collection, exclude the _id field"""
        if not operators:
            return self.collection.find()

        if not isinstance(operators, List):
            operators = [operators]

        conditions = []
        for key, value, operator in operators:
            if operator == Operator.EQUAL:
                conditions.append({key: value})
            elif operator == Operator.NOT_EQUAL:
                conditions.append({key: {"$ne": value}})
            elif operator == Operator.GREATER_THAN:
                conditions.append({key: {"$gt": value}})
            elif operator == Operator.GREATER_OR_EQUAL:
                conditions.append({key: {"$gte": value}})
            elif operator == Operator.LESS_THAN:
                conditions.append({key: {"$lt": value}})
            elif operator == Operator.LESS_OR_EQUAL:
                conditions.append({key: {"$lte": value}})

        query = {}
        if join_operator == JoinOperator.AND:
            query = {"$and": conditions}
        elif join_operator == JoinOperator.OR:
            query = {"$or": conditions}
        else:
            raise NotImplementedError(f"Join operator {join_operator} is not supported.")

        return self.collection.find(query)

    def _append(self, data) -> None:
        """Append data to a Mongo collection."""
        if not isinstance(data, list):
            data = [data]

        if len(data) == 0:
            return

        if isinstance(data[0], dict):
            self._insert_dicts(data)
        else:
            self._insert_dicts([self._encoder(row) for row in data])

    def _write(self, data) -> None:
        """Check data against a collection of types to handle insertion on the database.

        Parameters:
            data (Any): the data to write to the database.
        """
        if not isinstance(data, list):
            data = [data]

        if len(data) == 0:
            self.collection.drop()
            return

        if isinstance(data[0], dict):
            self._insert_dicts(data, drop=True)
        else:
            self._insert_dicts([self._encoder(row) for row in data], drop=True)

    def _insert_dicts(self, data: List[Dict], drop=False) -> None:
        """
        This method will insert data contained in a list of dictionaries into a collection.

        Parameters:
            data (List[Dict]): a list of dictionaries
            drop (bool): drop the collection before inserting the data to overwrite the data in the collection.
        """
        if drop:
            self.collection.drop()

        self.collection.insert_many(data)

    def _check_custom_document(self, custom_document):
        if not isclass(custom_document):
            raise InvalidCustomDocument(
                f"Invalid custom document of {custom_document}. Only custom class are supported."
            )

    def _default_decoder(self, document: Dict) -> Any:
        """Decode a Mongo dictionary to a custom document object for reading.

        Parameters:
            document (Dict): the document dictionary return by Mongo query.

        Returns:
            A custom document object.
        """
        return self.custom_document(**document)

    def _default_encoder(self, document_object: Any) -> Dict:
        """Encode a custom document object to a dictionary for writing to MongoDB.

        Args:
            document_object: the custom document class.

        Returns:
            The document dictionary.
        """
        return document_object.__dict__

