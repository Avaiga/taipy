from taipy import Config, Frequency, Scope


def clean_data(df, replacement_type):
    df = df.fillna(replacement_type)
    return df


def configure():
    initial_dataset_cfg = Config.configure_csv_data_node("initial_dataset", scope=Scope.CYCLE)
    replacement_type_cfg = Config.configure_data_node("replacement_type", default_data="NO VALUE")
    cleaned_dataset_cfg = Config.configure_csv_data_node("cleaned_dataset")


    clean_data_cfg = Config.configure_task("clean_data",
                                           function=clean_data,
                                           input=[initial_dataset_cfg, replacement_type_cfg],
                                           output=cleaned_dataset_cfg)

    scenario_cfg = Config.configure_scenario_from_tasks("scenario_configuration",
                                                        task_configs=[clean_data_cfg],
                                                        frequency=Frequency.DAILY)
    return scenario_cfg
