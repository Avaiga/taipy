from taipy import Config

from ..algos.algos import clean_data


def configure():
    initial_dataset_cfg = Config.configure_csv_data_node("initial_dataset")
    replacement_type_cfg = Config.configure_data_node("replacement_type")
    cleaned_dataset_cfg = Config.configure_csv_data_node("cleaned_dataset")

    clean_data_cfg = Config.configure_task(
        "clean_data", function=clean_data, input=[initial_dataset_cfg, replacement_type_cfg], output=cleaned_dataset_cfg
    )
    scenario_cfg = Config.configure_scenario_from_tasks("scenario_configuration", task_configs=[clean_data_cfg])
    return scenario_cfg
