import json
import os
import pathlib
import shutil
from abc import abstractmethod
from enum import Enum
from os import path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from taipy.exceptions import ModelNotFound

ModelType = TypeVar("ModelType")
Entity = TypeVar("Entity")
Json = Union[dict, list, str, int, float, bool, None]


class CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Json:
        result: Json
        if isinstance(o, Enum):
            result = o.value
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class FileSystemRepository(Generic[ModelType, Entity]):
    """
    Holds common methods to be used and extended when the need for saving
    dataclasses as JSON files in local storage emerges.

    Some lines have type: ignore because MyPy won't recognize some generic attributes. This
    should be revised in the future.

    Attributes:
        model (ModelType): Generic dataclass.
        dir_name (str): Folder that will hold the files for this dataclass model.
        base_path (str): Main folder that will hold the directories of all dataclass models.
    """

    @abstractmethod
    def to_model(self, obj):
        """
        Converts the object to be saved to its model.
        """
        ...

    @abstractmethod
    def from_model(self, model):
        """
        Converts a model to its functional object.
        """
        ...

    def __init__(self, model: Type[ModelType], dir_name: str, base_path: str = ".data"):
        self.model = model
        self.base_path = base_path
        self.dir_name = dir_name

    @property
    def directory(self):
        dir_path = pathlib.Path(path.join(self.base_path, self.dir_name))
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def _build_model(self, model_data: Dict) -> ModelType:
        return self.model.from_dict(model_data)  # type: ignore

    def load(self, model_id: str) -> Optional[Entity]:
        try:
            filepath = path.join(self.base_path, self.dir_name, f"{model_id}.json")
            return self.__to_entity(filepath)
        except FileNotFoundError:
            raise ModelNotFound(self.dir_name, model_id)

    def load_all(self) -> List[Entity]:
        models = []
        for filename in pathlib.Path(self.directory).glob("*.json"):
            models.append(self.__to_entity(filename))
        return models

    def save(self, model):
        model = self.to_model(model)
        with open(path.join(self.directory, f"{model.id}.json"), "w") as f:  # type: ignore
            json.dump(model.to_dict(), f, ensure_ascii=False, indent=4, cls=CustomEncoder)  # type: ignore

    def delete_all(self):
        shutil.rmtree(self.directory)

    def delete(self, model_id: str):
        try:
            filepath = path.join(self.base_path, self.dir_name, f"{model_id}.json")
            os.unlink(filepath)
        except FileNotFoundError:
            raise ModelNotFound(self.dir_name, model_id)

    def search(self, attribute: str, value: str) -> Optional[Entity]:
        model = None
        for filename in pathlib.Path(self.directory).glob("*.json"):
            m = self.__to_entity(filename)
            if hasattr(m, attribute) and getattr(m, attribute) == value:
                model = m
                break
        return model

    def search_all(self, attribute: str, value: str) -> List[Entity]:
        models = []
        for filename in pathlib.Path(self.directory).glob("*.json"):
            m = self.__to_entity(filename)
            if hasattr(m, attribute) and getattr(m, attribute) == value:
                models.append(m)
        return models

    def __to_entity(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        model = self.model.from_dict(data)  # type: ignore
        return self.from_model(model)
