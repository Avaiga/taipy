# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t

from flask import g, has_request_context, request

from ..request import _BaseRequestAccessor


class _RequestAccessorFlask(_BaseRequestAccessor):
    def args(self, to_dict=False):
        return request.args if to_dict is False else request.args.to_dict(flat=True)

    def arg(self, key, default=None):
        return request.args.get(key, default)

    def form(self):
        return request.form

    def files(self):
        return request.files

    def cookies(self):
        return request.cookies

    def sid(self):
        if has_request_context() and request:
            return getattr(request, "sid", None)
        return None

    def set_sid(self, incoming_sid: t.Optional[str]):
        request.sid = incoming_sid  # type: ignore[attr-defined]

    def get_request(self):
        return request

    def get_request_meta(self):
        return g

    def has_request_context(self):
        return has_request_context()
