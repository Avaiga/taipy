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

from functools import lru_cache
from typing import Dict

import pymongo

from taipy.logger._taipy_logger import _TaipyLogger

from ._utils import _migrate

__logger = _TaipyLogger._get_logger()


@lru_cache
def _connect_mongodb(db_host: str, db_port: int, db_username: str, db_password: str) -> pymongo.MongoClient:
    auth_str = ""
    if db_username and db_password:
        auth_str = f"{db_username}:{db_password}@"

    connection_string = f"mongodb://{auth_str}{db_host}:{db_port}"

    return pymongo.MongoClient(connection_string)


def __load_all_entities_from_mongo(
    hostname: str,
    port: int,
    user: str,
    password: str,
):
    client = _connect_mongodb(hostname, port, user, password)
    collections = [
        "cycle",
        "scenario",
        "pipeline",
        "task",
        "data_node",
        "job",
        "version",
    ]
    entities = {}
    for collection in collections:
        db = client["taipy"]
        cursor = db[collection].find({})
        for document in cursor:
            entities[document["id"]] = {"data": document}

    return entities


def __write_entities_to_mongo(
    _entities: Dict,
    hostname: str,
    port: int,
    user: str,
    password: str,
):
    client = _connect_mongodb(hostname, port, user, password)
    collections = [
        "cycle",
        "scenario",
        "task",
        "data_node",
        "job",
        "version",
    ]
    for collection in collections:
        db = client["taipy"]
        db[collection].insert_many(
            [entity["data"] for entity in _entities.values() if collection in entity["data"]["id"]]
        )


def _revert_migrate_mongo_entities(
    hostname: str = "localhost",
    port: int = 27017,
    user: str = "",
    password: str = "",
) -> bool:
    # TODO
    return True


def _clean_backup_mongo_entities(
    hostname: str = "localhost",
    port: int = 27017,
    user: str = "",
    password: str = "",
) -> bool:
    # TODO
    return True


def _migrate_mongo_entities(
    hostname: str = "localhost",
    port: int = 27017,
    user: str = "",
    password: str = "",
    backup: bool = True,
) -> bool:
    """Migrate entities from mongodb to the current version.

    Args:
        hostname (str, optional): The hostname of the mongodb. Defaults to "localhost".
        port (int, optional): The port of the mongodb. Defaults to 27017.
        user (str, optional): The username of the mongodb. Defaults to "".
        password (str, optional): The password of the mongodb. Defaults to "".
        backup (bool, optional): Whether to backup the entities before migrating. Defaults to True.

    Returns:
        bool: True if the migration was successful, False otherwise.
    """
    if backup:
        # TODO: Back up entities in the mongodb
        pass

    __logger.info(f"Starting entity migration from MongoDB {hostname}:{port}")

    entities = __load_all_entities_from_mongo(hostname, port, user, password)
    entities, _ = _migrate(entities)
    __write_entities_to_mongo(entities, hostname, port, user, password)

    __logger.info("Migration finished")
    return True
