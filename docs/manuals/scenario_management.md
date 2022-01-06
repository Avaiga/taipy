#Scenario management

## Core concepts

### Scenario

!!! abstract "TODO JRM"

### Cycle

!!! abstract "TODO JRM"

### Pipeline

!!! abstract "TODO JRM"

### Task

!!! abstract "TODO JRM"

### Data source

!!! abstract "TODO JRM"

### Job

!!! abstract "TODO JRM"

## Configuration

Taipy is an application builder. The purpose of configuring the application back end is to describe the user
application entities and how they behave at runtime.

The configuration includes configuration for global application, job executions, scenarios, pipelines, tasks and data
sources. As an example, the data source configurations may have name, storage type, credentials, format, path, scope,
or any custom property.

!!! info "Four methods to configure taipy are possible:"

        - A default configuration
        - A Python configuration
        - A file configuration using toml file format
        - An environment variable configuration

These methods are described below.

### Default configuration

The first method is the default configuration and is directly provided by the Taipy library. It allows the developer to
run the application in the most basic way (running in localhost, storing data on the local file system, executing tasks
sequentially and synchronously, ....). Nothing is needed from the user at this point.
Here is the toml export file of all (not None) default values :

```py linenums="1"

    [TAIPY]
    notification = false
    root_folder = "./taipy/"
    storage_folder = ".data/"

    [JOB]
    mode = "standalone"
    remote_execution = false
    parallel_execution = false
    nb_of_workers = "1"
    hostname = "localhost"
    airflow_dag_folder = ".dag/"
    airflow_folder = ".airflow/"

    [DATA_SOURCE.default]
    storage_type = "pickle"
    scope = "PIPELINE"

    [TASK.default]
    inputs = []
    outputs = []

    [PIPELINE.default]
    tasks = []

    [SCENARIO.default]
    pipelines = []

```

### Code configuration

Then, a code configuration can be done on a Python file directly when designing the pipelines and scenarios. This
configuration can simply be done by importing the Config class and by calling the various methods. It is made to be
used during the application development phase. It overrides the default configuration: In case some values are not
provided, the default configuration applies.

!!! example "Example"

        ```py linenums="1"
        dataset_cfg =Config.add_data_source(name="dataset", storage_type="csv", path="./the/path/to/my/dataset.csv")
        task_cfg = Config.add_task(name="my_task", inputs=data_set_cfg, my_function, outputs=[])
        ```

### Explicit file configuration

Taipy also provides file configuration. Indeed, a toml file can be explicitly provided by the developer to the Taipy
application using Python coding such as :

```py

    Config.load("folder/config.toml")

```

This file configuration overrides the code configuration (and the default configuration).
Here is an example of a toml file :

```py linenums="1"

    [TAIPY]
    version=0.5.5

    [JOB]
    mode = "remote"
    nb_of_workers = 5

    [DATA_SOURCE.Default]
    storage=local_file_system
    type=embedded

    [DATA_SOURCE.Historical_data_set]
    type=csv
    path="folder/subfolder/file.csv"

```

### Environment variable configuration

Finally, if the environment variable TAIPY_CONFIG_PATH is defined with the path of a toml config, Taipy will
automatically load the file and override the previous configurations (explicit file configuration, code configuration
and default configuration).

### Export configuration

Taipy also provides a method to export the configuration applied after the compilation of all the configurations
(default, Python code, explicit file, and environment variable configurations) which is the result of the overwriting.

```py linenums="1"


    [TAIPY]
    notification = true
    broker_endpoint = "my_broker_end_point"
    root_folder = "./root/"
    storage_folder = "./data/"

    [JOB]
    mode = "standalone"
    remote_execution = false
    parallel_execution = false
    nb_of_workers = "1"
    hostname = "localhost"
    airflow_dag_folder = "./dag/"
    airflow_folder = "./airflow"
    airflow_db_endpoint = "db"

    [DATA_SOURCE.default]
    custom = "default_custom_property"

    [DATA_SOURCE.dataset]
    storage_type = "csv"
    custom = "custom property"
    Path = "the/path/to/my/dataset.csv"

    [DATA_SOURCE.forecasts]
    storage_type = "csv"
    Path = "the/path/to/my/forecasts.csv"

    [DATA_SOURCE.date]
    scope = "SCENARIO"
    default_data = "15/03/2022"

    [TASK.t1]
    inputs = [ "dataset", "date"]
    outputs = [ "forecasts"]
    description = "my description"

    [PIPELINE.p1]
    tasks = [ "t1",]
    cron = "daily"

    [SCENARIO.s1]
    pipelines = [ "p1",]
    frequency = "DAILY"
    owner = "John Doe"

```

### Workflow

Here is a possible example of a workflow for the developer.

!!! example "Example"

        1. First as a developer, I am designing and developing my taipy application. I don’t really need to care about
        configuration, so I use the simple default configuration.

        2. Then, I am testing the application built. At this step, I need my application to have a more realistic
        behavior like real data. For that, I need more configuration. I can specify for my specific input dataset what
        file to use. I am using the Python code configuration for that.

        3. Then, once I am happy with my application running on local, I am deploying it to a remote environment for
        testing and debugging the application. This is on a dedicated environment made for testing deployment and for integration testing.
        I can use an explicit file configuration. I can easily update the file if necessary to be efficient in
        debugging, without changing the code directly.

        4. Once the step 3 are done, I want to be able to deploy a released and tagged version of my application on
        several remote environments (e.g. pre-production, production). I am creating one file per remote environment
        with a few values that differ from the step 3, and on each environment, I am setting a different environment variable value to point to the right configuration file.

### Configuration fields

!!! abstract "TODO JRM"

    -   Add reference to the ref manual
    -   Describe config nodes (Global, job, data source, ...)
    -   List all the fields and for each field provide possible values, examples

## Scenario Management

!!! abstract "TODO JRM"
