"""marshmallow plugin for apispec. Allows passing a marshmallow
`Schema` to `spec.components.schema <apispec.core.Components.schema>`,
`spec.components.parameter <apispec.core.Components.parameter>`,
`spec.components.response <apispec.core.Components.response>`
(for response and headers schemas) and
`spec.path <apispec.APISpec.path>` (for responses and response headers).

Requires marshmallow>=3.13.0.

``MarshmallowPlugin`` maps marshmallow ``Field`` classes with OpenAPI types and
formats.

It inspects field attributes to automatically document properties
such as read/write-only, range and length constraints, etc.

OpenAPI properties can also be passed as metadata to the ``Field`` instance
if they can't be inferred from the field attributes (`description`,...), or to
override automatic documentation (`readOnly`,...). A metadata attribute is used
in the documentation either if it is a valid OpenAPI property, or if it starts
with `"x-"` (vendor extension).

.. warning::

    ``MarshmallowPlugin`` infers the ``default`` property from the
    ``load_default`` attribute of the ``Field`` (unless ``load_default`` is a
    callable). Since default values are entered in deserialized form,
    the value displayed in the doc is serialized by the ``Field`` instance.
    This may lead to inaccurate documentation in very specific cases.
    The default value to display in the documentation can be
    specified explicitly by passing ``default`` as field metadata.

::

    from pprint import pprint
    import datetime as dt

    from apispec import APISpec
    from apispec.ext.marshmallow import MarshmallowPlugin
    from marshmallow import Schema, fields

    spec = APISpec(
        title="Example App",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()],
    )


    class UserSchema(Schema):
        id = fields.Int(dump_only=True)
        name = fields.Str(metadata={"description": "The user's name"})
        created = fields.DateTime(
            dump_only=True,
            dump_default=dt.datetime.utcnow,
            metadata={"default": "The current datetime"}
        )


    spec.components.schema("User", schema=UserSchema)
    pprint(spec.to_dict()["components"]["schemas"])
    # {'User': {'properties': {'created': {'default': 'The current datetime',
    #                                      'format': 'date-time',
    #                                      'readOnly': True,
    #                                      'type': 'string'},
    #                          'id': {'readOnly': True,
    #                                 'type': 'integer'},
    #                          'name': {'description': "The user's name",
    #                                   'type': 'string'}},
    #           'type': 'object'}}

"""
# pyright: reportIncompatibleMethodOverride=false
from __future__ import annotations

import warnings
import typing
from packaging.version import Version

from marshmallow import Schema

from apispec import BasePlugin, APISpec
from .common import resolve_schema_instance, make_schema_key, resolve_schema_cls
from .openapi import OpenAPIConverter
from .schema_resolver import SchemaResolver


def resolver(schema: type[Schema]) -> str:
    """Default schema name resolver function that strips 'Schema' from the end of the class name."""
    resolved = resolve_schema_cls(schema)
    schema_cls = resolved[0] if isinstance(resolved, list) else resolved
    name = schema_cls.__name__
    if name.endswith("Schema"):
        name = name[:-6] or name
    return name.strip()


class MarshmallowPlugin(BasePlugin):
    """APISpec plugin for translating marshmallow schemas to OpenAPI/JSONSchema format.

    :param callable schema_name_resolver: Callable to generate the schema definition name.
        Receives the `Schema` class and returns the name to be used in refs within
        the generated spec. When working with circular referencing this function
        must must not return `None` for schemas in a circular reference chain.

        Example: ::

            from apispec.ext.marshmallow.common import resolve_schema_cls

            def schema_name_resolver(schema):
                schema_cls = resolve_schema_cls(schema)
                return schema_cls.__name__
    """

    Converter = OpenAPIConverter
    Resolver = SchemaResolver

    def __init__(
        self,
        schema_name_resolver: typing.Callable[[type[Schema]], str] | None = None,
    ) -> None:
        super().__init__()
        self.schema_name_resolver = schema_name_resolver or resolver
        self.spec: APISpec | None = None
        self.openapi_version: Version | None = None
        self.converter: OpenAPIConverter | None = None
        self.resolver: SchemaResolver | None = None

    def init_spec(self, spec: APISpec) -> None:
        super().init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        self.converter = self.Converter(
            openapi_version=spec.openapi_version,
            schema_name_resolver=self.schema_name_resolver,
            spec=spec,
        )
        self.resolver = self.Resolver(
            openapi_version=spec.openapi_version, converter=self.converter
        )

    def map_to_openapi_type(self, field_cls, *args):
        """Set mapping for custom field class.

        :param type field_cls: Field class to set mapping for.

        ``*args`` can be:

        - a pair of the form ``(type, format)``
        - a core marshmallow field type (in which case we reuse that type's mapping)

        Examples: ::

            # Override Integer mapping
            class Int32(Integer):
                # ...

            ma_plugin.map_to_openapi_type(Int32, 'string', 'int32')

            # Map to ('integer', None) like Integer
            class IntegerLike(Integer):
                # ...

            ma_plugin.map_to_openapi_type(IntegerLike, Integer)
        """
        assert self.converter is not None, "init_spec has not yet been called"
        return self.converter.map_to_openapi_type(field_cls, *args)

    def schema_helper(self, name, _, schema=None, **kwargs):
        """Definition helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` to provide OpenAPI
        metadata.

        :param type|Schema schema: A marshmallow Schema class or instance.
        """
        if schema is None:
            return None

        schema_instance = resolve_schema_instance(schema)

        schema_key = make_schema_key(schema_instance)
        self.warn_if_schema_already_in_spec(schema_key)
        assert self.converter is not None, "init_spec has not yet been called"
        self.converter.refs[schema_key] = name

        json_schema = self.converter.schema2jsonschema(schema_instance)

        return json_schema

    def parameter_helper(self, parameter, **kwargs):
        """Parameter component helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` in parameter definition.

        :param dict parameter: parameter fields. May contain a marshmallow
            Schema class or instance.
        """
        assert self.resolver is not None, "init_spec has not yet been called"
        self.resolver.resolve_schema(parameter)
        return parameter

    def response_helper(self, response, **kwargs):
        """Response component helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` in response definition.

        :param dict parameter: response fields. May contain a marshmallow
            Schema class or instance.
        """
        assert self.resolver is not None, "init_spec has not yet been called"
        self.resolver.resolve_response(response)
        return response

    def header_helper(self, header: dict, **kwargs: typing.Any):
        """Header component helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` in header definition.

        :param dict header: header fields. May contain a marshmallow
            Schema class or instance.
        """
        assert self.resolver  # needed for mypy
        self.resolver.resolve_schema(header)
        return header

    def operation_helper(
        self,
        path: str | None = None,
        operations: dict | None = None,
        **kwargs: typing.Any,
    ) -> None:
        assert self.resolver  # needed for mypy
        self.resolver.resolve_operations(operations)

    def warn_if_schema_already_in_spec(self, schema_key: tuple) -> None:
        """Method to warn the user if the schema has already been added to the
        spec.
        """
        assert self.converter  # needed for mypy
        if schema_key in self.converter.refs:
            warnings.warn(
                "{} has already been added to the spec. Adding it twice may "
                "cause references to not resolve properly.".format(schema_key[0]),
                UserWarning,
            )
