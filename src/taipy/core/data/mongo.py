# Copyright 2023 Avaiga Private Limited
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
from inspect import isclass
from typing import Any, Dict, List, Optional, Set

import pymongo

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class MongoCollectionDataNode(DataNode):
    """Data Node stored in a Mongo collection.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        name (str): A user-readable name of this data node.
        owner_id (str): The identifier of the owner (sequence_id, scenario_id, cycle_id) or
            None.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The duration implemented as a timedelta since the last edit date for
            which the data node can be considered up-to-date. Once the validity period has passed, the data node is
            considered stale and relevant tasks will run even if they are skippable (see the
            [Task management page](../core/entities/task-mgt.md) for more details).
            If _validity_period_ is set to `None`, the data node is always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        editor_id (Optional[str]): The identifier of the user who is currently editing the data node.
        editor_expiration_date (Optional[datetime]): The expiration date of the editor lock.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the
            _properties_ parameter must at least contain an entry for _"db_name"_ and _"collection_name"_:

            - _"db_name"_ `(str)`: The database name.\n
            - _"collection_name"_ `(str)`: The collection in the database to read from and to write the data to.\n
            - _"custom_document"_ `(Any)`: The custom document class to store, encode, and decode data when reading and
                writing to a Mongo collection.\n
            - _"db_username"_ `(str)`: The database username.\n
            - _"db_password"_ `(str)`: The database password.\n
            - _"db_host"_ `(str)`: The database host. The default value is _"localhost"_.\n
            - _"db_port"_ `(int)`: The database port. The default value is 27017.\n
            - _"db_extra_args"_ `(Dict[str, Any])`: A dictionary of additional arguments to be passed into database
                connection string.\n
    """

    __STORAGE_TYPE = "mongo_collection"

    __DB_NAME_KEY = "db_name"
    __COLLECTION_KEY = "collection_name"
    __DB_USERNAME_KEY = "db_username"
    __DB_PASSWORD_KEY = "db_password"
    __DB_HOST_KEY = "db_host"
    __DB_PORT_KEY = "db_port"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"

    __DB_HOST_DEFAULT = "localhost"
    __DB_PORT_DEFAULT = 27017

    _CUSTOM_DOCUMENT_PROPERTY = "custom_document"
    __DB_EXTRA_ARGS_KEY = "db_extra_args"
    _REQUIRED_PROPERTIES: List[str] = [
        __DB_NAME_KEY,
        __COLLECTION_KEY,
    ]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        name: Optional[str] = None,
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
    ):
        if properties is None:
            properties = {}
        required = self._REQUIRED_PROPERTIES
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required"
            )

        self._check_custom_document(properties[self._CUSTOM_DOCUMENT_PROPERTY])

        super().__init__(
            config_id,
            scope,
            id,
            name,
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
            db_extra_args=properties.get(self.__DB_EXTRA_ARGS_KEY, {}),
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

        if not self._last_edit_date:
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
                self.__DB_EXTRA_ARGS_KEY,
            }
        )

    def _check_custom_document(self, custom_document):
        if not isclass(custom_document):
            raise InvalidCustomDocument(
                f"Invalid custom document of {custom_document}. Only custom class are supported."
            )

    @classmethod
    def storage_type(cls) -> str:
        return cls.__STORAGE_TYPE

    def _read(self):
        cursor = self._read_by_query()

        return list(map(lambda row: self._decoder(row), cursor))

    def _read_by_query(self):
        """Query from a Mongo collection, exclude the _id field"""

        return self.collection.find()

    def _write(self, data) -> None:
        """Check data against a collection of types to handle insertion on the database."""

        if not isinstance(data, list):
            data = [data]

        if len(data) == 0:
            self.collection.drop()
            return

        if isinstance(data[0], dict):
            self._insert_dicts(data)
        else:
            self._insert_dicts([self._encoder(row) for row in data])

    def _insert_dicts(self, data: List[Dict]) -> None:
        """
        :param data: a list of dictionaries

        This method will overwrite the data contained in a list of dictionaries into a collection.
        """
        self.collection.drop()
        self.collection.insert_many(data)

    def _default_decoder(self, document: Dict) -> Any:
        """Decode a Mongo dictionary to a custom document object for reading.

        Args:
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


def _connect_mongodb(
    db_host: str, db_port: int, db_username: str, db_password: str, db_extra_args: Dict[str, str]
) -> pymongo.MongoClient:
    """Create a connection to a Mongo database.

    Args:
        db_host (str): the database host.
        db_port (int): the database port.
        db_username (str): the database username.
        db_password (str): the database password.
        db_extra_args (Dict[str, Any]): A dictionary of additional arguments to be passed into database connection
            string.

    Returns:
        pymongo.MongoClient
    """
    auth_str = ""
    if db_username and db_password:
        auth_str = f"{db_username}:{db_password}@"

    extra_args_str = "&".join(f"{k}={str(v)}" for k, v in db_extra_args.items())
    if extra_args_str:
        extra_args_str = "/?" + extra_args_str

    connection_string = f"mongodb://{auth_str}{db_host}:{db_port}{extra_args_str}"

    return pymongo.MongoClient(connection_string)
