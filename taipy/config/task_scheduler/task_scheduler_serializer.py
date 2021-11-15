from dataclasses import dataclass, field
from typing import Optional

from taipy.config.interface import Configurable


@dataclass
class TaskSchedulerSerializer(Configurable):
    NB_OF_WORKERS_NODE = "nb_of_workers"
    EXECUTION_ENV_NODE = "execution_env"
    HOSTNAME_NODE = "hostname"
    LOCAL_EXECUTION_LABEL = "local"
    REMOTE_EXECUTION_LABEL = "remote"

    DEFAULT_HOSTNAME = "localhost"
    DEFAULT_REMOTE_EXECUTION = False
    DEFAULT_PARALLEL_EXECUTION = False

    remote_execution: Optional[bool] = field(default=None)
    parallel_execution: Optional[bool] = field(default=None)
    hostname: Optional[str] = field(default=None)
    _nb_of_workers: int = field(default=-1)

    @property
    def nb_of_workers(self) -> Optional[int]:
        if self._nb_of_workers > 0:
            return self._nb_of_workers
        return None

    def update(self, config):
        nb_of_workers = config.get(self.NB_OF_WORKERS_NODE)
        if nb_of_workers is not None:
            self._set_nb_of_workers(nb_of_workers)
            if not self._is_synchronous():
                self._is_parallel()
        if execution_env := config.get(self.EXECUTION_ENV_NODE):
            self._is_remote(execution_env, config.get(self.HOSTNAME_NODE))

    def export(self):
        env = self.REMOTE_EXECUTION_LABEL if self.remote_execution else self.LOCAL_EXECUTION_LABEL
        conf = {
            self.EXECUTION_ENV_NODE: env,
            self.NB_OF_WORKERS_NODE: self._nb_of_workers,
        }
        if self.remote_execution:
            conf[self.HOSTNAME_NODE] = self.hostname
        return conf

    def _set_nb_of_workers(self, nb_of_workers):
        if nb_of_workers == 0:
            self._nb_of_workers = 1
        elif nb_of_workers == -1:
            self._nb_of_workers = -1
        else:
            self._nb_of_workers = abs(int(nb_of_workers))

    def _is_synchronous(self):
        if self._nb_of_workers == 0 or self._nb_of_workers == 1:
            self.remote_execution = False
            self.parallel_execution = False
            return True
        return False

    def _is_parallel(self):
        self.remote_execution = False
        self.parallel_execution = True

    def _is_remote(self, execution_env, hostname):
        if execution_env == self.REMOTE_EXECUTION_LABEL:
            self.remote_execution = True
            self.parallel_execution = False
        else:
            self.remote_execution = False
        self.hostname = hostname or self.DEFAULT_HOSTNAME
