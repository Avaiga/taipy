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

from taipy.config.common._validate_id import _validate_id


class MongoDefaultDocument:
    """The default class for \"custom_document\" property to configure a `MongoCollectionDataNode^`.

    Attributes:
        **kwargs: Attributes of the MongoDefaultDocument object.

    Example:
        - `document = MongoDefaultDocument(name="example", age=30})`
        will return a MongoDefaultDocument object so that `document.name` returns `"example"`,
        and `document.age` returns `30`.
        - `document = MongoDefaultDocument(date="12/24/2018", temperature=20})`
        will return a MongoDefaultDocument object so that `document.date` returns `"12/24/2018"`,
        and `document.temperature` returns `20`.
    """

    def __init__(self, **kwargs):
        for attribute_name, value in kwargs.items():
            setattr(self, _validate_id(attribute_name), value)
