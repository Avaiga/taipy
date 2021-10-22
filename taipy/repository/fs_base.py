import json
import shutil
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
    """
    This class holds common methods to be used and extended when a functionality of saving
    dataclasses as JSON files in local storage emerges.

    Some lines have type: ignore because MyPy won't recognize some generic attributes. This
    should be revised in the future.

    Attributes
    ----------
    model: ModelType
        Generic dataclass
    dir_name: str
        Folder that will hold the files for this dataclass model
    base_path: str
        Main folder that will hold the directories of all dataclass models
    """

    def __init__(self, model: Type[ModelType], dir_name: str, base_path: str = ".data"):
        self.model = model
        self.base_path = base_path
        self.dir_name = dir_name

    @property
    def directory(self):
        return path.join(self.base_path, self.dir_name)

    def __get_all_filenames(self):
        files = []
        if path.exists(self.directory):
            for filename in listdir(self.directory):
                if filename.endswith(".json"):
                    files.append(path.join(self.directory, filename))
        return files

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
        files = self.__get_all_filenames()
        for filename in files:
            models.append(self._build_model(self.__load_json_file(filename)))
        return models

    def save(self, model: Type[ModelType]):
        if not path.exists(self.directory):
            makedirs(self.directory)
        with open(path.join(self.directory, f"{model.id}.json"), "w") as f:  # type: ignore
            json.dump(model.to_dict(), f, ensure_ascii=False, indent=4, cls=EnumEncoder)  # type: ignore

    def delete_all(self):
        if path.exists(self.directory):
            shutil.rmtree(self.directory)

    def search(self, attribute: str, value: str) -> Optional[ModelType]:
        files = self.__get_all_filenames()
        model = None

        for filename in files:
            m = self._build_model(self.__load_json_file(filename))
            if hasattr(m, attribute) and getattr(m, attribute) == value:
                model = m
                break
        return model
