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

from functools import lru_cache

import pymongo


@lru_cache
def _connect_mongodb(
    db_host: str, db_port: int, db_username: str, db_password: str, db_extra_args: frozenset, db_driver: str
) -> pymongo.MongoClient:
    """Create a connection to a Mongo database.
    The `"mongodb_extra_args"` passed by the user is originally a dictionary, but since `@lru_cache` wrapper only
    accepts hashable parameters, the `"mongodb_extra_args"` should be converted into a frozenset beforehand.

    Parameters:
        db_host (str): the database host.
        db_port (int): the database port.
        db_username (str): the database username.
        db_password (str): the database password.
        db_extra_args (frozenset): A frozenset converted from a dictionary of additional arguments to be passed into
            database connection string.

    Returns:
        pymongo.MongoClient
    """
    auth_str = ""
    if db_username and db_password:
        auth_str = f"{db_username}:{db_password}@"

    extra_args_str = "&".join(f"{k}={str(v)}" for k, v in db_extra_args)
    if extra_args_str:
        extra_args_str = "/?" + extra_args_str

    driver = "mongodb"
    if db_driver:
        driver = f"{driver}+{db_driver}"

    connection_string = f"{driver}://{auth_str}{db_host}"
    connection_string = connection_string if db_driver else f"{connection_string}:{db_port}"
    connection_string += extra_args_str

    return pymongo.MongoClient(connection_string)
