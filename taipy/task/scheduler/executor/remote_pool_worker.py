from taipy.config import Config
from taipy.task.scheduler.executor.remote_pool_executor import RemotePoolExecutor

if __name__ == "__main__":
    task_scheduler_config = Config.task_scheduler_configs.create()
    RemotePoolExecutor(None, task_scheduler_config.hostname).as_worker()
