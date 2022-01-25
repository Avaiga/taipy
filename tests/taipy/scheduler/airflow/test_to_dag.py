import sys
from datetime import datetime
from importlib import util
from io import StringIO

import pytest

from taipy.config import Config
from taipy.data.manager import DataManager
from taipy.scheduler.scheduler import Scheduler
from taipy.task.manager import TaskManager

if util.find_spec("airflow"):
    from airflow import DAG
    from airflow.operators.python import PythonOperator
else:
    pytest.skip("skipping tests because Airflow is not installed", allow_module_level=True)


from taipy.scheduler.airflow.to_dag import submit, to_dag


def test_single_task():
    single_task = {"path": "", "dag_id": "foo", "storage_folder": "", "tasks": ["task"]}

    expected_dag = DAG(dag_id="foo")

    PythonOperator(task_id="task", python_callable=submit, dag=expected_dag, start_date=datetime(2021, 1, 1))
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

    PythonOperator(
        task_id="task_1", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    PythonOperator(
        task_id="task_2", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    PythonOperator(
        task_id="task_3", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    PythonOperator(
        task_id="task_4", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    PythonOperator(
        task_id="task_5", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )
    PythonOperator(
        task_id="task_6", python_callable=Scheduler.submit, dag=expected_dag, start_date=datetime(2021, 1, 1)
    )

    dag = to_dag(multiple_tasks)
    assert_dag(expected_dag, dag)


def test_submit():
    string_to_copy = "foo"
    input_ = Config.add_data_node("input_data_node")
    output_u = Config.add_data_node("output_data_node")
    task_config = Config.add_task("name_1", input_, return_identity, output_u)
    task = TaskManager().get_or_create(task_config)
    task.input["input_data_node"].write(string_to_copy)
    DataManager().set(task.input["input_data_node"])

    original_path = sys.path
    submit("foo", task.id, Config.global_config().storage_folder)
    assert DataManager().get(task.output["output_data_node"].id).read() == string_to_copy
    sys.path = original_path


def return_identity(input_):
    return input_


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
