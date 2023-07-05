from taipy import Config


def configure():
    Config.load("config/config.toml")
    return Config.scenarios["scenario_configuration"]
