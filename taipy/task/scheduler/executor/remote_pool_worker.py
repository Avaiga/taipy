from taipy.config.config import Config
from taipy.task.scheduler.executor.remote_pool_executor import RemotePoolExecutor

if __name__ == "__main__":
    job_config = Config.job_config()
    RemotePoolExecutor(None, job_config.hostname).as_worker()
