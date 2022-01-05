import sys
from datetime import datetime
from io import StringIO
from unittest.mock import MagicMock

import pytest

from taipy.config import Config
from taipy.data.manager import DataManager

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.sensors.python import PythonSensor
except ImportError:
    pytest.skip("skipping tests because Airflow is not installed", allow_module_level=True)


from taipy.airflow.to_dag import is_ready, submit, to_dag
from taipy.task import TaskManager, TaskScheduler


def test_single_task():
    single_task = {"path": "", "dag_id": "foo", "storage_folder": "", "tasks": ["task"]}

    expected_dag = DAG(dag_id="foo")

    sensor = PythonSensor(
        task_id="sensor_task",
        python_callable=is_ready,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(task_id="task", python_callable=submit, dag=expected_dag, start_date=datetime(2021, 1, 1))
    sensor >> task

    dag = to_dag(single_task)
    assert_dag(expected_dag, dag)


def test_multiple_tasks():
    multiple_tasks = {
        "path": "",
        "dag_id": "bar",
        "storage_folder": "",
        "tasks": ["task_1", "task_2", "task_3", "task_4", "task_5", "task_6"],
    }

    expected_dag = DAG(dag_id="bar")

    sensor = PythonSensor(
        task_id="sensor_task_1",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_1", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    sensor = PythonSensor(
        task_id="sensor_task_2",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_2", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    sensor = PythonSensor(
        task_id="sensor_task_3",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_3", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    sensor = PythonSensor(
        task_id="sensor_task_4",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_4", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    sensor = PythonSensor(
        task_id="sensor_task_5",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_5", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    sensor = PythonSensor(
        task_id="sensor_task_6",
        python_callable=TaskScheduler.is_blocked,
        dag=expected_dag,
        start_date=datetime(2021, 1, 1),
    )
    task = PythonOperator(
        task_id="task_6", python_callable=TaskScheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    sensor >> task

    dag = to_dag(multiple_tasks)
    assert_dag(expected_dag, dag)


def test_is_ready():
    data_source = Config.add_data_source("data_source")
    task_config = Config.add_task("name_1", data_source, print, [])
    task = TaskManager().get_or_create(task_config)

    original_path = sys.path
    to_insert_in_path = "foo"
    assert not is_ready(to_insert_in_path, task.id, Config.global_config().storage_folder)
    assert to_insert_in_path in sys.path and sys.path not in original_path

    task.input["data_source"].write("ready")
    DataManager().set(task.input["data_source"])
    assert is_ready(to_insert_in_path, task.id, Config.global_config().storage_folder)
    sys.path = original_path


def return_identity(input_):
    return input_


def test_submit():
    string_to_copy = "foo"
    input_ = Config.add_data_source("input_data_source")
    output_u = Config.add_data_source("output_data_source")
    task_config = Config.add_task("name_1", input_, return_identity, output_u)
    task = TaskManager().get_or_create(task_config)
    task.input["input_data_source"].write(string_to_copy)
    DataManager().set(task.input["input_data_source"])

    original_path = sys.path
    submit("foo", task.id, Config.global_config().storage_folder)
    assert DataManager().get(task.output["output_data_source"].id).read() == string_to_copy
    sys.path = original_path


def assert_dag(expected_dag, generated_dag):
    assert expected_dag.dag_id == generated_dag.dag_id

    expected_dag_tree = get_tree_view(expected_dag)
    generated_dag_tree = get_tree_view(generated_dag)

    assert expected_dag_tree == generated_dag_tree


def get_tree_view(dag):
    previous_stdout = sys.stdout
    sys.stdout = stdout = StringIO()
    dag.tree_view()
    tree_view = stdout.getvalue()
    sys.stdout = previous_stdout
    return tree_view
