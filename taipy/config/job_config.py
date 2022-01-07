from typing import Any, Dict, Optional


class JobConfig:
    """
    Holds configuration fields related to the job executions.

    Parameters:
        mode (str): Field representing the Taipy operating mode. Possible values are "standalone", "airflow". Default
            value: "standalone".
        remote_execution (bool): Boolean to activate/deactivate the job executions on a remote environment.
            Default value is false.
            TO BE REMOVED IN THE NEXT TAIPY VERSION.
        parallel_execution (bool): Boolean to activate/deactivate the possibility to run multiple tasks in parallel.
            Default value is false.
        nb_of_workers (int): Maximum number of running workers to execute jobs. Must be a positive integer.
            Default value : 1
        hostname (str): Hostname. Default value is "localhost".
        airflow_dag_folder (str): Folder name used to store the dags to be read by airflow if airflow mode is activated.
            Default value is ".dag/". It is used in conjunction with the GlobalAppConfig.root_folder field. That means
            the path for the airflow dag folder is <root_folder><airflow_dag_folder> (Default path : "./taipy/.dag/").
        airflow_folder (str): Folder name used by airflow if airflow mode is activated. Default value is ".airflow/". It
            is used in conjunction with the GlobalAppConfig.root_folder field. That means the path for the airflow dag
            folder is <root_folder><airflow_dag_folder> (Default path : "./taipy/.airflow/").
        airflow_db_endpoint (str): Airflow database endpoint used if airflow mode is activated. Default value is None.
        start_airflow (bool): Allow Taipy to start Airflow if not alreay started.
        airflow_api_retry (int): Retry pattern on Airflow APIs.
        properties (dict): Dictionary of additional properties.

    """

    MODE_KEY = "mode"
    MODE_VALUE_STANDALONE = "standalone"
    MODE_VALUE_AIRFLOW = "airflow"
    DEFAULT_MODE = MODE_VALUE_STANDALONE

    REMOTE_EXECUTION_KEY = "remote_execution"
    REMOTE_EXECUTION_TRUE = True
    REMOTE_EXECUTION_FALSE = False
    DEFAULT_REMOTE_EXECUTION = REMOTE_EXECUTION_FALSE

    PARALLEL_EXECUTION_KEY = "parallel_execution"
    PARALLEL_EXECUTION_TRUE = True
    PARALLEL_EXECUTION_FALSE = False
    DEFAULT_PARALLEL_EXECUTION = PARALLEL_EXECUTION_FALSE

    NB_OF_WORKERS_KEY = "nb_of_workers"
    DEFAULT_NB_OF_WORKERS = 1

    HOSTNAME_KEY = "hostname"
    DEFAULT_HOSTNAME = "localhost"

    AIRFLOW_DAG_FOLDER_KEY = "airflow_dag_folder"
    DEFAULT_AIRFLOW_DAG_FOLDER = ".dag/"

    AIRFLOW_FOLDER_KEY = "airflow_folder"
    DEFAULT_AIRFLOW_FOLDER = ".airflow/"

    AIRFLOW_DB_ENDPOINT_KEY = "airflow_db_endpoint"
    DEFAULT_DB_ENDPOINT = None

    START_AIRFLOW_KEY = "start_airflow"
    DEFAULT_START_AIRFLOW = False

    AIRFLOW_API_RETRY_KEY = "airflow_api_retry"
    DEFAULT_AIRFLOW_API_RETRY = 10

    def __init__(
        self,
        mode: str = None,
        remote_execution: bool = None,
        parallel_execution: bool = None,
        nb_of_workers: int = None,
        hostname: str = None,
        airflow_dag_folder: str = None,
        airflow_folder: str = None,
        airflow_db_endpoint: str = None,
        start_airflow: bool = None,
        airflow_api_retry: int = None,
        **properties
    ):
        self.mode = mode

        self.remote_execution = remote_execution
        self.parallel_execution = parallel_execution
        self.nb_of_workers = nb_of_workers
        self.hostname = hostname

        self.airflow_dag_folder = airflow_dag_folder
        self.airflow_folder = airflow_folder
        self.airflow_db_endpoint = airflow_db_endpoint
        self.start_airflow = start_airflow
        self.airflow_api_retry = airflow_api_retry

        self.properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    @classmethod
    def default_config(cls):
        return JobConfig(
            cls.DEFAULT_MODE,
            cls.DEFAULT_REMOTE_EXECUTION,
            cls.DEFAULT_PARALLEL_EXECUTION,
            cls.DEFAULT_NB_OF_WORKERS,
            cls.DEFAULT_HOSTNAME,
            cls.DEFAULT_AIRFLOW_DAG_FOLDER,
            cls.DEFAULT_AIRFLOW_FOLDER,
            cls.DEFAULT_DB_ENDPOINT,
            cls.DEFAULT_START_AIRFLOW,
            cls.DEFAULT_AIRFLOW_API_RETRY,
        )

    def to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self.MODE_KEY] = self.mode
        if self.remote_execution is not None:
            as_dict[self.REMOTE_EXECUTION_KEY] = self.remote_execution
        if self.parallel_execution is not None:
            as_dict[self.PARALLEL_EXECUTION_KEY] = self.parallel_execution
        if self.nb_of_workers is not None:
            as_dict[self.NB_OF_WORKERS_KEY] = self.nb_of_workers
        if self.hostname is not None:
            as_dict[self.HOSTNAME_KEY] = self.hostname
        if self.airflow_dag_folder is not None:
            as_dict[self.AIRFLOW_DAG_FOLDER_KEY] = self.airflow_dag_folder
        if self.airflow_folder is not None:
            as_dict[self.AIRFLOW_FOLDER_KEY] = self.airflow_folder
        if self.airflow_db_endpoint is not None:
            as_dict[self.AIRFLOW_DB_ENDPOINT_KEY] = self.airflow_db_endpoint
        if self.start_airflow is not None:
            as_dict[self.START_AIRFLOW_KEY] = self.start_airflow
        if self.airflow_api_retry is not None:
            as_dict[self.AIRFLOW_API_RETRY_KEY] = self.airflow_api_retry
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]):
        config = JobConfig()
        config.mode = config_as_dict.pop(cls.MODE_KEY, None)
        config.remote_execution = config_as_dict.pop(cls.REMOTE_EXECUTION_KEY, None)
        config.parallel_execution = config_as_dict.pop(cls.PARALLEL_EXECUTION_KEY, None)
        config.nb_of_workers = config_as_dict.pop(cls.NB_OF_WORKERS_KEY, None)
        config.hostname = config_as_dict.pop(cls.HOSTNAME_KEY, None)
        config.airflow_dag_folder = config_as_dict.pop(cls.AIRFLOW_DAG_FOLDER_KEY, None)
        config.airflow_folder = config_as_dict.pop(cls.AIRFLOW_FOLDER_KEY, None)
        config.airflow_db_endpoint = config_as_dict.pop(cls.AIRFLOW_DB_ENDPOINT_KEY, None)
        config.start_airflow = config_as_dict.pop(cls.START_AIRFLOW_KEY, None)
        config.airflow_api_retry = config_as_dict.pop(cls.AIRFLOW_API_RETRY_KEY, None)
        config.properties = config_as_dict
        return config

    def update(self, config_as_dict):
        self.mode = config_as_dict.pop(self.MODE_KEY, self.mode)
        self.remote_execution = config_as_dict.pop(self.REMOTE_EXECUTION_KEY, self.remote_execution)
        self.parallel_execution = config_as_dict.pop(self.PARALLEL_EXECUTION_KEY, self.parallel_execution)
        self.nb_of_workers = config_as_dict.pop(self.NB_OF_WORKERS_KEY, self.nb_of_workers)
        self.hostname = config_as_dict.pop(self.HOSTNAME_KEY, self.hostname)
        self.airflow_dag_folder = config_as_dict.pop(self.AIRFLOW_DAG_FOLDER_KEY, self.airflow_dag_folder)
        self.airflow_folder = config_as_dict.pop(self.AIRFLOW_FOLDER_KEY, self.airflow_folder)
        self.airflow_db_endpoint = config_as_dict.pop(self.AIRFLOW_DB_ENDPOINT_KEY, self.airflow_db_endpoint)
        self.start_airflow = config_as_dict.pop(self.START_AIRFLOW_KEY, self.start_airflow)
        self.airflow_api_retry = config_as_dict.pop(self.AIRFLOW_API_RETRY_KEY, self.airflow_api_retry)
        self.properties.update(config_as_dict)

    def is_standalone(self) -> bool:
        """True if the config is set to standalone execution"""
        return self.mode == self.MODE_VALUE_STANDALONE
