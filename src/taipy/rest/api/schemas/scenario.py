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

from marshmallow import Schema, fields


class ScenarioSchema(Schema):
    sequences = fields.Dict()
    properties = fields.Dict()
    primary_scenario = fields.Boolean(default=False)
    tags = fields.List(fields.String)
    version = fields.String()


class ScenarioResponseSchema(ScenarioSchema):
    id = fields.String()
    subscribers = fields.List(fields.Dict)
    cycle = fields.String()
    creation_date = fields.String()
