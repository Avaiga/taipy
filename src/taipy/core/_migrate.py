# Copyright 2023 Avaiga Private Limited
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
import sqlite3
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import pymongo

from taipy.logger._taipy_logger import _TaipyLogger

__logger = _TaipyLogger._get_logger()


def __update_parent_ids(entity: Dict, data: Dict) -> Dict:
    # parent_id was replaced by parent_ids
    _ = entity.pop("parent_id", None)

    # parent_ids was not present in 2.0, need to be search for in tasks
    parent_ids = entity.get("parent_ids", [])
    if not parent_ids:
        parent_ids = __search_parent_ids(entity["id"], data)
    entity["parent_ids"] = parent_ids

    return entity


def __update_config_parent_ids(id: str, entity: Dict, entity_type: str, config: Dict) -> Dict:
    # parent_id was replaced by parent_ids
    _ = entity.pop("parent_id", None)

    # parent_ids was not present in 2.0, need to be search for in tasks
    parent_ids = entity.get("parent_ids", [])

    if not parent_ids:
        parent_ids = __search_parent_config(id, config, entity_type)
    entity["parent_ids"] = parent_ids

    return entity


def __search_parent_ids(entity_id: str, data: Dict) -> List:
    parents = []
    entity_type = entity_id.split("_", 1)[0]

    for _id, entity_data in data.items():
        entity_data = entity_data["data"]
        if entity_type == "DATANODE" and "TASK" in _id:
            if entity_id in entity_data["input_ids"] or entity_id in entity_data["output_ids"]:
                parents.append(_id)

        if entity_type == "TASK" and "SCENARIO" in _id:
            if entity_id in entity_data["tasks"]:
                parents.append(_id)
    return parents


def __search_parent_config(entity_id: str, config: Dict, entity_type: str) -> List:
    parents = []
    possible_parents = "TASK" if entity_type == "DATA_NODE" else "SCENARIO"
    data = config[possible_parents]

    for _id, entity_data in data.items():
        section_id = f"{entity_id}:SECTION"
        if entity_type == "DATANODE" and possible_parents == "TASK":
            if section_id in entity_data["input_ids"] or section_id in entity_data["output_ids"]:
                parents.append(section_id)

        if entity_type == "TASK" and possible_parents == "SCENARIO":
            if section_id in entity_data["tasks"]:
                parents.append(section_id)
    return parents


def __fetch_tasks_from_pipelines(pipelines: List, data: Dict) -> List:
    tasks = []
    for pipeline in pipelines:
        pipeline_data = data[pipeline]["data"]
        tasks.extend(pipeline_data["tasks"])
    return tasks


def __migrate_subscriber(fct_module, fct_name):
    """Rename scheduler by orchestrator on old jobs. Used to migrate from <=2.2 to >=2.3 version."""

    if fct_module == "taipy.core._scheduler._scheduler":
        fct_module = fct_module.replace("_scheduler", "_orchestrator")
        fct_name = fct_name.replace("_Scheduler", "_Orchestrator")
    return fct_module, fct_name


def _migrate_scenario(scenario: Dict, data: Dict) -> Dict:
    # pipelines were replaced by tasks
    scenario["tasks"] = __fetch_tasks_from_pipelines(scenario["pipelines"], data)

    # pipeline attribute not removed in 3.0
    scenario["pipelines"] = None

    # additional_data_nodes attribute added
    scenario["additional_data_nodes"] = []

    return scenario


def __is_cacheable(task: Dict, data: Dict) -> bool:
    for id in task["output_ids"]:
        dn = data.get(id, {})
        if "cacheable" not in dn or not dn["cacheable"]:
            return False
    return True


def _migrate_task(task: Dict, data: Dict) -> Dict:
    # owner_id was not present in 2.0
    if task.get("parent_id"):
        task["owner_id"] = task.get("owner_id")
        del task["parent_id"]

    # properties was not present in 2.0
    task["properties"] = task.get("properties", {})

    # skippable was not present in 2.0
    task["skippable"] = task.get("skippable", False) or __is_cacheable(task, data)

    return task


def _migrate_task_entity(task: Dict, data: Dict) -> Dict:
    task = __update_parent_ids(task, data)
    return _migrate_task(task, data)


def _migrate_task_config(id: str, task: Dict, config: Dict) -> Dict:
    task = __update_config_parent_ids(id, task, "TASK", config)
    return _migrate_task(task, config["DATA_NODE"])


def __update_scope(scope: str):
    if scope in "<Scope.SCENARIO: 2>":
        return "<Scope.SCENARIO: 1>"
    elif scope == "<Scope.CYCLE: 3>":
        return "<Scope.CYCLE: 2>"
    elif scope == "<Scope.GLOBAL: 4>":
        return "<Scope.GLOBAL: 3>"
    return scope


def _migrate_datanode(datanode: Dict) -> Dict:
    # cacheable was removed in after 2.0
    _ = datanode.pop("cacheable", False)

    # job_ids was replaced by edits
    if "job_ids" in datanode:
        datanode["edits"] = [{"job_id": job, "timestamp": datanode["last_edit_date"]} for job in datanode["job_ids"]]
    elif "edits" in datanode:
        # make sure timestamp inside edits is a string
        edits = []
        for edit in datanode["edits"]:
            timestamp = edit.get("timestamp")
            if isinstance(timestamp, dict):
                timestamp = timestamp.get("__value__")
            new_edit = {"timestamp": timestamp}
            if "job_id" in edit:
                new_edit["job_id"] = edit["job_id"]
            edits.append(new_edit)
        datanode["edits"] = edits

    # owner_id was not present in 2.0, need to be search for in tasks
    datanode["owner_id"] = datanode["parent_ids"][0] if datanode["parent_ids"] else None

    # Update Scope enum after Pipeline removal
    datanode["scope"] = __update_scope(datanode["scope"])

    if "last_edit_date" not in datanode:
        datanode["last_edit_date"] = datanode.get("last_edition_date")
        if "last_edition_date" in datanode:
            del datanode["last_edition_date"]

    if "edit_in_progress" not in datanode:
        datanode["edit_in_progress"] = datanode.get("edition_in_progress")
        if "edition_in_progress" in datanode:
            del datanode["edition_in_progress"]

    return datanode


def _migrate_datanode_entity(datanode: Dict, data: Dict) -> Dict:
    datanode = __update_parent_ids(datanode, data)
    return _migrate_datanode(datanode)


def _migrate_datanode_config(id: str, datanode: Dict, config: Dict) -> Dict:
    datanode_cfg = __update_config_parent_ids(id, datanode, "DATA_NODE", config)
    datanode_cfg = _migrate_datanode(datanode_cfg)
    return datanode_cfg


def _migrate_job(job: Dict) -> Dict:
    # submit_entity_id was not present before 3.0
    job["submit_entity_id"] = job.get("submit_entity_id", None)
    if "subscribers" in job:
        for sub in job["subscribers"]:
            sub["fct_module"], sub["fct_name"] = __migrate_subscriber(sub["fct_module"], sub["fct_name"])
    return job


def _migrate_version(version: Dict) -> Dict:
    config_str = version["config"]

    # Remove PIPELINE scope
    config_str = config_str.replace("PIPELINE:SCOPE", "SCENARIO:SCOPE")
    config = json.loads(config_str)

    # replace pipelines for tasks
    pipelines_section = config["PIPELINE"]
    for id, content in config["SCENARIO"].items():
        tasks = []
        for _pipeline in content["pipelines"]:
            pipeline_id = _pipeline.split(":")[0]
            tasks = pipelines_section[pipeline_id]["tasks"]
        config["SCENARIO"][id]["tasks"] = tasks
        del config["SCENARIO"][id]["pipelines"]

    for id, content in config["TASK"].items():
        config["TASK"][id] = _migrate_task_config(id, content, config)

    config["JOB"] = _migrate_job(config["JOB"])
    for id, content in config["DATA_NODE"].items():
        config["DATA_NODE"][id] = _migrate_datanode_config(id, content, config)

    del config["PIPELINE"]

    version["config"] = json.dumps(config)
    return version


def _migrate_entity(entity_type: str, data: Dict) -> Dict:
    migration_fct = FCT_MIGRATION_MAP.get(entity_type)
    _entities = {k: data[k] for k in data if entity_type in k}

    for k, v in _entities.items():
        if entity_type in ["JOB", "VERSION"]:
            v["data"] = migration_fct(v["data"])  # type: ignore
        else:
            v["data"] = migration_fct(v["data"], data)  # type: ignore
        data[k] = v
    return data


def _load_all_entities_from_fs(root: str = ".data") -> Dict:
    # run through all files in the data folder and load them
    entities = {}
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file)) as f:
                    _id = file.split(".")[0]
                    if "version" in root:
                        _id = f"VERSION_{_id}"
                    entities[_id] = {
                        "data": json.load(f),
                        "path": os.path.join(root, file),
                    }
    return entities


def __write_entities_to_fs(_entities: Dict, root: str = ".data"):
    if not os.path.exists(root):
        os.makedirs(root, exist_ok=True)

    for _id, entity in _entities.items():
        with open(os.path.join(root, entity["path"]), "w") as f:
            json.dump(entity["data"], f, indent=2)


@lru_cache
def __connect_mongodb(db_host: str, db_port: int, db_username: str, db_password: str) -> pymongo.MongoClient:
    auth_str = ""
    if db_username and db_password:
        auth_str = f"{db_username}:{db_password}@"

    connection_string = f"mongodb://{auth_str}{db_host}:{db_port}"

    return pymongo.MongoClient(connection_string)


def _load_all_entities_from_mongo(
    hostname: str = "localhost",
    port: int = 27017,
    user: str = "taipy",
    password: str = "password",
):
    client = __connect_mongodb(hostname, port, user, password)
    collections = [
        "cycle",
        "scenario",
        "pipeline",
        "task",
        "data_node",
        "job",
        "version",
    ]
    entities = {}
    for collection in collections:
        db = client["taipy"]
        cursor = db[collection].find({})
        for document in cursor:
            entities[document["id"]] = {"data": document}

    return entities


def __write_entities_to_mongo(
    _entities: Dict,
    hostname: str = "localhost",
    port: int = 27017,
    user: str = "taipy",
    password: str = "password",
):
    client = __connect_mongodb(hostname, port, user, password)
    collections = [
        "cycle",
        "scenario",
        "pipeline",
        "task",
        "data_node",
        "job",
        "version",
    ]
    for collection in collections:
        db = client["taipy"]
        db[collection].insert_many(
            [entity["data"] for entity in _entities.values() if collection in entity["data"]["id"]]
        )


def _load_all_entities_from_sql(db_file: str = "test.db") -> Tuple[Dict, Dict]:
    conn = sqlite3.connect(db_file)
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


def __write_entities_to_sql(_entities: Dict, _versions: Dict, db_file: str = "test.db"):
    conn = sqlite3.connect(db_file)

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

    for k, version in _versions.items():
        __insert_version(version, conn)


FCT_MIGRATION_MAP = {
    "SCENARIO": _migrate_scenario,
    "TASK": _migrate_task_entity,
    "DATANODE": _migrate_datanode_entity,
    "JOB": _migrate_job,
    "VERSION": _migrate_version,
}


def __migrate(entities: Dict, versions: Optional[Dict] = None) -> Tuple[Dict, Optional[Dict]]:
    __logger.info("Migrating SCENARIOS")
    entities = _migrate_entity("SCENARIO", entities)

    __logger.info("Migrating TASKS")
    entities = _migrate_entity("TASKS", entities)

    __logger.info("Migrating DATANODES")
    entities = _migrate_entity("DATANODE", entities)

    __logger.info("Migrating JOBS")
    entities = _migrate_entity("JOB", entities)

    __logger.info("Migrating VERSION")
    if versions:
        versions = _migrate_entity("VERSION", versions)
    else:
        entities = _migrate_entity("VERSION", entities)
    return entities, versions


def _migrate_fs_entities(path: str) -> None:
    __logger.info("Starting entity migration")
    entities = _load_all_entities_from_fs(path)

    entities, _ = __migrate(entities)

    __write_entities_to_fs(entities)

    __logger.info("Migration finished")


def _migrate_sql_entities(path: str) -> None:
    __logger.info("Starting entity migration")
    entities, versions = _load_all_entities_from_sql(path)

    entities, versions = __migrate(entities, versions)  # type: ignore

    __write_entities_to_sql(entities, versions, path)

    __logger.info("Migration finished")


def _migrate_mongo_entities(
    hostname: str = "localhost", port: int = 27017, user: str = "taipy", password: str = "password"
) -> None:
    __logger.info("Starting entity migration")
    entities = _load_all_entities_from_mongo(hostname, port, user, password)

    entities, _ = __migrate(entities)

    __write_entities_to_mongo(entities)

    __logger.info("Migration finished")
