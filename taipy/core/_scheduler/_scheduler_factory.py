from taipy.core._scheduler._abstract_scheduler import _AbstractScheduler
from taipy.core._scheduler._scheduler import _Scheduler
from taipy.core.common._utils import _load_fct
from taipy.core.config.config import Config


class _SchedulerFactory:
    @classmethod
    def _build_scheduler(cls) -> _AbstractScheduler:
        if Config.job_config._is_default_mode():
            return _Scheduler()

        package = f"taipy.{Config.job_config.mode}._scheduler"
        return _load_fct(package, "Scheduler")()
