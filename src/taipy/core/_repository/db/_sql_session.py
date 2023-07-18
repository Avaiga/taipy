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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taipy.config.config import Config

from ...exceptions import MissingRequiredProperty
from .._decoder import loads
from .._encoder import dumps


@lru_cache
def _build_engine():
    properties = Config.core.repository_properties
    try:
        # More sql databases can be easily added in the future
        engine = create_engine(
            f"sqlite:///{properties.get('db_location')}?check_same_thread=False",
            poolclass=StaticPool,
            json_serializer=dumps,
            json_deserializer=loads,
        )
        return engine

    except KeyError:
        raise MissingRequiredProperty("Missing property db_location")


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
