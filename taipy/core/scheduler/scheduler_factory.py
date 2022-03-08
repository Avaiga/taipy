from taipy.core.common._utils import _load_fct
from taipy.core.config.config import Config
from taipy.core.scheduler.abstract_scheduler import AbstractScheduler
from taipy.core.scheduler.scheduler import Scheduler


class SchedulerFactory:
    @classmethod
    def build_scheduler(cls) -> AbstractScheduler:
        if Config.job_config._is_default_mode():
            return Scheduler()

        package = f"taipy.{Config.job_config.mode}.scheduler"
        return _load_fct(package, "Scheduler")()
