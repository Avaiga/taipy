from calendar import timegm
from decimal import Decimal as MyDecimal, ROUND_HALF_EVEN
from email.utils import formatdate
import six
try:
    from urlparse import urlparse, urlunparse
except ImportError:
    # python3
    from urllib.parse import urlparse, urlunparse
from flask_restful import marshal
from flask import url_for, request

__all__ = ["String", "FormattedString", "Url", "DateTime", "Float",
           "Integer", "Arbitrary", "Nested", "List", "Raw", "Boolean",
           "Fixed", "Price"]


class MarshallingException(Exception):
    """
    This is an encapsulating Exception in case of marshalling error.
    """

    def __init__(self, underlying_exception):
        # just put the contextual representation of the error to hint on what
        # went wrong without exposing internals
        super(MarshallingException, self).__init__(six.text_type(underlying_exception))


def is_indexable_but_not_string(obj):
    return not hasattr(obj, "strip") and hasattr(obj, "__iter__")


def get_value(key, obj, default=None):
    """Helper for pulling a keyed value off various types of objects"""
    if isinstance(key, int):
        return _get_value_for_key(key, obj, default)
    elif callable(key):
        return key(obj)
    else:
        return _get_value_for_keys(key.split('.'), obj, default)


def _get_value_for_keys(keys, obj, default):
    if len(keys) == 1:
        return _get_value_for_key(keys[0], obj, default)
    else:
        return _get_value_for_keys(
            keys[1:], _get_value_for_key(keys[0], obj, default), default)


def _get_value_for_key(key, obj, default):
    if is_indexable_but_not_string(obj):
        try:
            return obj[key]
        except (IndexError, TypeError, KeyError):
            pass
    return getattr(obj, key, default)


def to_marshallable_type(obj):
    """Helper for converting an object to a dictionary only if it is not
    dictionary already or an indexable object nor a simple type"""
    if obj is None:
        return None  # make it idempotent for None

    if hasattr(obj, '__marshallable__'):
        return obj.__marshallable__()

    if hasattr(obj, '__getitem__'):
        return obj  # it is indexable it is ok

    return dict(obj.__dict__)


class Raw(object):
    """Raw provides a base field class from which others should extend. It
    applies no formatting by default, and should only be used in cases where
    data does not need to be formatted before being serialized. Fields should
    throw a :class:`MarshallingException` in case of parsing problem.

    :param default: The default value for the field, if no value is
        specified.
    :param attribute: If the public facing value differs from the internal
        value, use this to retrieve a different attribute from the response
        than the publicly named value.
    """

    def __init__(self, default=None, attribute=None):
        self.attribute = attribute
        self.default = default

    def format(self, value):
        """Formats a field's value. No-op by default - field classes that
        modify how the value of existing object keys should be presented should
        override this and apply the appropriate formatting.

        :param value: The value to format
        :exception MarshallingException: In case of formatting problem

        Ex::

            class TitleCase(Raw):
                def format(self, value):
                    return unicode(value).title()
        """
        return value

    def output(self, key, obj):
        """Pulls the value for the given key from the object, applies the
        field's formatting and returns the result. If the key is not found
        in the object, returns the default value. Field classes that create
        values which do not require the existence of the key in the object
        should override this and return the desired value.

        :exception MarshallingException: In case of formatting problem
        """

        value = get_value(key if self.attribute is None else self.attribute, obj)

        if value is None:
            return self.default

        return self.format(value)


class Nested(Raw):
    """Allows you to nest one set of fields inside another.
    See :ref:`nested-field` for more information

    :param dict nested: The dictionary to nest
    :param bool allow_null: Whether to return None instead of a dictionary
        with null keys, if a nested dictionary has all-null keys
    :param kwargs: If ``default`` keyword argument is present, a nested
        dictionary will be marshaled as its value if nested dictionary is
        all-null keys (e.g. lets you return an empty JSON object instead of
        null)
    """

    def __init__(self, nested, allow_null=False, **kwargs):
        self.nested = nested
        self.allow_null = allow_null
        super(Nested, self).__init__(**kwargs)

    def output(self, key, obj):
        value = get_value(key if self.attribute is None else self.attribute, obj)
        if value is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default

        return marshal(value, self.nested)


class List(Raw):
    """
    Field for marshalling lists of other fields.

    See :ref:`list-field` for more information.

    :param cls_or_instance: The field type the list will contain.
    """

    def __init__(self, cls_or_instance, **kwargs):
        super(List, self).__init__(**kwargs)
        error_msg = ("The type of the list elements must be a subclass of "
                     "flask_restful.fields.Raw")
        if isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, Raw):
                raise MarshallingException(error_msg)
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, Raw):
                raise MarshallingException(error_msg)
            self.container = cls_or_instance

    def format(self, value):
        # Convert all instances in typed list to container type
        if isinstance(value, set):
            value = list(value)

        return [
            self.container.output(idx,
                val if (isinstance(val, dict)
                        or (self.container.attribute
                            and hasattr(val, self.container.attribute)))
                        and not isinstance(self.container, Nested)
                        and not type(self.container) is Raw
                    else value)
            for idx, val in enumerate(value)
        ]

    def output(self, key, data):
        value = get_value(key if self.attribute is None else self.attribute, data)
        # we cannot really test for external dict behavior
        if is_indexable_but_not_string(value) and not isinstance(value, dict):
            return self.format(value)

        if value is None:
            return self.default

        return [marshal(value, self.container.nested)]


class String(Raw):
    """
    Marshal a value as a string. Uses ``six.text_type`` so values will
    be converted to :class:`unicode` in python2 and :class:`str` in
    python3.
    """
    def format(self, value):
        try:
            return six.text_type(value)
        except ValueError as ve:
            raise MarshallingException(ve)


class Integer(Raw):
    """ Field for outputting an integer value.

    :param int default: The default value for the field, if no value is
        specified.
    """
    def __init__(self, default=0, **kwargs):
        super(Integer, self).__init__(default=default, **kwargs)

    def format(self, value):
        try:
            if value is None:
                return self.default
            return int(value)
        except ValueError as ve:
            raise MarshallingException(ve)


class Boolean(Raw):
    """
    Field for outputting a boolean value.

    Empty collections such as ``""``, ``{}``, ``[]``, etc. will be converted to
    ``False``.
    """
    def format(self, value):
        return bool(value)


class FormattedString(Raw):
    """
    FormattedString is used to interpolate other values from
    the response into this field. The syntax for the source string is
    the same as the string :meth:`~str.format` method from the python
    stdlib.

    Ex::

        fields = {
            'name': fields.String,
            'greeting': fields.FormattedString("Hello {name}")
        }
        data = {
            'name': 'Doug',
        }
        marshal(data, fields)
    """
    def __init__(self, src_str):
        """
        :param string src_str: the string to format with the other
        values from the response.
        """
        super(FormattedString, self).__init__()
        self.src_str = six.text_type(src_str)

    def output(self, key, obj):
        try:
            data = to_marshallable_type(obj)
            return self.src_str.format(**data)
        except (TypeError, IndexError) as error:
            raise MarshallingException(error)


class Url(Raw):
    """
    A string representation of a Url

    :param endpoint: Endpoint name. If endpoint is ``None``,
        ``request.endpoint`` is used instead
    :type endpoint: str
    :param absolute: If ``True``, ensures that the generated urls will have the
        hostname included
    :type absolute: bool
    :param scheme: URL scheme specifier (e.g. ``http``, ``https``)
    :type scheme: str
    """
    def __init__(self, endpoint=None, absolute=False, scheme=None, **kwargs):
        super(Url, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.absolute = absolute
        self.scheme = scheme

    def output(self, key, obj):
        try:
            data = to_marshallable_type(obj)
            endpoint = self.endpoint if self.endpoint is not None else request.endpoint
            o = urlparse(url_for(endpoint, _external=self.absolute, **data))
            if self.absolute:
                scheme = self.scheme if self.scheme is not None else o.scheme
                return urlunparse((scheme, o.netloc, o.path, "", "", ""))
            return urlunparse(("", "", o.path, "", "", ""))
        except TypeError as te:
            raise MarshallingException(te)


class Float(Raw):
    """
    A double as IEEE-754 double precision.
    ex : 3.141592653589793 3.1415926535897933e-06 3.141592653589793e+24 nan inf
    -inf
    """

    def format(self, value):
        try:
            return float(value)
        except ValueError as ve:
            raise MarshallingException(ve)


class Arbitrary(Raw):
    """
        A floating point number with an arbitrary precision
          ex: 634271127864378216478362784632784678324.23432
    """

    def format(self, value):
        return six.text_type(MyDecimal(value))


class DateTime(Raw):
    """
    Return a formatted datetime string in UTC. Supported formats are RFC 822
    and ISO 8601.

    See :func:`email.utils.formatdate` for more info on the RFC 822 format.

    See :meth:`datetime.datetime.isoformat` for more info on the ISO 8601
    format.

    :param dt_format: ``'rfc822'`` or ``'iso8601'``
    :type dt_format: str
    """
    def __init__(self, dt_format='rfc822', **kwargs):
        super(DateTime, self).__init__(**kwargs)
        self.dt_format = dt_format

    def format(self, value):
        try:
            if self.dt_format == 'rfc822':
                return _rfc822(value)
            elif self.dt_format == 'iso8601':
                return _iso8601(value)
            else:
                raise MarshallingException(
                    'Unsupported date format %s' % self.dt_format
                )
        except AttributeError as ae:
            raise MarshallingException(ae)

ZERO = MyDecimal()


class Fixed(Raw):
    """
    A decimal number with a fixed precision.
    """
    def __init__(self, decimals=5, **kwargs):
        super(Fixed, self).__init__(**kwargs)
        self.precision = MyDecimal('0.' + '0' * (decimals - 1) + '1')

    def format(self, value):
        dvalue = MyDecimal(value)
        if not dvalue.is_normal() and dvalue != ZERO:
            raise MarshallingException('Invalid Fixed precision number.')
        return six.text_type(dvalue.quantize(self.precision, rounding=ROUND_HALF_EVEN))


"""Alias for :class:`~fields.Fixed`"""
Price = Fixed


def _rfc822(dt):
    """Turn a datetime object into a formatted date.

    Example::

        fields._rfc822(datetime(2011, 1, 1)) => "Sat, 01 Jan 2011 00:00:00 -0000"

    :param dt: The datetime to transform
    :type dt: datetime
    :return: A RFC 822 formatted date string
    """
    return formatdate(timegm(dt.utctimetuple()))


def _iso8601(dt):
    """Turn a datetime object into an ISO8601 formatted date.

    Example::

        fields._iso8601(datetime(2012, 1, 1, 0, 0)) => "2012-01-01T00:00:00"

    :param dt: The datetime to transform
    :type dt: datetime
    :return: A ISO 8601 formatted date string
    """
    return dt.isoformat()
