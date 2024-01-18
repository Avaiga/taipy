from copy import deepcopy

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
from flask import current_app, request
from werkzeug.datastructures import MultiDict, FileStorage
from werkzeug import exceptions
import flask_restful
import decimal
import six


class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


_friendly_location = {
    u'json': u'the JSON body',
    u'form': u'the post body',
    u'args': u'the query string',
    u'values': u'the post body or the query string',
    u'headers': u'the HTTP headers',
    u'cookies': u'the request\'s cookies',
    u'files': u'an uploaded file',
}

text_type = lambda x: six.text_type(x)


class Argument(object):

    """
    :param name: Either a name or a list of option strings, e.g. foo or
        -f, --foo.
    :param default: The value produced if the argument is absent from the
        request.
    :param dest: The name of the attribute to be added to the object
        returned by :meth:`~reqparse.RequestParser.parse_args()`.
    :param bool required: Whether or not the argument may be omitted (optionals
        only).
    :param action: The basic type of action to be taken when this argument
        is encountered in the request. Valid options are "store" and "append".
    :param ignore: Whether to ignore cases where the argument fails type
        conversion
    :param type: The type to which the request argument should be
        converted. If a type raises an exception, the message in the
        error will be returned in the response. Defaults to :class:`unicode`
        in python2 and :class:`str` in python3.
    :param location: The attributes of the :class:`flask.Request` object
        to source the arguments from (ex: headers, args, etc.), can be an
        iterator. The last item listed takes precedence in the result set.
    :param choices: A container of the allowable values for the argument.
    :param help: A brief description of the argument, returned in the
        response when the argument is invalid. May optionally contain
        an "{error_msg}" interpolation token, which will be replaced with
        the text of the error raised by the type converter.
    :param bool case_sensitive: Whether argument values in the request are
        case sensitive or not (this will convert all values to lowercase)
    :param bool store_missing: Whether the arguments default value should
        be stored if the argument is missing from the request.
    :param bool trim: If enabled, trims whitespace around the argument.
    :param bool nullable: If enabled, allows null value in argument.
    """

    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=text_type, location=('json', 'values',),
                 choices=(), action='store', help=None, operators=('=',),
                 case_sensitive=True, store_missing=True, trim=False,
                 nullable=True):
        self.name = name
        self.default = default
        self.dest = dest
        self.required = required
        self.ignore = ignore
        self.location = location
        self.type = type
        self.choices = choices
        self.action = action
        self.help = help
        self.case_sensitive = case_sensitive
        self.operators = operators
        self.store_missing = store_missing
        self.trim = trim
        self.nullable = nullable

    def __str__(self):
        if len(self.choices) > 5:
            choices = self.choices[0:3]
            choices.append('...')
            choices.append(self.choices[-1])
        else:
            choices = self.choices
        return 'Name: {0}, type: {1}, choices: {2}'.format(self.name, self.type, choices)

    def __repr__(self):
        return "{0}('{1}', default={2}, dest={3}, required={4}, ignore={5}, location={6}, " \
               "type=\"{7}\", choices={8}, action='{9}', help={10}, case_sensitive={11}, " \
               "operators={12}, store_missing={13}, trim={14}, nullable={15})".format(
                self.__class__.__name__, self.name, self.default, self.dest, self.required, self.ignore, self.location,
                self.type, self.choices, self.action, self.help, self.case_sensitive,
                self.operators, self.store_missing, self.trim, self.nullable)

    def source(self, request):
        """Pulls values off the request in the provided location
        :param request: The flask request object to parse arguments from
        """
        if isinstance(self.location, six.string_types):
            value = getattr(request, self.location, MultiDict())
            if callable(value):
                value = value()
            if value is not None:
                return value
        else:
            values = MultiDict()
            for l in self.location:
                value = getattr(request, l, None)
                if callable(value):
                    value = value()
                if value is not None:
                    values.update(value)
            return values

        return MultiDict()

    def convert(self, value, op):
        # Don't cast None
        if value is None:
            if self.nullable:
                return None
            else:
                raise ValueError('Must not be null!')

        # and check if we're expecting a filestorage and haven't overridden `type`
        # (required because the below instantiation isn't valid for FileStorage)
        elif isinstance(value, FileStorage) and self.type == FileStorage:
            return value

        try:
            return self.type(value, self.name, op)
        except TypeError:
            try:
                if self.type is decimal.Decimal:
                    return self.type(str(value))
                else:
                    return self.type(value, self.name)
            except TypeError:
                return self.type(value)

    def handle_validation_error(self, error, bundle_errors):
        """Called when an error is raised while parsing. Aborts the request
        with a 400 status and an error message

        :param error: the error that was raised
        :param bundle_errors: do not abort when first error occurs, return a
            dict with the name of the argument and the error message to be
            bundled
        """
        error_str = six.text_type(error)
        error_msg = self.help.format(error_msg=error_str) if self.help else error_str
        msg = {self.name: error_msg}

        if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
            return error, msg
        flask_restful.abort(400, message=msg)

    def parse(self, request, bundle_errors=False):
        """Parses argument value(s) from the request, converting according to
        the argument's type.

        :param request: The flask request object to parse arguments from
        :param bundle_errors: Do not abort when first error occurs, return a
            dict with the name of the argument and the error message to be
            bundled
        """
        source = self.source(request)

        results = []

        # Sentinels
        _not_found = False
        _found = True

        for operator in self.operators:
            name = self.name + operator.replace("=", "", 1)
            if name in source:
                # Account for MultiDict and regular dict
                if hasattr(source, "getlist"):
                    values = source.getlist(name)
                else:
                    values = source.get(name)
                    if not (isinstance(values, MutableSequence) and self.action == 'append'):
                        values = [values]

                for value in values:
                    if hasattr(value, "strip") and self.trim:
                        value = value.strip()
                    if hasattr(value, "lower") and not self.case_sensitive:
                        value = value.lower()

                        if hasattr(self.choices, "__iter__"):
                            self.choices = [choice.lower()
                                            for choice in self.choices]

                    try:
                        value = self.convert(value, operator)
                    except Exception as error:
                        if self.ignore:
                            continue
                        return self.handle_validation_error(error, bundle_errors)

                    if self.choices and value not in self.choices:
                        if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
                            return self.handle_validation_error(
                                ValueError(u"{0} is not a valid choice".format(
                                    value)), bundle_errors)
                        self.handle_validation_error(
                                ValueError(u"{0} is not a valid choice".format(
                                    value)), bundle_errors)

                    if name in request.unparsed_arguments:
                        request.unparsed_arguments.pop(name)
                    results.append(value)

        if not results and self.required:
            if isinstance(self.location, six.string_types):
                error_msg = u"Missing required parameter in {0}".format(
                    _friendly_location.get(self.location, self.location)
                )
            else:
                friendly_locations = [_friendly_location.get(loc, loc)
                                      for loc in self.location]
                error_msg = u"Missing required parameter in {0}".format(
                    ' or '.join(friendly_locations)
                )
            if current_app.config.get("BUNDLE_ERRORS", False) or bundle_errors:
                return self.handle_validation_error(ValueError(error_msg), bundle_errors)
            self.handle_validation_error(ValueError(error_msg), bundle_errors)

        if not results:
            if callable(self.default):
                return self.default(), _not_found
            else:
                return self.default, _not_found

        if self.action == 'append':
            return results, _found

        if self.action == 'store' or len(results) == 1:
            return results[0], _found
        return results, _found


class RequestParser(object):
    """Enables adding and parsing of multiple arguments in the context of a
    single request. Ex::

        from flask_restful import reqparse

        parser = reqparse.RequestParser()
        parser.add_argument('foo')
        parser.add_argument('int_bar', type=int)
        args = parser.parse_args()

    :param bool trim: If enabled, trims whitespace on all arguments in this
        parser
    :param bool bundle_errors: If enabled, do not abort when first error occurs,
        return a dict with the name of the argument and the error message to be
        bundled and return all validation errors
    """

    def __init__(self, argument_class=Argument, namespace_class=Namespace,
                 trim=False, bundle_errors=False):
        self.args = []
        self.argument_class = argument_class
        self.namespace_class = namespace_class
        self.trim = trim
        self.bundle_errors = bundle_errors

    def add_argument(self, *args, **kwargs):
        """Adds an argument to be parsed.

        Accepts either a single instance of Argument or arguments to be passed
        into :class:`Argument`'s constructor.

        See :class:`Argument`'s constructor for documentation on the
        available options.
        """

        if len(args) == 1 and isinstance(args[0], self.argument_class):
            self.args.append(args[0])
        else:
            self.args.append(self.argument_class(*args, **kwargs))

        # Do not know what other argument classes are out there
        if self.trim and self.argument_class is Argument:
            # enable trim for appended element
            self.args[-1].trim = kwargs.get('trim', self.trim)

        return self

    def parse_args(self, req=None, strict=False, http_error_code=400):
        """Parse all arguments from the provided request and return the results
        as a Namespace

        :param req: Can be used to overwrite request from Flask
        :param strict: if req includes args not in parser, throw 400 BadRequest exception
        :param http_error_code: use custom error code for `flask_restful.abort()`
        """
        if req is None:
            req = request

        namespace = self.namespace_class()

        # A record of arguments not yet parsed; as each is found
        # among self.args, it will be popped out
        req.unparsed_arguments = dict(self.argument_class('').source(req)) if strict else {}
        errors = {}
        for arg in self.args:
            value, found = arg.parse(req, self.bundle_errors)
            if isinstance(value, ValueError):
                errors.update(found)
                found = None
            if found or arg.store_missing:
                namespace[arg.dest or arg.name] = value
        if errors:
            flask_restful.abort(http_error_code, message=errors)

        if strict and req.unparsed_arguments:
            raise exceptions.BadRequest('Unknown arguments: %s'
                                        % ', '.join(req.unparsed_arguments.keys()))

        return namespace

    def copy(self):
        """ Creates a copy of this RequestParser with the same set of arguments """
        parser_copy = self.__class__(self.argument_class, self.namespace_class)
        parser_copy.args = deepcopy(self.args)
        parser_copy.trim = self.trim
        parser_copy.bundle_errors = self.bundle_errors
        return parser_copy

    def replace_argument(self, name, *args, **kwargs):
        """ Replace the argument matching the given name with a new version. """
        new_arg = self.argument_class(name, *args, **kwargs)
        for index, arg in enumerate(self.args[:]):
            if new_arg.name == arg.name:
                del self.args[index]
                self.args.append(new_arg)
                break
        return self

    def remove_argument(self, name):
        """ Remove the argument matching the given name. """
        for index, arg in enumerate(self.args[:]):
            if name == arg.name:
                del self.args[index]
                break
        return self
