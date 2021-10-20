import json
from dataclasses import dataclass
from os import listdir, path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from typing_extensions import Protocol

from taipy.exceptions import ModelNotFound

ModelType = TypeVar("ModelType")


class FileSystemStorage(Generic[ModelType]):
    """ """

    def __init__(self, model: Type[ModelType], dir_name: str, base_path: str = ".data"):
        self.model = model
        self.base_path = base_path
        self.dir_name = dir_name

    def __load_json_file(self, filepath):
        with open(filepath, "r") as f:
            return json.load(f)

    def get(self, model_id: str) -> Optional[ModelType]:
        try:
            filepath = path.join(self.base_path, self.dir_name, model_id)
            return self.__load_json_file(filepath)
        except FileNotFoundError:
            raise ModelNotFound(self.dir_name, model_id)

    def get_all(self) -> List[Dict[Any, Any]]:
        models = []
        directory = path.join(self.base_path, self.dir_name)
        for filename in listdir(directory):
            if filename.endswith(".json"):
                models.append(self.__load_json_file(path.join(directory, filename)))
        return models

    def save(self):
        directory = path.join(self.base_path, self.dir_name)
        with open(path.join(directory, self.model.id), "w") as f:
            json.dump(self.model.to_json(), f, ensure_ascii=False, indent=4)
