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

from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.taipy.core.exceptions import MissingRequiredProperty
from taipy.config.config import Config


@cache
def _build_engine():
    properties = Config.global_config.repository_properties
    try:
        # More sql databases can be easily added in the future
        engine = create_engine(
            f"sqlite:///{properties.get('db_location')}?check_same_thread=False", poolclass=StaticPool
        )
        return engine

    except KeyError:
        raise MissingRequiredProperty("Missing property db_location")


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
