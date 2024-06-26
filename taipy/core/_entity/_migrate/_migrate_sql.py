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

from contextlib import closing
import json
import os
import shutil
import sqlite3
from typing import Dict, Tuple

from taipy.logger._taipy_logger import _TaipyLogger

from ._utils import _migrate

__logger = _TaipyLogger._get_logger()


def _load_all_entities_from_sql(db_file: str) -> Tuple[Dict, Dict]:
    conn = sqlite3.connect(db_file)
    with closing(conn):
        query = "SELECT model_id, document FROM taipy_model"
        query_version = "SELECT * FROM taipy_version"
        cursor = conn.execute(query)
        entities = {}
        versions = {}

        for row in cursor:
            _id = row[0]
            document = row[1]
            entities[_id] = {"data": json.loads(document)}

        cursor = conn.execute(query_version)
        for row in cursor:
            id = row[0]
            config_id = row[1]
            creation_date = row[2]
            is_production = row[3]
            is_development = row[4]
            is_latest = row[5]
            versions[id] = {
                "config_id": config_id,
                "creation_date": creation_date,
                "is_production": is_production,
                "is_development": is_development,
                "is_latest": is_latest,
            }

    return entities, versions


def __insert_scenario(scenario: dict, conn):
    query = f"""
        INSERT INTO scenario (id, config_id, tasks, additional_data_nodes, creation_date, primary_scenario, subscribers,
         tags, version, pipelines, cycle)
        VALUES ({scenario['id']}, {scenario['config_id']}, {scenario['tasks']}, {scenario['additional_data_nodes']},
        {scenario['creation_date']}, {scenario['primary_scenario']}, {scenario['subscribers']}, {scenario['tags']},
        {scenario['version']}, {scenario['pipelines']}, {scenario['cycle']})
        """
    conn.execute(query)
    conn.commit()


def __insert_task(task: dict, conn):
    query = f"""
        INSERT INTO task (id, owner_id, parent_ids, config_id, input_ids, function_name, function_module, output_ids,
        version, skippable, properties)
        VALUES ({task['id']}, {task['owner_id']}, {task['parent_ids']}, {task['config_id']}, {task['input_ids']},
         {task['function_name']}, {task['function_module']}, {task['output_ids']}, {task['version']},
         {task['skippable']}, {task['properties']})
    """
    conn.execute(query)
    conn.commit()


def __insert_datanode(datanode: dict, conn):
    query = f"""
        INSERT INTO data_node (id, config_id, scope, storage_type, name, owner_id, parent_ids, last_edit_date, edits,
        version, validity_days, validity_seconds, edit_in_progress, data_node_properties)
        VALUES ({datanode['id']}, {datanode['config_id']}, {datanode['scope']}, {datanode['storage_type']},
        {datanode['name']}, {datanode['owner_id']}, {datanode['parent_ids']}, {datanode['last_edit_date']},
        {datanode['edits']}, {datanode['version']}, {datanode['validity_days']}, {datanode['validity_seconds']},
        {datanode['edit_in_progress']}, {datanode['data_node_properties']})
    """
    conn.execute(query)
    conn.commit()


def __insert_job(job: dict, conn):
    query = f"""
        INSERT INTO job (id, task_id, status, force, submit_id, submit_entity_id, creation_date, subscribers,
        stacktrace, version)
        VALUES ({job['id']}, {job['task_id']}, {job['status']}, {job['force']}, {job['submit_id']},
        {job['submit_entity_id']}, {job['creation_date']}, {job['subscribers']}, {job['stacktrace']}, {job['version']})
    """
    conn.execute(query)
    conn.commit()


def __insert_cycle(cycle: dict, conn):
    query = f"""
        INSERT INTO scenario (id, name, frequency, properties, creation_date, start_date, end_date)
        VALUES ({cycle['id']}, {cycle['name']}, {cycle['frequency']}, {cycle['properties']}, {cycle['creation_date']},
        {cycle['start_date']}, {cycle['end_date']})
    """
    conn.execute(query)
    conn.commit()


def __insert_version(version: dict, conn):
    query = f"""
        INSERT INTO version (id, config_id, creation_date, is_production, is_development, is_latest)
        VALUES ({version['id']}, {version['config_id']}, {version['creation_date']}, {version['is_production']},
        {version['is_development']}, {version['is_latest']})
    """
    conn.execute(query)
    conn.commit()


def __write_entities_to_sql(_entities: Dict, _versions: Dict, db_file: str):
    conn = sqlite3.connect(db_file)
    with closing(conn):
        for k, entity in _entities.items():
            if "SCENARIO" in k:
                __insert_scenario(entity["data"], conn)
            elif "TASK" in k:
                __insert_task(entity["data"], conn)
            elif "DATANODE" in k:
                __insert_datanode(entity["data"], conn)
            elif "JOB" in k:
                __insert_job(entity["data"], conn)
            elif "CYCLE" in k:
                __insert_cycle(entity["data"], conn)

        for _, version in _versions.items():
            __insert_version(version, conn)


def _restore_migrate_sql_entities(path: str) -> bool:
    file_name, file_extension = path.rsplit(".", 1)
    backup_path = f"{file_name}_backup.{file_extension}"

    if not os.path.exists(backup_path):
        __logger.error(f"The backup database '{backup_path}' does not exist.")
        return False

    if os.path.exists(path):
        os.remove(path)
    else:
        __logger.warning(f"The original entities database '{path}' does not exist.")

    os.rename(backup_path, path)
    __logger.info(f"Restored entities from the backup database '{backup_path}' to '{path}'.")
    return True


def _remove_backup_sql_entities(path: str) -> bool:
    file_name, file_extension = path.rsplit(".", 1)
    backup_path = f"{file_name}_backup.{file_extension}"
    if not os.path.exists(backup_path):
        __logger.error(f"The backup database '{backup_path}' does not exist.")
        return False

    os.remove(backup_path)
    __logger.info(f"Removed backup entities from the backup database '{backup_path}'.")
    return True


def _migrate_sql_entities(path: str, backup: bool = True) -> bool:
    """Migrate entities from sqlite database to the current version.

    Args:
        path (str): The path to the sqlite database.
        backup (bool, optional): Whether to backup the entities before migrating. Defaults to True.

    Returns:
        bool: True if the migration was successful, False otherwise.
    """
    if not path:
        __logger.error("Missing the required sqlite path.")
        return False
    if not os.path.exists(path):
        __logger.error(f"File '{path}' does not exist.")
        return False

    if backup:
        file_name, file_extension = path.rsplit(".", 1)
        shutil.copyfile(path, f"{file_name}_backup.{file_extension}")
        __logger.info(f"Backed up entities from '{path}' to '{file_name}_backup.{file_extension}' before migration.")

    __logger.info(f"Starting entity migration from sqlite database '{path}'")

    entities, versions = _load_all_entities_from_sql(path)
    entities, versions = _migrate(entities, versions)
    __write_entities_to_sql(entities, versions, path)

    __logger.info("Migration finished")
    return True
