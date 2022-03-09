from taipy.core.config.config import Config


def test_job_config():
    assert Config.job_config.mode == "standalone"
    assert Config.job_config.nb_of_workers == 1

    Config._set_job_config(nb_of_workers=2)
    assert Config.job_config.mode == "standalone"
    assert Config.job_config.nb_of_workers == 2
