# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
import os
import shutil
from typing import Dict

from taipy.common.logger._taipy_logger import _TaipyLogger

from ._utils import _migrate

__logger = _TaipyLogger._get_logger()


def _load_all_entities_from_fs(root: str) -> Dict:
    # run through all files in the data folder and load them
    entities = {}
    for dirpath, _, files in os.walk(root):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(dirpath, file)) as f:
                    _id = file.split(".")[0]
                    if "version" in dirpath:
                        _id = f"VERSION_{_id}"
                    entities[_id] = {
                        "data": json.load(f),
                        "path": os.path.join(dirpath, file),
                    }
    return entities


def __write_entities_to_fs(_entities: Dict, root: str):
    if not os.path.exists(root):
        os.makedirs(root, exist_ok=True)

    for _id, entity in _entities.items():
        # Do not write pipeline entities
        if "PIPELINE" in _id:
            continue
        with open(entity["path"], "w") as f:
            json.dump(entity["data"], f, indent=0)

    # Remove pipelines folder
    pipelines_path = os.path.join(root, "pipelines")
    if os.path.exists(pipelines_path):
        shutil.rmtree(pipelines_path)


def _restore_migrate_file_entities(path: str) -> bool:
    backup_path = f"{path}_backup"

    if not os.path.exists(backup_path):
        __logger.error(f"The backup folder '{backup_path}' does not exist.")
        return False

    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        __logger.warning(f"The original entities folder '{path}' does not exist.")

    os.rename(backup_path, path)
    __logger.info(f"Restored entities from the backup folder '{backup_path}' to '{path}'.")
    return True


def _remove_backup_file_entities(path: str) -> bool:
    backup_path = f"{path}_backup"
    if not os.path.exists(backup_path):
        __logger.error(f"The backup folder '{backup_path}' does not exist.")
        return False

    shutil.rmtree(backup_path)
    __logger.info(f"Removed backup entities from the backup folder '{backup_path}'.")
    return True


def _migrate_fs_entities(path: str, backup: bool = True) -> bool:
    """Migrate entities from filesystem to the current version.

    Args:
        path (str): The path to the folder containing the entities.
        backup (bool, optional): Whether to backup the entities before migrating. Defaults to True.

    Returns:
        bool: True if the migration was successful, False otherwise.
    """
    if not os.path.isdir(path):
        __logger.error(f"Folder '{path}' does not exist.")
        return False

    if backup:
        backup_path = f"{path}_backup"
        try:
            shutil.copytree(path, backup_path)
        except FileExistsError:
            __logger.warning(f"The backup folder '{backup_path}' already exists. Migration canceled.")
            return False
        else:
            __logger.info(f"Backed up entities from '{path}' to '{backup_path}' folder before migration.")

    __logger.info(f"Starting entity migration from '{path}' folder.")

    entities = _load_all_entities_from_fs(path)
    entities, _ = _migrate(entities)
    __write_entities_to_fs(entities, path)

    __logger.info("Migration finished")
    return True
