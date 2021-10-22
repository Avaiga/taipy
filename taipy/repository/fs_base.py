import json
from enum import Enum
from os import listdir, makedirs, path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from taipy.exceptions import ModelNotFound

ModelType = TypeVar("ModelType")
Json = Union[dict, list, str, int, float, bool, None]


class EnumEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Json:
        result: Json
        if isinstance(o, Enum):
            result = o.value
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class FileSystemRepository(Generic[ModelType]):
    """ """

    def __init__(self, model: Type[ModelType], dir_name: str, base_path: str = ".data"):
        self.model = model
        self.base_path = base_path
        self.dir_name = dir_name

    def __load_json_file(self, filepath):
        with open(filepath, "r") as f:
            return json.load(f)

    def _build_model(self, model_data: Dict) -> ModelType:
        return self.model.from_dict(model_data)  # type: ignore

    def get(self, model_id: str) -> Optional[ModelType]:
        try:
            filepath = path.join(self.base_path, self.dir_name, f"{model_id}.json")
            return self._build_model(self.__load_json_file(filepath))
        except FileNotFoundError:
            raise ModelNotFound(self.dir_name, model_id)

    def get_all(self) -> List[ModelType]:
        models = []
        directory = path.join(self.base_path, self.dir_name)
        for filename in listdir(directory):
            if filename.endswith(".json"):
                models.append(self._build_model(self.__load_json_file(path.join(directory, filename))))
        return models

    def save(self, model: Type[ModelType]):
        directory = path.join(self.base_path, self.dir_name)
        if not path.exists(directory):
            makedirs(directory)
        with open(path.join(directory, f"{model.id}.json"), "w") as f:  # type: ignore
            json.dump(model.to_dict(), f, ensure_ascii=False, indent=4, cls=EnumEncoder)  # type: ignore
