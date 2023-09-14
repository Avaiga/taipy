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


from typing import List, Optional


class ConfigCoreVersionMismatched(Exception):
    """Raised if core version in Config does not match with the version of Taipy Core."""

    def __init__(self, config_core_version: str, core_version: str) -> None:
        self.message = (
            f"Core version {config_core_version} in Config does not match with version of Taipy Core {core_version}."
        )


class CycleAlreadyExists(Exception):
    """Raised if it is trying to create a Cycle that has already exists."""


class NonExistingCycle(Exception):
    """Raised if a requested cycle is not known by the Cycle manager."""

    def __init__(self, cycle_id: str):
        self.message = f"Cycle: {cycle_id} does not exist."


class MissingRequiredProperty(Exception):
    """Raised if a required property is missing when creating a Data Node."""


class InvalidDataNodeType(Exception):
    """Raised if a data node storage type does not exist."""


class MultipleDataNodeFromSameConfigWithSameOwner(Exception):
    """
    Raised if there are multiple data nodes from the same data node configuration and the same owner identifier.
    """


class NoData(Exception):
    """Raised if a data node is read before it has been written.

    This exception can be raised by `DataNode.read_or_raise()^`.
    """


class UnknownDatabaseEngine(Exception):
    """Raised if the database engine is not known when creating a connection with a SQLDataNode."""


class UnknownParquetEngine(Exception):
    """Raised if the parquet engine is not known or not supported when create a ParquetDataNode."""


class UnknownCompressionAlgorithm(Exception):
    """Raised if the compression algorithm is not supported by ParquetDataNode."""


class NonExistingDataNode(Exception):
    """Raised if a requested DataNode is not known by the DataNode Manager."""

    def __init__(self, data_node_id: str):
        self.message = f"DataNode: {data_node_id} does not exist."


class DataNodeIsBeingEdited(Exception):
    """Raised if a DataNode is being edited."""

    def __init__(self, data_node_id: str, editor_id: Optional[str] = None):
        self.message = f"DataNode {data_node_id} is being edited{ ' by ' + editor_id if editor_id else ''}."


class NonExistingDataNodeConfig(Exception):
    """Raised if a requested DataNodeConfig is not known by the DataNode Manager."""

    def __init__(self, data_node_config_id: str):
        self.message = f"Data node config: {data_node_config_id} does not exist."


class NonExistingExcelSheet(Exception):
    """Raised if a requested Sheet name does not exist in the provided Excel file."""

    def __init__(self, sheet_name: str, excel_file_name: str):
        self.message = f"{sheet_name} does not exist in {excel_file_name}."


class ExposedTypeLengthMismatch(Exception):
    """Raised if length of exposed type list does not match with number of sheets in the provided Excel file."""


class SheetNameLengthMismatch(Exception):
    """Raised if length of sheet_name list does not match
    with number of sheets in the data to be written to Excel file."""


class InvalidExposedType(Exception):
    """Raised if an invalid exposed type is provided."""


class InvalidCustomDocument(Exception):
    """Raised if an invalid custom document class is provided to a `MongoCollectionDataNode`."""


class DataNodeConfigIsNotGlobal(Exception):
    """Raised if a DataNode is not global."""

    def __init__(self, data_node_config_id: str):
        self.message = f"Data node config `{data_node_config_id}` does not have GLOBAL scope."


class MissingReadFunction(Exception):
    """Raised if no read function is provided for the GenericDataNode."""


class MissingWriteFunction(Exception):
    """Raised if no write function is provided for the GenericDataNode."""


class JobNotDeletedException(RuntimeError):
    """Raised if there is an attempt to delete a job that cannot be deleted.

    This exception can be raised by `taipy.delete_job()^`.
    """

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} cannot be deleted."


class NonExistingJob(RuntimeError):
    """Raised if a requested job is not known by the Job manager."""

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} does not exist."


class DataNodeWritingError(RuntimeError):
    """Raised if an error happens during the writing in a data node."""


class InvalidSubscriber(RuntimeError):
    """Raised if the loaded function is not valid."""


class InvalidSequenceId(Exception):
    """Raised if a Sequence id can not be broken down."""

    def __init__(self, sequence_id: str):
        self.message = f"Sequence: {sequence_id} is invalid."


class InvalidSequence(Exception):
    """Raised if a Sequence is not a connected Directed Acyclic Graph."""

    def __init__(self, sequence_id: str):
        self.message = f"Sequence: {sequence_id} is not a connected Directed Acyclic Graph."


class NonExistingSequence(Exception):
    """Raised if a requested Sequence is not known by the Sequence Manager."""

    def __init__(self, sequence_id: str):
        self.message = f"Sequence: {sequence_id} does not exist."


class SequenceBelongsToNonExistingScenario(Exception):
    """Raised if a Sequence does not belong to an existing Scenario."""

    def __init__(self, sequence_id: str, scenario_id: str):
        self.message = f"Sequence: {sequence_id} belongs to a non-existing Scenario: {scenario_id}."


class SequenceTaskDoesNotExistInScenario(Exception):
    """Raised if Tasks of a Sequence do not exist in the same Scenario that the Sequence belongs to."""

    def __init__(self, task_ids: List[Optional[str]], sequence_name: str, scenario_id: str):
        self.message = f"Tasks {task_ids} of Sequence {sequence_name} does not exist in Scenario {scenario_id}."


class SequenceTaskConfigDoesNotExistInSameScenarioConfig(Exception):
    """Raised if TaskConfigs of a Sequence do not exist in the same ScenarioConfig that the Sequence belongs to."""

    def __init__(self, task_config_ids: List[Optional[str]], sequence_name: str, scenario_config_id: str):
        self.message = f"TaskConfig {task_config_ids} of Sequence name {sequence_name} "
        self.message += f"does not exist in ScenarioConfig {scenario_config_id}."


class NonExistingSequenceConfig(Exception):
    """Raised if a requested Sequence configuration is not known by the Sequence Manager."""

    def __init__(self, sequence_config_id: str):
        self.message = f"Sequence config: {sequence_config_id} does not exist."


class MultipleSequenceFromSameConfigWithSameOwner(Exception):
    """Raised if it exists multiple sequences from the same sequence config and with the same _owner_id_."""


class ModelNotFound(Exception):
    """Raised when trying to fetch a non-existent model.

    This exception can be raised by `taipy.get()^` and `taipy.delete()^`.
    """

    def __init__(self, model_name: str, model_id: str):
        self.message = f"A {model_name} model with id {model_id} could not be found."


class NonExistingScenario(Exception):
    """Raised if a requested scenario is not known by the Scenario Manager."""

    def __init__(self, scenario_id: str):
        self.message = f"Scenario: {scenario_id} does not exist."


class NonExistingScenarioConfig(Exception):
    """Raised if a requested scenario configuration is not known by the Scenario Manager.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """

    def __init__(self, scenario_config_id: str):
        self.message = f"Scenario config: {scenario_config_id} does not exist."


class InvalidSscenario(Exception):
    """Raised if a Scenario is not a Directed Acyclic Graph."""

    def __init__(self, scenario_id: str):
        self.message = f"Scenario: {scenario_id} is not a Directed Acyclic Graph."


class DoesNotBelongToACycle(Exception):
    """Raised if a scenario without any cycle is promoted as primary scenario."""


class DeletingPrimaryScenario(Exception):
    """Raised if a primary scenario is deleted."""


class DifferentScenarioConfigs(Exception):
    """Raised if scenario comparison is requested on scenarios with different scenario configs.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class InsufficientScenarioToCompare(Exception):
    """Raised if too few scenarios are requested to be compared.

    Scenario comparison need at least two scenarios to compare.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class NonExistingComparator(Exception):
    """Raised if a scenario comparator does not exist.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class UnauthorizedTagError(Exception):
    """Must provide an authorized tag."""


class DependencyNotInstalled(Exception):
    """Raised if a package is missing."""

    def __init__(self, package_name: str):
        self.message = f"""
        Package '{package_name}' should be installed.
        Run 'pip install taipy[{package_name}]' to installed it.
        """


class NonExistingTask(Exception):
    """Raised if a requested task is not known by the Task Manager."""

    def __init__(self, task_id: str):
        self.message = f"Task: {task_id} does not exist."


class NonExistingTaskConfig(Exception):
    """Raised if a requested task configuration is not known by the Task Manager."""

    def __init__(self, id: str):
        self.message = f"Task config: {id} does not exist."


class MultipleTaskFromSameConfigWithSameOwner(Exception):
    """Raised if there are multiple tasks from the same task configuration and the same owner identifier."""


class OrchestratorNotBuilt(Exception):
    """Raised if the orchestrator was not built in the OrchestratorFactory"""


class ModeNotAvailable(Exception):
    """Raised if the mode in JobConfig is not supported."""


class InvalidExportPath(Exception):
    """Raised if the export path is not valid."""


class NonExistingVersion(Exception):
    """Raised if request a Version that is not known by the Version Manager."""

    def __init__(self, version_number: str):
        self.message = f"Version '{version_number}' does not exist."


class VersionIsNotProductionVersion(Exception):
    """Raised if the version is not a production version."""


class ConflictedConfigurationError(Exception):
    """Conflicts have been detected between the current and previous Configurations."""


class InvalidEventAttributeName(Exception):
    """
    Raised if the attribute doesn't exist or an attribute name is provided
    when operation is either creation, deletion or submission
    """


class InvalidEventOperation(Exception):
    """Raised when operation doesn't belong to the entity"""


class FileCannotBeRead(Exception):
    """Raised when a file cannot be read."""


class _SuspiciousFileOperation(Exception):
    pass
