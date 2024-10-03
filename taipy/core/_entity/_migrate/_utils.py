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
from importlib.metadata import version
from typing import Dict, List, Optional, Tuple

from taipy.common.logger._taipy_logger import _TaipyLogger

__logger = _TaipyLogger._get_logger()


def __update_parent_ids(entity: Dict, data: Dict) -> Dict:
    # parent_ids was not present in 2.0, need to be search for in tasks
    parent_ids = entity.get("parent_ids", [])
    id = entity["id"]

    if not parent_ids:
        parent_ids = __search_parent_ids(entity["id"], data)
    entity["parent_ids"] = parent_ids

    if "TASK" in id:
        parents = []
        for parent in entity.get("parent_ids", []):
            if "PIPELINE" in parent:
                continue
            parents.append(parent)
        if entity.get("owner_id") and entity.get("owner_id") not in parents:
            parents.append(entity.get("owner_id"))
        entity["parent_ids"] = parents

    return entity


def __update_config_parent_ids(id: str, entity: Dict, entity_type: str, config: Dict) -> Dict:
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
    parents.sort()
    return parents


def __search_parent_config(entity_id: str, config: Dict, entity_type: str) -> List:
    parents = []
    possible_parents = "TASK" if entity_type == "DATA_NODE" else "SCENARIO"
    data = config[possible_parents]

    section_id = f"{entity_id}:SECTION"
    for _id, entity_data in data.items():
        if entity_type == "DATANODE" and possible_parents == "TASK":
            if section_id in entity_data["input_ids"] or section_id in entity_data["output_ids"]:
                parents.append(section_id)

        if entity_type == "TASK" and possible_parents == "SCENARIO":
            if section_id in entity_data["tasks"]:
                parents.append(section_id)

    parents.sort()
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


def __migrate_scenario(scenario: Dict, data: Dict) -> Dict:
    if "pipelines" in scenario:
        # pipelines were replaced by tasks
        scenario["tasks"] = scenario.get("tasks") or __fetch_tasks_from_pipelines(scenario["pipelines"], data)

        # pipeline attribute not removed in 3.0
        scenario["pipelines"] = None

    # additional_data_nodes attribute added
    scenario["additional_data_nodes"] = scenario.get("additional_data_nodes", [])

    return scenario


def __is_cacheable(task: Dict, data: Dict) -> bool:
    output_ids = task.get("output_ids", []) or task.get("outputs", [])  # output_ids is on entity, outputs is on config

    for output_id in output_ids:
        if output_id.endswith(":SECTION"):  # Get the config_id if the task is a Config
            output_id = output_id.split(":")[0]
        dn = data.get(output_id, {})
        if "data" in dn:
            dn = dn.get("data", {})

        if "cacheable" not in dn or not dn["cacheable"] or dn["cacheable"] == "False:bool":
            return False
    return True


def __migrate_task(task: Dict, data: Dict, is_entity: bool = True) -> Dict:
    if is_entity:
        # parent_id has been renamed to owner_id
        try:
            task["owner_id"] = task.get("owner_id", task["parent_id"])
            del task["parent_id"]
        except KeyError:
            pass

        # properties attribute was not present in 2.0
        task["properties"] = task.get("properties", {})

    # skippable was not present in 2.0
    task["skippable"] = task.get("skippable", False) or __is_cacheable(task, data)

    return task


def __migrate_task_entity(task: Dict, data: Dict) -> Dict:
    task = __update_parent_ids(task, data)
    return __migrate_task(task, data)


def __migrate_task_config(task: Dict, config: Dict) -> Dict:
    task = __migrate_task(task, config["DATA_NODE"], False)

    # Convert the skippable boolean to a string if needed
    if isinstance(task.get("skippable"), bool):
        task["skippable"] = str(task["skippable"]) + ":bool"
    return task


def __update_scope(scope: str):
    if scope in "<Scope.SCENARIO: 2>":
        return "<Scope.SCENARIO: 1>"
    elif scope == "<Scope.CYCLE: 3>":
        return "<Scope.CYCLE: 2>"
    elif scope == "<Scope.GLOBAL: 4>":
        return "<Scope.GLOBAL: 3>"
    return scope


def __migrate_datanode(datanode: Dict) -> Dict:
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

    # parent_id has been renamed to owner_id
    try:
        datanode["owner_id"] = datanode.get("owner_id", datanode["parent_id"])
        del datanode["parent_id"]
    except KeyError:
        pass

    # Update Scope enum after Pipeline removal
    datanode["scope"] = __update_scope(datanode["scope"])

    # Update move name attribute to properties dictionary
    datanode["data_node_properties"]["name"] = datanode.pop("name", None)

    if "last_edit_date" not in datanode:
        datanode["last_edit_date"] = datanode.get("last_edition_date")
        if "last_edition_date" in datanode:
            del datanode["last_edition_date"]

    if "edit_in_progress" not in datanode:
        datanode["edit_in_progress"] = datanode.get("edition_in_progress")
        if "edition_in_progress" in datanode:
            del datanode["edition_in_progress"]

    return datanode


def __migrate_datanode_entity(datanode: Dict, data: Dict) -> Dict:
    datanode = __update_parent_ids(datanode, data)
    return __migrate_datanode(datanode)


def __migrate_datanode_config(datanode: Dict) -> Dict:
    if datanode["storage_type"] in ["csv", "json"]:
        datanode["encoding"] = "utf-8"
    return datanode


def __migrate_job(job: Dict) -> Dict:
    # submit_entity_id was not present before 3.0
    job["submit_entity_id"] = job.get("submit_entity_id", None)
    if "subscribers" in job:
        for sub in job["subscribers"]:
            sub["fct_module"], sub["fct_name"] = __migrate_subscriber(sub["fct_module"], sub["fct_name"])
    return job


def __migrate_global_config(config: Dict):
    fields_to_remove = ["clean_entities_enabled"]
    fields_to_move = ["root_folder", "storage_folder", "repository_type", "read_entity_retry"]

    for field in fields_to_remove:
        if field in config["TAIPY"]:
            del config["TAIPY"][field]
    try:
        for field in fields_to_move:
            if field not in config["CORE"]:
                config["CORE"][field] = config["TAIPY"][field]
                del config["TAIPY"][field]
    except KeyError:
        pass

    if "core_version" not in config["CORE"] or config["CORE"]["core_version"] != version("taipy-core"):
        config["CORE"]["core_version"] = version("taipy-core")

    return config


def __migrate_version(version: Dict) -> Dict:
    config_str = version["config"]

    # Remove PIPELINE scope
    config_str = config_str.replace("PIPELINE:SCOPE", "SCENARIO:SCOPE")
    config = json.loads(config_str)

    # remove unused fields and move others from TAIPY to CORE section
    config = __migrate_global_config(config)

    # replace pipelines for tasks
    if "PIPELINE" in config:
        pipelines_section = config["PIPELINE"]
        for id, content in config["SCENARIO"].items():
            tasks = []
            for _pipeline in content["pipelines"]:
                pipeline_id = _pipeline.split(":")[0]
                tasks = pipelines_section[pipeline_id]["tasks"]
            config["SCENARIO"][id]["tasks"] = tasks
            del config["SCENARIO"][id]["pipelines"]
        del config["PIPELINE"]

    for id, content in config["TASK"].items():
        config["TASK"][id] = __migrate_task_config(content, config)

    for id, content in config["DATA_NODE"].items():
        config["DATA_NODE"][id] = __migrate_datanode_config(content)

    version["config"] = json.dumps(config, ensure_ascii=False, indent=0)
    return version


def __migrate_entities(entity_type: str, data: Dict) -> Dict:
    migration_fct = FCT_MIGRATION_MAP.get(entity_type)
    _entities = {k: data[k] for k in data if entity_type in k}

    for k, v in _entities.items():
        if entity_type in {"JOB", "VERSION"}:
            v["data"] = migration_fct(v["data"])  # type: ignore
        else:
            v["data"] = migration_fct(v["data"], data)  # type: ignore
        data[k] = v
    return data


FCT_MIGRATION_MAP = {
    "SCENARIO": __migrate_scenario,
    "TASK": __migrate_task_entity,
    "DATANODE": __migrate_datanode_entity,
    "JOB": __migrate_job,
    "VERSION": __migrate_version,
}


def _migrate(entities: Dict, versions: Optional[Dict] = None) -> Tuple[Dict, Dict]:
    __logger.info("Migrating SCENARIOS")
    entities = __migrate_entities("SCENARIO", entities)

    __logger.info("Migrating TASKS")
    entities = __migrate_entities("TASK", entities)

    __logger.info("Migrating DATANODES")
    entities = __migrate_entities("DATANODE", entities)

    __logger.info("Migrating JOBS")
    entities = __migrate_entities("JOB", entities)

    __logger.info("Migrating VERSION")
    if versions:
        versions = __migrate_entities("VERSION", versions)
    else:
        entities = __migrate_entities("VERSION", entities)
        versions = {}
    return entities, versions
