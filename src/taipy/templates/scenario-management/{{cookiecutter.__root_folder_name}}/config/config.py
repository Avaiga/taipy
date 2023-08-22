from algos import clean_data

from taipy import Config, Frequency, Scope


def configure():
    # ##################################################################################################################
    # PLACEHOLDER: Add your scenario configurations here                                                               #
    #                                                                                                                  #
    # Example:                                                                                                         #
    initial_dataset_cfg = Config.configure_csv_data_node("initial_dataset", scope=Scope.CYCLE)
    replacement_type_cfg = Config.configure_data_node("replacement_type", default_data="NO VALUE")
    cleaned_dataset_cfg = Config.configure_csv_data_node("cleaned_dataset")
    clean_data_cfg = Config.configure_task(
        "clean_data",
        function=clean_data,
        input=[initial_dataset_cfg, replacement_type_cfg],
        output=cleaned_dataset_cfg,
    )
    scenario_cfg = Config.configure_scenario(
        "scenario_configuration", task_configs=[clean_data_cfg], frequency=Frequency.DAILY
    )
    return scenario_cfg
    # Comment, remove or replace the previous lines with your own use case                                             #
    # ##################################################################################################################
