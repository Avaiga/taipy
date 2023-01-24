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


from typing import Union

from sqlalchemy import Boolean, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Json = Union[dict, list, str, int, float, bool, None]


class _TaipyModel(Base):  # type: ignore
    """_TaipyModel Represents the table used to store the information of taipy entities."""

    __tablename__ = "taipy_model"

    id = Column(Integer, primary_key=True)
    model_id = Column(Text)
    model_name = Column(Text)
    document = Column(Text)

    def __int__(self, model_id: str, model_name: str, document: Json):
        self.model_id = model_id
        self.model_name = model_name
        self.document = document


class _TaipyVersion(Base):  # type: ignore
    """_TaipyVersion Represents the table used to store versioning information of taipy configs."""

    __tablename__ = "taipy_version"

    id = Column(Text, primary_key=True)
    config = Column(Text)
    creation_date = Column(Text)
    is_production = Column(Boolean)
    is_development = Column(Boolean)
    is_latest = Column(Boolean)

    def __int__(
        self,
        id: str,
        config: Json,
        creation_date: str,
    ):
        self.id = id
        self.config = config
        self.creation_date = creation_date
        self.is_production = False
        self.is_development = False
        self.latest = False
