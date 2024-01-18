"""Core apispec classes and functions."""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
import warnings
import typing

from packaging.version import Version

from .exceptions import (
    APISpecError,
    PluginMethodNotImplementedError,
    DuplicateComponentNameError,
    DuplicateParameterError,
    InvalidParameterError,
)
from .utils import deepupdate, COMPONENT_SUBSECTIONS, build_reference

if typing.TYPE_CHECKING:
    from .plugin import BasePlugin


VALID_METHODS_OPENAPI_V2 = ["get", "post", "put", "patch", "delete", "head", "options"]

VALID_METHODS_OPENAPI_V3 = VALID_METHODS_OPENAPI_V2 + ["trace"]

VALID_METHODS = {2: VALID_METHODS_OPENAPI_V2, 3: VALID_METHODS_OPENAPI_V3}

MIN_INCLUSIVE_OPENAPI_VERSION = Version("2.0")
MAX_EXCLUSIVE_OPENAPI_VERSION = Version("4.0")


class Components:
    """Stores OpenAPI components

    Components are top-level fields in OAS v2.
    They became sub-fields of "components" top-level field in OAS v3.
    """

    def __init__(
        self,
        plugins: Sequence[BasePlugin],
        openapi_version: Version,
    ) -> None:
        self._plugins = plugins
        self.openapi_version = openapi_version
        self.schemas: dict[str, dict] = {}
        self.responses: dict[str, dict] = {}
        self.parameters: dict[str, dict] = {}
        self.headers: dict[str, dict] = {}
        self.examples: dict[str, dict] = {}
        self.security_schemes: dict[str, dict] = {}
        self.schemas_lazy: dict[str, dict] = {}
        self.responses_lazy: dict[str, dict] = {}
        self.parameters_lazy: dict[str, dict] = {}
        self.headers_lazy: dict[str, dict] = {}
        self.examples_lazy: dict[str, dict] = {}

        self._subsections = {
            "schema": self.schemas,
            "response": self.responses,
            "parameter": self.parameters,
            "header": self.headers,
            "example": self.examples,
            "security_scheme": self.security_schemes,
        }
        self._subsections_lazy = {
            "schema": self.schemas_lazy,
            "response": self.responses_lazy,
            "parameter": self.parameters_lazy,
            "header": self.headers_lazy,
            "example": self.examples_lazy,
        }

    def to_dict(self) -> dict[str, dict]:
        return {
            COMPONENT_SUBSECTIONS[self.openapi_version.major][k]: v
            for k, v in self._subsections.items()
            if v != {}
        }

    def _register_component(
        self,
        obj_type: str,
        component_id: str,
        component: dict,
        *,
        lazy: bool = False,
    ) -> None:
        subsection = (self._subsections if lazy is False else self._subsections_lazy)[
            obj_type
        ]
        subsection[component_id] = component

    def _do_register_lazy_component(
        self,
        obj_type: str,
        component_id: str,
    ) -> None:
        component_buffer = self._subsections_lazy[obj_type]
        # If component was lazy registered, register it for real
        if component_id in component_buffer:
            self._subsections[obj_type][component_id] = component_buffer.pop(
                component_id
            )

    def get_ref(
        self,
        obj_type: str,
        obj_or_component_id: dict | str,
    ) -> dict:
        """Return object or reference

        If obj is a dict, it is assumed to be a complete description and it is returned as is.
        Otherwise, it is assumed to be a reference name as string and the corresponding $ref
        string is returned.

        :param str subsection: "schema", "parameter", "response" or "security_scheme"
        :param dict|str obj: object in dict form or as ref_id string
        """
        if isinstance(obj_or_component_id, dict):
            return obj_or_component_id
        # Register the component if it was lazy registered
        self._do_register_lazy_component(obj_type, obj_or_component_id)
        return build_reference(
            obj_type, self.openapi_version.major, obj_or_component_id
        )

    def schema(
        self,
        component_id: str,
        component: dict | None = None,
        *,
        lazy: bool = False,
        **kwargs: typing.Any,
    ) -> Components:
        """Add a new schema to the spec.

        :param str component_id: identifier by which schema may be referenced
        :param dict component: schema definition
        :param bool lazy: register component only when referenced in the spec
        :param kwargs: plugin-specific arguments

        .. note::

            If you are using `apispec.ext.marshmallow`, you can pass fields' metadata as
            additional keyword arguments.

            For example, to add ``enum`` and ``description`` to your field: ::

                status = fields.String(
                    required=True,
                    metadata={
                        "description": "Status (open or closed)",
                        "enum": ["open", "closed"],
                    },
                )

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject
        """
        if component_id in self.schemas:
            raise DuplicateComponentNameError(
                f'Another schema with name "{component_id}" is already registered.'
            )
        ret = deepcopy(component) or {}
        # Execute all helpers from plugins
        for plugin in self._plugins:
            try:
                ret.update(plugin.schema_helper(component_id, ret, **kwargs) or {})
            except PluginMethodNotImplementedError:
                continue
        self._resolve_refs_in_schema(ret)
        self._register_component("schema", component_id, ret, lazy=lazy)
        return self

    def response(
        self,
        component_id: str,
        component: dict | None = None,
        *,
        lazy: bool = False,
        **kwargs: typing.Any,
    ) -> Components:
        """Add a response which can be referenced.

        :param str component_id: ref_id to use as reference
        :param dict component: response fields
        :param bool lazy: register component only when referenced in the spec
        :param kwargs: plugin-specific arguments
        """
        if component_id in self.responses:
            raise DuplicateComponentNameError(
                f'Another response with name "{component_id}" is already registered.'
            )
        ret = deepcopy(component) or {}
        # Execute all helpers from plugins
        for plugin in self._plugins:
            try:
                ret.update(plugin.response_helper(ret, **kwargs) or {})
            except PluginMethodNotImplementedError:
                continue
        self._resolve_refs_in_response(ret)
        self._register_component("response", component_id, ret, lazy=lazy)
        return self

    def parameter(
        self,
        component_id: str,
        location: str,
        component: dict | None = None,
        *,
        lazy: bool = False,
        **kwargs: typing.Any,
    ) -> Components:
        """Add a parameter which can be referenced.

        :param str component_id: identifier by which parameter may be referenced
        :param str location: location of the parameter
        :param dict component: parameter fields
        :param bool lazy: register component only when referenced in the spec
        :param kwargs: plugin-specific arguments
        """
        if component_id in self.parameters:
            raise DuplicateComponentNameError(
                f'Another parameter with name "{component_id}" is already registered.'
            )
        ret = deepcopy(component) or {}
        ret.setdefault("name", component_id)
        ret["in"] = location

        # if "in" is set to "path", enforce required flag to True
        if location == "path":
            ret["required"] = True

        # Execute all helpers from plugins
        for plugin in self._plugins:
            try:
                ret.update(plugin.parameter_helper(ret, **kwargs) or {})
            except PluginMethodNotImplementedError:
                continue
        self._resolve_refs_in_parameter_or_header(ret)
        self._register_component("parameter", component_id, ret, lazy=lazy)
        return self

    def header(
        self,
        component_id: str,
        component: dict,
        *,
        lazy: bool = False,
        **kwargs: typing.Any,
    ) -> Components:
        """Add a header which can be referenced.

        :param str component_id: identifier by which header may be referenced
        :param dict component: header fields
        :param bool lazy: register component only when referenced in the spec
        :param kwargs: plugin-specific arguments

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.1.md#headerObject
        """
        ret = deepcopy(component) or {}
        if component_id in self.headers:
            raise DuplicateComponentNameError(
                f'Another header with name "{component_id}" is already registered.'
            )
        # Execute all helpers from plugins
        for plugin in self._plugins:
            try:
                ret.update(plugin.header_helper(ret, **kwargs) or {})
            except PluginMethodNotImplementedError:
                continue
        self._resolve_refs_in_parameter_or_header(ret)
        self._register_component("header", component_id, ret, lazy=lazy)
        return self

    def example(
        self, component_id: str, component: dict, *, lazy: bool = False
    ) -> Components:
        """Add an example which can be referenced

        :param str component_id: identifier by which example may be referenced
        :param dict component: example fields
        :param bool lazy: register component only when referenced in the spec

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.1.md#exampleObject
        """
        if component_id in self.examples:
            raise DuplicateComponentNameError(
                f'Another example with name "{component_id}" is already registered.'
            )
        self._register_component("example", component_id, component, lazy=lazy)
        return self

    def security_scheme(self, component_id: str, component: dict) -> Components:
        """Add a security scheme which can be referenced.

        :param str component_id: component_id to use as reference
        :param dict component: security scheme fields
        """
        if component_id in self.security_schemes:
            raise DuplicateComponentNameError(
                f'Another security scheme with name "{component_id}" is already registered.'
            )
        self._register_component("security_scheme", component_id, component)
        return self

    def _resolve_schema(self, obj) -> None:
        """Replace schema reference as string with a $ref if needed

        Also resolve references in the schema
        """
        if "schema" in obj:
            obj["schema"] = self.get_ref("schema", obj["schema"])
            self._resolve_refs_in_schema(obj["schema"])

    def _resolve_examples(self, obj) -> None:
        """Replace example reference as string with a $ref"""
        for name, example in obj.get("examples", {}).items():
            obj["examples"][name] = self.get_ref("example", example)

    def _resolve_refs_in_schema(self, schema: dict) -> None:
        if "properties" in schema:
            for key in schema["properties"]:
                schema["properties"][key] = self.get_ref(
                    "schema", schema["properties"][key]
                )
                self._resolve_refs_in_schema(schema["properties"][key])
        if "items" in schema:
            schema["items"] = self.get_ref("schema", schema["items"])
            self._resolve_refs_in_schema(schema["items"])
        for key in ("allOf", "oneOf", "anyOf"):
            if key in schema:
                schema[key] = [self.get_ref("schema", s) for s in schema[key]]
                for sch in schema[key]:
                    self._resolve_refs_in_schema(sch)
        if "not" in schema:
            schema["not"] = self.get_ref("schema", schema["not"])
            self._resolve_refs_in_schema(schema["not"])

    def _resolve_refs_in_parameter_or_header(self, parameter_or_header) -> None:
        self._resolve_schema(parameter_or_header)
        self._resolve_examples(parameter_or_header)
        # parameter content is OpenAPI v3+
        for media_type in parameter_or_header.get("content", {}).values():
            self._resolve_schema(media_type)

    def _resolve_refs_in_request_body(self, request_body) -> None:
        # requestBody is OpenAPI v3+
        for media_type in request_body["content"].values():
            self._resolve_schema(media_type)
            self._resolve_examples(media_type)

    def _resolve_refs_in_response(self, response) -> None:
        if self.openapi_version.major < 3:
            self._resolve_schema(response)
        else:
            for media_type in response.get("content", {}).values():
                self._resolve_schema(media_type)
                self._resolve_examples(media_type)
            for name, header in response.get("headers", {}).items():
                response["headers"][name] = self.get_ref("header", header)
                self._resolve_refs_in_parameter_or_header(response["headers"][name])
            # TODO: Resolve link refs when Components supports links

    def _resolve_refs_in_operation(self, operation) -> None:
        if "parameters" in operation:
            parameters = []
            for parameter in operation["parameters"]:
                parameter = self.get_ref("parameter", parameter)
                self._resolve_refs_in_parameter_or_header(parameter)
                parameters.append(parameter)
            operation["parameters"] = parameters
        if "callbacks" in operation:
            for callback in operation["callbacks"].values():
                if isinstance(callback, dict):
                    for path in callback.values():
                        self.resolve_refs_in_path(path)
        if "requestBody" in operation:
            self._resolve_refs_in_request_body(operation["requestBody"])
        if "responses" in operation:
            responses = {}
            for code, response in operation["responses"].items():
                response = self.get_ref("response", response)
                self._resolve_refs_in_response(response)
                responses[code] = response
            operation["responses"] = responses

    def resolve_refs_in_path(self, path) -> None:
        if "parameters" in path:
            parameters = []
            for parameter in path["parameters"]:
                parameter = self.get_ref("parameter", parameter)
                self._resolve_refs_in_parameter_or_header(parameter)
                parameters.append(parameter)
            path["parameters"] = parameters
        for method in (
            "get",
            "put",
            "post",
            "delete",
            "options",
            "head",
            "patch",
            "trace",
        ):
            if method in path:
                self._resolve_refs_in_operation(path[method])


class APISpec:
    """Stores metadata that describes a RESTful API using the OpenAPI specification.

    :param str title: API title
    :param str version: API version
    :param list|tuple plugins: Plugin instances.
        See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#infoObject
    :param str openapi_version: OpenAPI Specification version.
        Should be in the form '2.x' or '3.x.x' to comply with the OpenAPI standard.
    :param options: Optional top-level keys
        See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#openapi-object
    """

    def __init__(
        self,
        title: str,
        version: str,
        openapi_version: str,
        plugins: Sequence[BasePlugin] = (),
        **options: typing.Any,
    ) -> None:
        self.title = title
        self.version = version
        self.options = options
        self.plugins = plugins
        self.openapi_version = Version(openapi_version)
        if not (
            MIN_INCLUSIVE_OPENAPI_VERSION
            <= self.openapi_version
            < MAX_EXCLUSIVE_OPENAPI_VERSION
        ):
            raise APISpecError(f"Not a valid OpenAPI version number: {openapi_version}")

        # Metadata
        self._tags: list[dict] = []
        self._paths: dict = {}

        # Components
        self.components = Components(self.plugins, self.openapi_version)

        # Plugins
        for plugin in self.plugins:
            plugin.init_spec(self)

    def to_dict(self) -> dict[str, typing.Any]:
        ret: dict[str, typing.Any] = {
            "paths": self._paths,
            "info": {"title": self.title, "version": self.version},
        }
        if self._tags:
            ret["tags"] = self._tags
        if self.openapi_version.major < 3:
            ret["swagger"] = str(self.openapi_version)
            ret.update(self.components.to_dict())
        else:
            ret["openapi"] = str(self.openapi_version)
            components_dict = self.components.to_dict()
            if components_dict:
                ret["components"] = components_dict
        ret = deepupdate(ret, self.options)
        return ret

    def to_yaml(self, yaml_dump_kwargs: typing.Any | None = None) -> str:
        """Render the spec to YAML. Requires PyYAML to be installed.

        :param dict yaml_dump_kwargs: Additional keyword arguments to pass to `yaml.dump`
        """
        from .yaml_utils import dict_to_yaml

        return dict_to_yaml(self.to_dict(), yaml_dump_kwargs)

    def tag(self, tag: dict) -> APISpec:
        """Store information about a tag.

        :param dict tag: the dictionary storing information about the tag.
        """
        self._tags.append(tag)
        return self

    def path(
        self,
        path: str | None = None,
        *,
        operations: dict[str, typing.Any] | None = None,
        summary: str | None = None,
        description: str | None = None,
        parameters: list[dict] | None = None,
        **kwargs: typing.Any,
    ) -> APISpec:
        """Add a new path object to the spec.

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#path-item-object

        :param str|None path: URL path component
        :param dict|None operations: describes the http methods and options for `path`
        :param str summary: short summary relevant to all operations in this path
        :param str description: long description relevant to all operations in this path
        :param list|None parameters: list of parameters relevant to all operations in this path
        :param kwargs: parameters used by any path helpers see :meth:`register_path_helper`
        """
        # operations and parameters must be deepcopied because they are mutated
        # in _clean_operations and operation helpers and path may be called twice
        operations = deepcopy(operations) or {}
        parameters = deepcopy(parameters) or []

        # Execute path helpers
        for plugin in self.plugins:
            try:
                ret = plugin.path_helper(
                    path=path, operations=operations, parameters=parameters, **kwargs
                )
            except PluginMethodNotImplementedError:
                continue
            if ret is not None:
                path = ret
        if not path:
            raise APISpecError("Path template is not specified.")

        # Execute operation helpers
        for plugin in self.plugins:
            try:
                plugin.operation_helper(path=path, operations=operations, **kwargs)
            except PluginMethodNotImplementedError:
                continue

        self._clean_operations(operations)

        self._paths.setdefault(path, operations).update(operations)
        if summary is not None:
            self._paths[path]["summary"] = summary
        if description is not None:
            self._paths[path]["description"] = description
        if parameters:
            parameters = self._clean_parameters(parameters)
            self._paths[path]["parameters"] = parameters

        self.components.resolve_refs_in_path(self._paths[path])

        return self

    def _clean_parameters(
        self,
        parameters: list[dict],
    ) -> list[dict]:
        """Ensure that all parameters with "in" equal to "path" are also required
        as required by the OpenAPI specification, as well as normalizing any
        references to global parameters and checking for duplicates parameters

        See https ://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#parameterObject.

        :param list parameters: List of parameters mapping
        """
        seen = set()
        for parameter in [p for p in parameters if isinstance(p, dict)]:
            # check missing name / location
            missing_attrs = [attr for attr in ("name", "in") if attr not in parameter]
            if missing_attrs:
                raise InvalidParameterError(
                    f"Missing keys {missing_attrs} for parameter"
                )

            # OpenAPI Spec 3 and 2 don't allow for duplicated parameters
            # A unique parameter is defined by a combination of a name and location
            unique_key = (parameter["name"], parameter["in"])
            if unique_key in seen:
                raise DuplicateParameterError(
                    "Duplicate parameter with name {} and location {}".format(
                        parameter["name"], parameter["in"]
                    )
                )
            seen.add(unique_key)

            # Add "required" attribute to path parameters
            if parameter["in"] == "path":
                parameter["required"] = True

        return parameters

    def _clean_operations(
        self,
        operations: dict[str, dict],
    ) -> None:
        """Ensure that all parameters with "in" equal to "path" are also required
        as required by the OpenAPI specification, as well as normalizing any
        references to global parameters. Also checks for invalid HTTP methods.

        See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#parameterObject.

        :param dict operations: Dict mapping status codes to operations
        """
        operation_names = set(operations)
        valid_methods = set(VALID_METHODS[self.openapi_version.major])
        invalid = {
            key for key in operation_names - valid_methods if not key.startswith("x-")
        }
        if invalid:
            raise APISpecError(
                "One or more HTTP methods are invalid: {}".format(", ".join(invalid))
            )

        for operation in (operations or {}).values():
            if "parameters" in operation:
                operation["parameters"] = self._clean_parameters(
                    operation["parameters"]
                )
            if "responses" in operation:
                responses = {}
                for code, response in operation["responses"].items():
                    try:
                        code = int(code)  # handles IntEnums like http.HTTPStatus
                    except (TypeError, ValueError):
                        if self.openapi_version.major < 3 and code != "default":
                            warnings.warn("Non-integer code not allowed in OpenAPI < 3")
                    responses[str(code)] = response
                operation["responses"] = responses
