import pickle
import sys
import io
import os
import json
import uuid
import logging
import re  # NOQA
import builtins  # NOQA
import datetime  # NOQA
import decimal  # NOQA
import ordered_set  # NOQA
import collections  # NOQA
try:
    import yaml
except ImportError:  # pragma: no cover.
    yaml = None  # pragma: no cover.
try:
    if sys.version_info >= (3, 11):
        import tomllib as tomli
    else:
        import tomli
except ImportError:  # pragma: no cover.
    tomli = None  # pragma: no cover.
try:
    import tomli_w
except ImportError:  # pragma: no cover.
    tomli_w = None  # pragma: no cover.
try:
    import clevercsv
    csv = None
except ImportError:  # pragma: no cover.
    import csv
    clevercsv = None  # pragma: no cover.
try:
    import orjson
except ImportError:  # pragma: no cover.
    orjson = None
try:
    from pydantic import BaseModel as PydanticBaseModel
except ImportError:  # pragma: no cover.
    PydanticBaseModel = None

from copy import deepcopy
from functools import partial
from collections.abc import Mapping
from deepdiff.helper import (
    strings, get_type, TEXT_VIEW, np_float32, np_float64, np_int32, np_int64
)
from deepdiff.model import DeltaResult

logger = logging.getLogger(__name__)

try:
    import jsonpickle
except ImportError:  # pragma: no cover. Json pickle is getting deprecated.
    jsonpickle = None  # pragma: no cover. Json pickle is getting deprecated.


class UnsupportedFormatErr(TypeError):
    pass


NONE_TYPE = type(None)

CSV_HEADER_MAX_CHUNK_SIZE = 2048  # The chunk needs to be big enough that covers a couple of rows of data.


MODULE_NOT_FOUND_MSG = 'DeepDiff Delta did not find {} in your modules. Please make sure it is already imported.'
FORBIDDEN_MODULE_MSG = "Module '{}' is forbidden. You need to explicitly pass it by passing a safe_to_import parameter"
DELTA_IGNORE_ORDER_NEEDS_REPETITION_REPORT = 'report_repetition must be set to True when ignore_order is True to create the delta object.'
DELTA_ERROR_WHEN_GROUP_BY = 'Delta can not be made when group_by is used since the structure of data is modified from the original form.'

SAFE_TO_IMPORT = {
    'builtins.range',
    'builtins.complex',
    'builtins.set',
    'builtins.frozenset',
    'builtins.slice',
    'builtins.str',
    'builtins.bytes',
    'builtins.list',
    'builtins.tuple',
    'builtins.int',
    'builtins.float',
    'builtins.dict',
    'builtins.bool',
    'builtins.bin',
    'builtins.None',
    'datetime.datetime',
    'datetime.time',
    'datetime.timedelta',
    'decimal.Decimal',
    'uuid.UUID',
    'ordered_set.OrderedSet',
    'collections.namedtuple',
    'collections.OrderedDict',
    're.Pattern',
}


TYPE_STR_TO_TYPE = {
    'range': range,
    'complex': complex,
    'set': set,
    'frozenset': frozenset,
    'slice': slice,
    'str': str,
    'bytes': bytes,
    'list': list,
    'tuple': tuple,
    'int': int,
    'float': float,
    'dict': dict,
    'bool': bool,
    'bin': bin,
    'None': None,
    'NoneType': None,
    'datetime': datetime.datetime,
    'time': datetime.time,
    'timedelta': datetime.timedelta,
    'Decimal': decimal.Decimal,
    'OrderedSet': ordered_set.OrderedSet,
    'namedtuple': collections.namedtuple,
    'OrderedDict': collections.OrderedDict,
    'Pattern': re.Pattern,    
}


class ModuleNotFoundError(ImportError):
    """
    Raised when the module is not found in sys.modules
    """
    pass


class ForbiddenModule(ImportError):
    """
    Raised when a module is not explicitly allowed to be imported
    """
    pass


class SerializationMixin:

    def to_json_pickle(self):
        """
        :ref:`to_json_pickle_label`
        Get the json pickle of the diff object. Unless you need all the attributes and functionality of DeepDiff, running to_json() is the safer option that json pickle.
        """
        if jsonpickle:
            copied = self.copy()
            return jsonpickle.encode(copied)
        else:
            logger.error('jsonpickle library needs to be installed in order to run to_json_pickle')  # pragma: no cover. Json pickle is getting deprecated.

    @classmethod
    def from_json_pickle(cls, value):
        """
        :ref:`from_json_pickle_label`
        Load DeepDiff object with all the bells and whistles from the json pickle dump.
        Note that json pickle dump comes from to_json_pickle
        """
        if jsonpickle:
            return jsonpickle.decode(value)
        else:
            logger.error('jsonpickle library needs to be installed in order to run from_json_pickle')  # pragma: no cover. Json pickle is getting deprecated.

    def to_json(self, default_mapping=None, **kwargs):
        """
        Dump json of the text view.
        **Parameters**

        default_mapping : dictionary(optional), a dictionary of mapping of different types to json types.

        by default DeepDiff converts certain data types. For example Decimals into floats so they can be exported into json.
        If you have a certain object type that the json serializer can not serialize it, please pass the appropriate type
        conversion through this dictionary.

        kwargs: Any other kwargs you pass will be passed on to Python's json.dumps()

        **Example**

        Serialize custom objects
            >>> class A:
            ...     pass
            ...
            >>> class B:
            ...     pass
            ...
            >>> t1 = A()
            >>> t2 = B()
            >>> ddiff = DeepDiff(t1, t2)
            >>> ddiff.to_json()
            TypeError: We do not know how to convert <__main__.A object at 0x10648> of type <class '__main__.A'> for json serialization. Please pass the default_mapping parameter with proper mapping of the object to a basic python type.

            >>> default_mapping = {A: lambda x: 'obj A', B: lambda x: 'obj B'}
            >>> ddiff.to_json(default_mapping=default_mapping)
            '{"type_changes": {"root": {"old_type": "A", "new_type": "B", "old_value": "obj A", "new_value": "obj B"}}}'
        """
        dic = self.to_dict(view_override=TEXT_VIEW)
        return json_dumps(dic, default_mapping=default_mapping, **kwargs)

    def to_dict(self, view_override=None):
        """
        convert the result to a python dictionary. You can override the view type by passing view_override.

        **Parameters**

        view_override: view type, default=None,
            override the view that was used to generate the diff when converting to the dictionary.
            The options are the text or tree.
        """

        view = view_override if view_override else self.view
        return dict(self._get_view_results(view))

    def _to_delta_dict(self, directed=True, report_repetition_required=True, always_include_values=False):
        """
        Dump to a dictionary suitable for delta usage.
        Unlike to_dict, this is not dependent on the original view that the user chose to create the diff.

        **Parameters**

        directed : Boolean, default=True, whether to create a directional delta dictionary or a symmetrical

        Note that in the current implementation the symmetrical delta (non-directional) is ONLY used for verifying that
        the delta is being applied to the exact same values as what was used to generate the delta and has
        no other usages.

        If this option is set as True, then the dictionary will not have the "old_value" in the output.
        Otherwise it will have the "old_value". "old_value" is the value of the item in t1.

        If delta = Delta(DeepDiff(t1, t2)) then
        t1 + delta == t2

        Note that it the items in t1 + delta might have slightly different order of items than t2 if ignore_order
        was set to be True in the diff object.

        """
        if self.group_by is not None:
            raise ValueError(DELTA_ERROR_WHEN_GROUP_BY)

        result = DeltaResult(tree_results=self.tree, ignore_order=self.ignore_order, always_include_values=always_include_values)
        result.remove_empty_keys()
        if report_repetition_required and self.ignore_order and not self.report_repetition:
            raise ValueError(DELTA_IGNORE_ORDER_NEEDS_REPETITION_REPORT)
        if directed:
            for report_key, report_value in result.items():
                if isinstance(report_value, Mapping):
                    for path, value in report_value.items():
                        if isinstance(value, Mapping) and 'old_value' in value:
                            del value['old_value']
        if self._numpy_paths:
            # Note that keys that start with '_' are considered internal to DeepDiff
            # and will be omitted when counting distance. (Look inside the distance module.)
            result['_numpy_paths'] = self._numpy_paths

        if self.iterable_compare_func:
            result['_iterable_compare_func_was_used'] = True

        return deepcopy(dict(result))

    def pretty(self):
        """
        The pretty human readable string output for the diff object
        regardless of what view was used to generate the diff.

        Example:
            >>> t1={1,2,4}
            >>> t2={2,3}
            >>> print(DeepDiff(t1, t2).pretty())
            Item root[3] added to set.
            Item root[4] removed from set.
            Item root[1] removed from set.
        """
        result = []
        keys = sorted(self.tree.keys())  # sorting keys to guarantee constant order across python versions.
        for key in keys:
            for item_key in self.tree[key]:
                result += [pretty_print_diff(item_key)]

        return '\n'.join(result)


class _RestrictedUnpickler(pickle.Unpickler):

    def __init__(self, *args, **kwargs):
        self.safe_to_import = kwargs.pop('safe_to_import', None)
        if self.safe_to_import:
            if isinstance(self.safe_to_import, strings):
                self.safe_to_import = set([self.safe_to_import])
            elif isinstance(self.safe_to_import, (set, frozenset)):
                pass
            else:
                self.safe_to_import = set(self.safe_to_import)
            self.safe_to_import = self.safe_to_import | SAFE_TO_IMPORT
        else:
            self.safe_to_import = SAFE_TO_IMPORT
        super().__init__(*args, **kwargs)

    def find_class(self, module, name):
        # Only allow safe classes from self.safe_to_import.
        module_dot_class = '{}.{}'.format(module, name)
        if module_dot_class in self.safe_to_import:
            try:
                module_obj = sys.modules[module]
            except KeyError:
                raise ModuleNotFoundError(MODULE_NOT_FOUND_MSG.format(module_dot_class)) from None
            return getattr(module_obj, name)
        # Forbid everything else.
        raise ForbiddenModule(FORBIDDEN_MODULE_MSG.format(module_dot_class)) from None

    def persistent_load(self, persistent_id):
        if persistent_id == "<<NoneType>>":
            return type(None)


class _RestrictedPickler(pickle.Pickler):
    def persistent_id(self, obj):
        if obj is NONE_TYPE:  # NOQA
            return "<<NoneType>>"
        return None


def pickle_dump(obj, file_obj=None, protocol=4):
    """
    **pickle_dump**
    Dumps the obj into pickled content.

    **Parameters**

    obj : Any python object

    file_obj : (Optional) A file object to dump the contents into

    **Returns**

    If file_obj is passed the return value will be None. It will write the object's pickle contents into the file.
    However if no file_obj is passed, then it will return the pickle serialization of the obj in the form of bytes.
    """
    file_obj_passed = bool(file_obj)
    file_obj = file_obj or io.BytesIO()
    _RestrictedPickler(file_obj, protocol=protocol, fix_imports=False).dump(obj)
    if not file_obj_passed:
        return file_obj.getvalue()


def pickle_load(content=None, file_obj=None, safe_to_import=None):
    """
    **pickle_load**
    Load the pickled content. content should be a bytes object.

    **Parameters**

    content : Bytes of pickled object. 

    file_obj : A file object to load the content from

    safe_to_import : A set of modules that needs to be explicitly allowed to be loaded.
        Example: {'mymodule.MyClass', 'decimal.Decimal'}
        Note that this set will be added to the basic set of modules that are already allowed.
        The set of what is already allowed can be found in deepdiff.serialization.SAFE_TO_IMPORT

    **Returns**

        A delta object that can be added to t1 to recreate t2.

    **Examples**

    Importing
        >>> from deepdiff import DeepDiff, Delta
        >>> from pprint import pprint


    """
    if not content and not file_obj:
        raise ValueError('Please either pass the content or the file_obj to pickle_load.') 
    if isinstance(content, str):
        content = content.encode('utf-8')
    if content:
        file_obj = io.BytesIO(content)
    return _RestrictedUnpickler(file_obj, safe_to_import=safe_to_import).load()


def _get_pretty_form_text(verbose_level):
    pretty_form_texts = {
        "type_changes": "Type of {diff_path} changed from {type_t1} to {type_t2} and value changed from {val_t1} to {val_t2}.",
        "values_changed": "Value of {diff_path} changed from {val_t1} to {val_t2}.",
        "dictionary_item_added": "Item {diff_path} added to dictionary.",
        "dictionary_item_removed": "Item {diff_path} removed from dictionary.",
        "iterable_item_added": "Item {diff_path} added to iterable.",
        "iterable_item_removed": "Item {diff_path} removed from iterable.",
        "attribute_added": "Attribute {diff_path} added.",
        "attribute_removed": "Attribute {diff_path} removed.",
        "set_item_added": "Item root[{val_t2}] added to set.",
        "set_item_removed": "Item root[{val_t1}] removed from set.",
        "repetition_change": "Repetition change for item {diff_path}.",
    }
    if verbose_level == 2:
        pretty_form_texts.update(
            {
                "dictionary_item_added": "Item {diff_path} ({val_t2}) added to dictionary.",
                "dictionary_item_removed": "Item {diff_path} ({val_t1}) removed from dictionary.",
                "iterable_item_added": "Item {diff_path} ({val_t2}) added to iterable.",
                "iterable_item_removed": "Item {diff_path} ({val_t1}) removed from iterable.",
                "attribute_added": "Attribute {diff_path} ({val_t2}) added.",
                "attribute_removed": "Attribute {diff_path} ({val_t1}) removed.",
            }
        )
    return pretty_form_texts


def pretty_print_diff(diff):
    type_t1 = get_type(diff.t1).__name__
    type_t2 = get_type(diff.t2).__name__

    val_t1 = '"{}"'.format(str(diff.t1)) if type_t1 == "str" else str(diff.t1)
    val_t2 = '"{}"'.format(str(diff.t2)) if type_t2 == "str" else str(diff.t2)

    diff_path = diff.path(root='root')
    return _get_pretty_form_text(diff.verbose_level).get(diff.report_type, "").format(
        diff_path=diff_path,
        type_t1=type_t1,
        type_t2=type_t2,
        val_t1=val_t1,
        val_t2=val_t2)


def load_path_content(path, file_type=None):
    """
    Loads and deserializes the content of the path.
    """
    if file_type is None:
        file_type = path.split('.')[-1]
    if file_type == 'json':
        with open(path, 'r') as the_file:
            content = json_loads(the_file.read())
    elif file_type in {'yaml', 'yml'}:
        if yaml is None:  # pragma: no cover.
            raise ImportError('Pyyaml needs to be installed.')  # pragma: no cover.
        with open(path, 'r') as the_file:
            content = yaml.safe_load(the_file)
    elif file_type == 'toml':
        if tomli is None:  # pragma: no cover.
            raise ImportError('On python<=3.10 tomli needs to be installed.')  # pragma: no cover.
        with open(path, 'rb') as the_file:
            content = tomli.load(the_file)
    elif file_type == 'pickle':
        with open(path, 'rb') as the_file:
            content = the_file.read()
            content = pickle_load(content)
    elif file_type in {'csv', 'tsv'}:
        if clevercsv:  # pragma: no cover.
            content = clevercsv.read_dicts(path)
        else:
            with open(path, 'r') as the_file:
                content = list(csv.DictReader(the_file))
        logger.info(f"NOTE: CSV content was empty in {path}")

        # Everything in csv is string but we try to automatically convert any numbers we find
        for row in content:
            for key, value in row.items():
                value = value.strip()
                for type_ in [int, float, complex]:
                    try:
                        value = type_(value)
                    except Exception:
                        pass
                    else:
                        row[key] = value
                        break
    else:
        raise UnsupportedFormatErr(f'Only json, yaml, toml, csv, tsv and pickle are supported.\n'
                                   f' The {file_type} extension is not known.')
    return content


def save_content_to_path(content, path, file_type=None, keep_backup=True):
    """
    Saves and serializes the content of the path.
    """

    backup_path = f"{path}.bak"
    os.rename(path, backup_path)

    try:
        _save_content(
            content=content, path=path,
            file_type=file_type, keep_backup=keep_backup)
    except Exception:
        os.rename(backup_path, path)
        raise
    else:
        if not keep_backup:
            os.remove(backup_path)


def _save_content(content, path, file_type, keep_backup=True):
    if file_type == 'json':
        with open(path, 'w') as the_file:
            content = json_dumps(content)
            the_file.write(content)
    elif file_type in {'yaml', 'yml'}:
        if yaml is None:  # pragma: no cover.
            raise ImportError('Pyyaml needs to be installed.')  # pragma: no cover.
        with open(path, 'w') as the_file:
            content = yaml.safe_dump(content, stream=the_file)
    elif file_type == 'toml':
        if tomli_w is None:  # pragma: no cover.
            raise ImportError('Tomli-w needs to be installed.')  # pragma: no cover.
        with open(path, 'wb') as the_file:
            content = tomli_w.dump(content, the_file)
    elif file_type == 'pickle':
        with open(path, 'wb') as the_file:
            content = pickle_dump(content, file_obj=the_file)
    elif file_type in {'csv', 'tsv'}:
        if clevercsv:  # pragma: no cover.
            dict_writer = clevercsv.DictWriter
        else:
            dict_writer = csv.DictWriter
        with open(path, 'w', newline='') as csvfile:
            fieldnames = list(content[0].keys())
            writer = dict_writer(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(content)
    else:
        raise UnsupportedFormatErr('Only json, yaml, toml, csv, tsv and pickle are supported.\n'
                                   f' The {file_type} extension is not known.')
    return content


def _serialize_decimal(value):
    if value.as_tuple().exponent == 0:
        return int(value)
    else:
        return float(value)


JSON_CONVERTOR = {
    decimal.Decimal: _serialize_decimal,
    ordered_set.OrderedSet: list,
    set: list,
    type: lambda x: x.__name__,
    bytes: lambda x: x.decode('utf-8'),
    datetime.datetime: lambda x: x.isoformat(),
    uuid.UUID: lambda x: str(x),
    np_float32: float,
    np_float64: float,
    np_int32: int,
    np_int64: int
}

if PydanticBaseModel:
    JSON_CONVERTOR[PydanticBaseModel] = lambda x: x.dict()


def json_convertor_default(default_mapping=None):
    if default_mapping:
        _convertor_mapping = JSON_CONVERTOR.copy()
        _convertor_mapping.update(default_mapping)
    else:
        _convertor_mapping = JSON_CONVERTOR

    def _convertor(obj):
        for original_type, convert_to in _convertor_mapping.items():
            if isinstance(obj, original_type):
                return convert_to(obj)
        raise TypeError('We do not know how to convert {} of type {} for json serialization. Please pass the default_mapping parameter with proper mapping of the object to a basic python type.'.format(obj, type(obj)))

    return _convertor


class JSONDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'old_type' in obj and 'new_type' in obj:
            for type_key in ('old_type', 'new_type'):
                type_str = obj[type_key]
                obj[type_key] = TYPE_STR_TO_TYPE.get(type_str, type_str)

        return obj


def json_dumps(item, default_mapping=None, **kwargs):
    """
    Dump json with extra details that are not normally json serializable
    """
    if orjson:
        indent = kwargs.pop('indent', None)
        if indent:
            kwargs['option'] = orjson.OPT_INDENT_2
        return orjson.dumps(
            item,
            default=json_convertor_default(default_mapping=default_mapping),
            **kwargs).decode(encoding='utf-8')
    else:
        return json.dumps(
            item,
            default=json_convertor_default(default_mapping=default_mapping),
            **kwargs)


json_loads = partial(json.loads, cls=JSONDecoder)
