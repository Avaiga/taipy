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

from marshmallow import Schema, fields


class CallableSchema(Schema):
    fct_name = fields.String()
    fct_module = fields.String()


class JobSchema(Schema):
    id = fields.String()
    task_id = fields.String()
    status = fields.String()
    force = fields.Boolean()
    creation_date = fields.String()
    subscribers = fields.Nested(CallableSchema)
    stacktrace = fields.List(fields.String)
