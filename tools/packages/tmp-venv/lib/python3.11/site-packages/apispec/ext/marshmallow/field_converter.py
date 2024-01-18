"""Utilities for generating OpenAPI Specification (fka Swagger) entities from
:class:`Fields <marshmallow.fields.Field>`.

.. warning::

    This module is treated as private API.
    Users should not need to use this module directly.
"""
from __future__ import annotations
import re
import functools
import operator
import typing
import warnings
from packaging.version import Version

import marshmallow
from marshmallow.orderedset import OrderedSet


# marshmallow field => (JSON Schema type, format)
DEFAULT_FIELD_MAPPING: dict[type, tuple[str | None, str | None]] = {
    marshmallow.fields.Integer: ("integer", None),
    marshmallow.fields.Number: ("number", None),
    marshmallow.fields.Float: ("number", None),
    marshmallow.fields.Decimal: ("number", None),
    marshmallow.fields.String: ("string", None),
    marshmallow.fields.Boolean: ("boolean", None),
    marshmallow.fields.UUID: ("string", "uuid"),
    marshmallow.fields.DateTime: ("string", "date-time"),
    marshmallow.fields.Date: ("string", "date"),
    marshmallow.fields.Time: ("string", None),
    marshmallow.fields.TimeDelta: ("integer", None),
    marshmallow.fields.Email: ("string", "email"),
    marshmallow.fields.URL: ("string", "url"),
    marshmallow.fields.Dict: ("object", None),
    marshmallow.fields.Field: (None, None),
    marshmallow.fields.Raw: (None, None),
    marshmallow.fields.List: ("array", None),
}


# Properties that may be defined in a field's metadata that will be added to the output
# of field2property
# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject
_VALID_PROPERTIES = {
    "format",
    "title",
    "description",
    "default",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "maxLength",
    "minLength",
    "pattern",
    "maxItems",
    "minItems",
    "uniqueItems",
    "maxProperties",
    "minProperties",
    "required",
    "enum",
    "type",
    "items",
    "allOf",
    "oneOf",
    "anyOf",
    "not",
    "properties",
    "additionalProperties",
    "readOnly",
    "writeOnly",
    "xml",
    "externalDocs",
    "example",
    "nullable",
    "deprecated",
}


_VALID_PREFIX = "x-"


class FieldConverterMixin:
    """Adds methods for converting marshmallow fields to an OpenAPI properties."""

    field_mapping: dict[type, tuple[str | None, str | None]] = DEFAULT_FIELD_MAPPING
    openapi_version: Version

    def init_attribute_functions(self):
        self.attribute_functions = [
            # self.field2type_and_format should run first
            # as other functions may rely on its output
            self.field2type_and_format,
            self.field2default,
            self.field2choices,
            self.field2read_only,
            self.field2write_only,
            self.field2nullable,
            self.field2range,
            self.field2length,
            self.field2pattern,
            self.metadata2properties,
            self.enum2properties,
            self.nested2properties,
            self.pluck2properties,
            self.list2properties,
            self.dict2properties,
            self.timedelta2properties,
            self.datetime2properties,
        ]

    def map_to_openapi_type(self, field_cls, *args):
        """Set mapping for custom field class.

        :param type field_cls: Field class to set mapping for.

        ``*args`` can be:

        - a pair of the form ``(type, format)``
        - a core marshmallow field type (in which case we reuse that type's mapping)
        """
        if len(args) == 1 and args[0] in self.field_mapping:
            openapi_type_field = self.field_mapping[args[0]]
        elif len(args) == 2:
            openapi_type_field = args
        else:
            raise TypeError("Pass core marshmallow field type or (type, fmt) pair.")

        self.field_mapping[field_cls] = openapi_type_field

    def add_attribute_function(self, func):
        """Method to add an attribute function to the list of attribute functions
        that will be called on a field to convert it from a field to an OpenAPI
        property.

        :param func func: the attribute function to add
            The attribute function will be bound to the
            `OpenAPIConverter <apispec.ext.marshmallow.openapi.OpenAPIConverter>`
            instance.
            It will be called for each field in a schema with
            `self <apispec.ext.marshmallow.openapi.OpenAPIConverter>` and a
            `field <marshmallow.fields.Field>` instance
            positional arguments and `ret <dict>` keyword argument.
            Must return a dictionary of OpenAPI properties that will be shallow
            merged with the return values of all other attribute functions called on the field.
            User added attribute functions will be called after all built-in attribute
            functions in the order they were added. The merged results of all
            previously called attribute functions are accessible via the `ret`
            argument.
        """
        bound_func = func.__get__(self)
        setattr(self, func.__name__, bound_func)
        self.attribute_functions.append(bound_func)

    def field2property(self, field: marshmallow.fields.Field) -> dict:
        """Return the JSON Schema property definition given a marshmallow
        :class:`Field <marshmallow.fields.Field>`.

        Will include field metadata that are valid properties of OpenAPI schema objects
        (e.g. "description", "enum", "example").

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject

        :param Field field: A marshmallow field.
        :rtype: dict, a Property Object
        """
        ret: dict = {}

        for attr_func in self.attribute_functions:
            ret.update(attr_func(field, ret=ret))

        return ret

    def field2type_and_format(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI type and format based on the field type.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        # If this type isn't directly in the field mapping then check the
        # hierarchy until we find something that does.
        for field_class in type(field).__mro__:
            if field_class in self.field_mapping:
                type_, fmt = self.field_mapping[field_class]
                break
        else:
            warnings.warn(
                "Field of type {} does not inherit from marshmallow.Field.".format(
                    type(field)
                ),
                UserWarning,
            )
            type_, fmt = "string", None

        ret = {}
        if type_:
            ret["type"] = type_
        if fmt:
            ret["format"] = fmt

        return ret

    def field2default(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary containing the field's default value.

        Will first look for a `default` key in the field's metadata and then
        fall back on the field's `missing` parameter. A callable passed to the
        field's missing parameter will be ignored.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if "default" in field.metadata:
            ret["default"] = field.metadata["default"]
        else:
            default = field.load_default
            if default is not marshmallow.missing and not callable(default):
                default = field._serialize(default, None, None)
                ret["default"] = default
        return ret

    def field2choices(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI field attributes for valid choices definition.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        attributes = {}

        comparable = [
            validator.comparable
            for validator in field.validators
            if hasattr(validator, "comparable")
        ]
        if comparable:
            attributes["enum"] = comparable
        else:
            choices = [
                OrderedSet(validator.choices)
                for validator in field.validators
                if hasattr(validator, "choices")
            ]
            if choices:
                attributes["enum"] = list(functools.reduce(operator.and_, choices))

        return attributes

    def field2read_only(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI field attributes for a dump_only field.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        attributes = {}
        if field.dump_only:
            attributes["readOnly"] = True
        return attributes

    def field2write_only(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI field attributes for a load_only field.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        attributes = {}
        if field.load_only and self.openapi_version.major >= 3:
            attributes["writeOnly"] = True
        return attributes

    def field2nullable(self, field: marshmallow.fields.Field, ret) -> dict:
        """Return the dictionary of OpenAPI field attributes for a nullable field.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        attributes: dict = {}
        if field.allow_none:
            if self.openapi_version.major < 3:
                attributes["x-nullable"] = True
            elif self.openapi_version.minor < 1:
                attributes["nullable"] = True
            else:
                attributes["type"] = [*make_type_list(ret.get("type")), "null"]
        return attributes

    def field2range(self, field: marshmallow.fields.Field, ret) -> dict:
        """Return the dictionary of OpenAPI field attributes for a set of
        :class:`Range <marshmallow.validators.Range>` validators.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        validators = [
            validator
            for validator in field.validators
            if (
                hasattr(validator, "min")
                and hasattr(validator, "max")
                and not hasattr(validator, "equal")
            )
        ]

        min_attr, max_attr = (
            ("minimum", "maximum")
            if set(make_type_list(ret.get("type"))) & {"number", "integer"}
            else ("x-minimum", "x-maximum")
        )

        # Serialize min/max values with the field to which the validator is applied
        return {
            k: field._serialize(v, None, None)
            for k, v in make_min_max_attributes(validators, min_attr, max_attr).items()
        }

    def field2length(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI field attributes for a set of
        :class:`Length <marshmallow.validators.Length>` validators.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        validators = [
            validator
            for validator in field.validators
            if (
                hasattr(validator, "min")
                and hasattr(validator, "max")
                and hasattr(validator, "equal")
            )
        ]

        is_array = isinstance(
            field, (marshmallow.fields.Nested, marshmallow.fields.List)
        )
        min_attr = "minItems" if is_array else "minLength"
        max_attr = "maxItems" if is_array else "maxLength"

        equal_list = [
            validator.equal for validator in validators if validator.equal is not None
        ]
        if equal_list:
            return {min_attr: equal_list[0], max_attr: equal_list[0]}

        return make_min_max_attributes(validators, min_attr, max_attr)

    def field2pattern(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return the dictionary of OpenAPI field attributes for a
        :class:`Regexp <marshmallow.validators.Regexp>` validator.

        If there is more than one such validator, only the first
        is used in the output spec.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        regex_validators = (
            v
            for v in field.validators
            if isinstance(getattr(v, "regex", None), re.Pattern)
        )
        v = next(regex_validators, None)
        attributes = {} if v is None else {"pattern": v.regex.pattern}  # type:ignore

        if next(regex_validators, None) is not None:
            warnings.warn(
                "More than one regex validator defined on {} field. Only the "
                "first one will be used in the output spec.".format(type(field)),
                UserWarning,
            )

        return attributes

    def metadata2properties(
        self, field: marshmallow.fields.Field, **kwargs: typing.Any
    ) -> dict:
        """Return a dictionary of properties extracted from field metadata.

        Will include field metadata that are valid properties of `OpenAPI schema
        objects
        <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject>`_
        (e.g. "description", "enum", "example").

        In addition, `specification extensions
        <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#specification-extensions>`_
        are supported.  Prefix `x_` to the desired extension when passing the
        keyword argument to the field constructor. apispec will convert `x_` to
        `x-` to comply with OpenAPI.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        # Dasherize metadata that starts with x_
        metadata = {
            key.replace("_", "-") if key.startswith("x_") else key: value
            for key, value in field.metadata.items()
            if isinstance(key, str)
        }

        # Avoid validation error with "Additional properties not allowed"
        ret = {
            key: value
            for key, value in metadata.items()
            if key in _VALID_PROPERTIES or key.startswith(_VALID_PREFIX)
        }
        return ret

    def nested2properties(self, field: marshmallow.fields.Field, ret) -> dict:
        """Return a dictionary of properties from :class:`Nested <marshmallow.fields.Nested` fields.

        Typically provides a reference object and will add the schema to the spec
        if it is not already present
        If a custom `schema_name_resolver` function returns `None` for the nested
        schema a JSON schema object will be returned

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        # Pluck is a subclass of Nested but is in essence a single field; it
        # is treated separately by pluck2properties.
        if isinstance(field, marshmallow.fields.Nested) and not isinstance(
            field, marshmallow.fields.Pluck
        ):
            schema_dict = self.resolve_nested_schema(field.schema)  # type:ignore
            if ret and "$ref" in schema_dict:
                ret.update({"allOf": [schema_dict]})
            else:
                ret.update(schema_dict)
        return ret

    def pluck2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`Pluck <marshmallow.fields.Pluck` fields.

        Pluck effectively trans-includes a field from another schema into this,
        possibly wrapped in an array (`many=True`).

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        if isinstance(field, marshmallow.fields.Pluck):
            plucked_field = field.schema.fields[field.field_name]
            ret = self.field2property(plucked_field)
            return {"type": "array", "items": ret} if field.many else ret
        return {}

    def list2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`List <marshmallow.fields.List>` fields.

        Will provide an `items` property based on the field's `inner` attribute

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if isinstance(field, marshmallow.fields.List):
            ret["items"] = self.field2property(field.inner)
        return ret

    def dict2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`Dict <marshmallow.fields.Dict>` fields.

        Only applicable for Marshmallow versions greater than 3. Will provide an
        `additionalProperties` property based on the field's `value_field` attribute

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if isinstance(field, marshmallow.fields.Dict):
            value_field = field.value_field
            if value_field:
                ret["additionalProperties"] = self.field2property(value_field)
        return ret

    def timedelta2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`TimeDelta <marshmallow.fields.TimeDelta>` fields.

        Adds a `x-unit` vendor property based on the field's `precision` attribute

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if isinstance(field, marshmallow.fields.TimeDelta):
            ret["x-unit"] = field.precision
        return ret

    def enum2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`Enum <marshmallow.fields.Enum` fields.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if isinstance(field, marshmallow.fields.Enum):
            ret = self.field2property(field.field)
            if field.by_value is False:
                choices = (m for m in field.enum.__members__)
            else:
                choices = (m.value for m in field.enum)
            ret["enum"] = [field.field._serialize(v, None, None) for v in choices]
        return ret

    def datetime2properties(self, field, **kwargs: typing.Any) -> dict:
        """Return a dictionary of properties from :class:`DateTime <marshmallow.fields.DateTime` fields.

        :param Field field: A marshmallow field.
        :rtype: dict
        """
        ret = {}
        if isinstance(field, marshmallow.fields.DateTime) and not isinstance(
            field, marshmallow.fields.Date
        ):
            if field.format == "iso" or field.format is None:
                # Will return { "type": "string", "format": "date-time" }
                # as specified inside DEFAULT_FIELD_MAPPING
                pass
            elif field.format == "rfc":
                ret = {
                    "type": "string",
                    "format": None,
                    "example": "Wed, 02 Oct 2002 13:00:00 GMT",
                    "pattern": r"((Mon|Tue|Wed|Thu|Fri|Sat|Sun), ){0,1}\d{2} "
                    + r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} "
                    + r"(UT|GMT|EST|EDT|CST|CDT|MST|MDT|PST|PDT|(Z|A|M|N)|(\+|-)\d{4})",
                }
            elif field.format == "timestamp":
                ret = {
                    "type": "number",
                    "format": "float",
                    "example": "1676451245.596",
                    "min": "0",
                }
            elif field.format == "timestamp_ms":
                ret = {
                    "type": "number",
                    "format": "float",
                    "example": "1676451277514.654",
                    "min": "0",
                }
            else:
                ret = {
                    "type": "string",
                    "format": None,
                    "pattern": field.metadata["pattern"]
                    if field.metadata.get("pattern")
                    else None,
                }
        return ret


def make_type_list(types):
    """Return a list of types from a type attribute

    Since OpenAPI 3.1.0, "type" can be a single type as string or a list of
    types, including 'null'. This function takes a "type" attribute as input
    and returns it as a list, be it an empty or single-element list.
    This is useful to factorize type-conditional code or code adding a type.
    """
    if types is None:
        return []
    if isinstance(types, str):
        return [types]
    return types


def make_min_max_attributes(validators, min_attr, max_attr) -> dict:
    """Return a dictionary of minimum and maximum attributes based on a list
    of validators. If either minimum or maximum values are not present in any
    of the validator objects that attribute will be omitted.

    :param validators list: A list of `Marshmallow` validator objects. Each
        objct is inspected for a minimum and maximum values
    :param min_attr string: The OpenAPI attribute for the minimum value
    :param max_attr string: The OpenAPI attribute for the maximum value
    """
    attributes = {}
    min_list = [validator.min for validator in validators if validator.min is not None]
    max_list = [validator.max for validator in validators if validator.max is not None]
    if min_list:
        attributes[min_attr] = max(min_list)
    if max_list:
        attributes[max_attr] = min(max_list)
    return attributes
