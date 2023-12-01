# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from typing import List

from src.taipy.config.common.scope import Scope
from src.taipy.core import DataNode, Sequence, SequenceId, Task, TaskId
from src.taipy.core._entity._dag import _DAG


def assert_x(x: int, *nodes):
    for node in nodes:
        assert node.x == x


def assert_y(y: List[int], *nodes):
    for node in nodes:
        assert node.y in y
        y.remove(node.y)


def assert_x_y(x: int, y: List[int], *nodes):
    assert_x(x, *nodes)
    for node in nodes:
        assert node.y in y
        y.remove(node.y)


def assert_edge_exists(src, dest, dag: _DAG):
    list_of_tuples = [(edge.src.entity.id, edge.dest.entity.id) for edge in dag.edges]
    assert (src, dest) in list_of_tuples


class TestDAG:
    def test_get_dag_1(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        data_node_3 = DataNode("baz", Scope.SCENARIO, "s3")
        data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
        data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
        data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
        data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
        task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_3, data_node_4], TaskId("t1"))
        task_2 = Task("garply", {}, print, [data_node_3], [data_node_5], TaskId("t2"))
        task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
        task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
        sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))

        dag = sequence._get_dag()
        # s1 ---             ---> s3 ---> t2 ---> s5 ----
        #       |           |                           |
        #       |---> t1 ---|      -------------------------> t3 ---> s6
        #       |           |      |
        # s2 ---             ---> s4 ---> t4 ---> s7

        assert dag.length == 7
        assert dag.width == 2
        assert dag._grid_length == 7
        assert dag._grid_width == 3
        assert len(dag.nodes) == 11
        assert_x_y(0, [0, 2], dag.nodes["s1"], dag.nodes["s2"])
        assert_x_y(1, [1], dag.nodes["t1"])
        assert_x_y(2, [0, 2], dag.nodes["s3"], dag.nodes["s4"])
        assert_x_y(3, [0, 2], dag.nodes["t2"], dag.nodes["t4"])
        assert_x_y(4, [0, 2], dag.nodes["s5"], dag.nodes["s7"])
        assert_x_y(5, [1], dag.nodes["t3"])
        assert_x_y(6, [1], dag.nodes["s6"])
        assert len(dag.edges) == 11
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("s2", "t1", dag)
        assert_edge_exists("t1", "s3", dag)
        assert_edge_exists("t1", "s4", dag)
        assert_edge_exists("s3", "t2", dag)
        assert_edge_exists("t2", "s5", dag)
        assert_edge_exists("s5", "t3", dag)
        assert_edge_exists("s4", "t3", dag)
        assert_edge_exists("t3", "s6", dag)
        assert_edge_exists("s4", "t4", dag)
        assert_edge_exists("t4", "s7", dag)

    def test_get_dag_2(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
        data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
        data_node_6 = DataNode("quuz", Scope.SCENARIO, "s6")
        data_node_7 = DataNode("corge", Scope.SCENARIO, "s7")
        task_1 = Task("grault", {}, print, [data_node_1, data_node_2], [data_node_4], TaskId("t1"))
        task_2 = Task("garply", {}, print, None, [data_node_5], TaskId("t2"))
        task_3 = Task("waldo", {}, print, [data_node_5, data_node_4], [data_node_6], TaskId("t3"))
        task_4 = Task("fred", {}, print, [data_node_4], [data_node_7], TaskId("t4"))
        sequence = Sequence({}, [task_4, task_2, task_1, task_3], SequenceId("p1"))

        #  6  |   t2 _____
        #  5  |           \
        #  4  |            s5 _________________ t3 _______ s6
        #  3  |   s1 __            _ s4 _____/
        #  2  |        \ _ t1 ____/          \_ t4 _______ s7
        #  1  |        /
        #  0  |   s2 --
        #     |________________________________________________
        #         0        1         2          3          4

        dag = sequence._get_dag()

        assert dag.length == 5
        assert dag.width == 3
        assert dag._grid_length == 5
        assert dag._grid_width == 7
        assert len(dag.nodes) == 10
        assert_x_y(0, [0, 3, 6], dag.nodes["s1"], dag.nodes["s2"], dag.nodes["t2"])
        assert_x_y(1, [2, 4], dag.nodes["t1"], dag.nodes["s5"])
        assert_x_y(2, [3], dag.nodes["s4"])
        assert_x_y(3, [2, 4], dag.nodes["t3"], dag.nodes["t4"])
        assert_x_y(4, [2, 4], dag.nodes["s6"], dag.nodes["s7"])
        assert len(dag.edges) == 9
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("s2", "t1", dag)
        assert_edge_exists("t1", "s4", dag)
        assert_edge_exists("t2", "s5", dag)
        assert_edge_exists("s5", "t3", dag)
        assert_edge_exists("s4", "t3", dag)
        assert_edge_exists("t3", "s6", dag)
        assert_edge_exists("s4", "t4", dag)
        assert_edge_exists("t4", "s7", dag)

    def test_get_dag_3(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        data_node_3 = DataNode("quuz", Scope.SCENARIO, "s3")
        data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
        data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
        data_node_6 = DataNode("corge", Scope.SCENARIO, "s6")
        data_node_7 = DataNode("hugh", Scope.SCENARIO, "s7")

        task_1 = Task("grault", {}, print, [data_node_1, data_node_2, data_node_3], [data_node_4], TaskId("t1"))
        task_2 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t2"))
        task_3 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t3"))
        task_4 = Task("garply", {}, print, output=[data_node_6], id=TaskId("t4"))
        task_5 = Task("bob", {}, print, [data_node_7], None, TaskId("t5"))
        sequence = Sequence({}, [task_5, task_3, task_4, task_1, task_2], SequenceId("p1"))

        #  12 |  s7 __
        #  11 |       \
        #  10 |        \
        #  9  |  t4 _   \_ t5
        #  8  |      \                     ____ t3 ___
        #  7  |       \                   /           \
        #  6  |  s3 _  \__ s6      _ s4 _/             \___ s5
        #  5  |      \            /      \
        #  4  |       \          /        \____ t2
        #  3  |  s2 ___\__ t1 __/
        #  2  |        /
        #  1  |       /
        #  0  |  s1 _/
        #     |________________________________________________
        #         0         1         2          3          4
        dag = sequence._get_dag()

        assert dag.length == 5
        assert dag.width == 5
        assert dag._grid_length == 5
        assert dag._grid_width == 13
        assert len(dag.nodes) == 12

        assert_x_y(
            0, [0, 3, 6, 9, 12], dag.nodes["s1"], dag.nodes["s2"], dag.nodes["s3"], dag.nodes["s7"], dag.nodes["t4"]
        )
        assert_x_y(1, [3, 6, 9], dag.nodes["t1"], dag.nodes["t5"], dag.nodes["s6"])
        assert_x_y(2, [6], dag.nodes["s4"])
        assert_x_y(3, [4, 8], dag.nodes["t2"], dag.nodes["t3"])
        assert_x_y(4, [6], dag.nodes["s5"])
        assert len(dag.edges) == 9
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("s2", "t1", dag)
        assert_edge_exists("s3", "t1", dag)
        assert_edge_exists("t1", "s4", dag)
        assert_edge_exists("s4", "t2", dag)
        assert_edge_exists("s4", "t3", dag)
        assert_edge_exists("t3", "s5", dag)
        assert_edge_exists("t4", "s6", dag)
        assert_edge_exists("s7", "t5", dag)

    def test_get_dag_4(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        data_node_3 = DataNode("quuz", Scope.SCENARIO, "s3")
        data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
        data_node_5 = DataNode("quux", Scope.SCENARIO, "s5")
        data_node_6 = DataNode("corge", Scope.SCENARIO, "s6")

        task_1 = Task("grault", {}, print, [data_node_1, data_node_2, data_node_3], [data_node_4], TaskId("t1"))
        task_2 = Task("waldo", {}, print, [data_node_4], None, id=TaskId("t2"))
        task_3 = Task("fred", {}, print, [data_node_4], [data_node_5], TaskId("t3"))
        task_4 = Task("garply", {}, print, output=[data_node_6], id=TaskId("t4"))
        sequence = Sequence({}, [task_3, task_4, task_1, task_2], SequenceId("p1"))

        #  6  |  t4 __
        #  5  |       \
        #  4  |  s3 _  \__ s6            ______ t3 ___
        #  3  |      \          ___ s4 _/             \___ s5
        #  2  |  s2 __\__ t1 __/        \______ t2
        #  1  |       /
        #  0  |  s1 _/
        #     |________________________________________________
        #         0         1         2          3          4
        dag = sequence._get_dag()

        assert dag.length == 5
        assert dag.width == 4
        assert dag._grid_length == 5
        assert dag._grid_width == 7
        assert len(dag.nodes) == 10

        assert_x_y(0, [0, 2, 4, 6], dag.nodes["s1"], dag.nodes["s2"], dag.nodes["s3"], dag.nodes["t4"])
        assert_x_y(1, [2, 4], dag.nodes["t1"], dag.nodes["s6"])
        assert_x_y(2, [3], dag.nodes["s4"])
        assert_x_y(3, [2, 4], dag.nodes["t2"], dag.nodes["t3"])
        assert_x_y(4, [3], dag.nodes["s5"])
        assert len(dag.edges) == 8
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("s2", "t1", dag)
        assert_edge_exists("s3", "t1", dag)
        assert_edge_exists("t1", "s4", dag)
        assert_edge_exists("s4", "t2", dag)
        assert_edge_exists("s4", "t3", dag)
        assert_edge_exists("t3", "s5", dag)
        assert_edge_exists("t4", "s6", dag)

    def test_get_dag_5(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        task_1 = Task("baz", {}, print, [data_node_1], [data_node_2], TaskId("t1"))
        sequence = Sequence({}, [task_1], SequenceId("p1"))

        #  1  |
        #  0  |  s1 __ t1 __ s2
        #     |_________________
        #         0    1     2
        dag = sequence._get_dag()

        assert dag.length == 3
        assert dag.width == 1
        assert dag._grid_length == 3
        assert dag._grid_width == 1
        assert len(dag.nodes) == 3

        assert_x_y(0, [0], dag.nodes["s1"])
        assert_x_y(1, [0], dag.nodes["t1"])
        assert_x_y(2, [0], dag.nodes["s2"])
        assert len(dag.edges) == 2
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("t1", "s2", dag)

    def test_get_dag_6(self):
        data_node_1 = DataNode("foo", Scope.SCENARIO, "s1")
        data_node_2 = DataNode("bar", Scope.SCENARIO, "s2")
        data_node_3 = DataNode("baz", Scope.SCENARIO, "s3")
        data_node_4 = DataNode("qux", Scope.SCENARIO, "s4")
        task_1 = Task("quux", {}, print, [data_node_1, data_node_2], [data_node_3], TaskId("t1"))
        task_2 = Task("quuz", {}, print, [data_node_2], [data_node_4], TaskId("t2"))
        sequence = Sequence({}, [task_1, task_2], SequenceId("p1"))

        #  2  |
        #     |
        #  1  |  s1 ___ t1 __ s3
        #     |      /
        #  0  |  s2 /__ t2 __ s4
        #     |_________________
        #         0     1     2
        dag = sequence._get_dag()

        assert dag.length == 3
        assert dag.width == 2
        assert dag._grid_length == 3
        assert dag._grid_width == 2
        assert len(dag.nodes) == 6

        assert_x_y(0, [0, 1], dag.nodes["s1"], dag.nodes["s2"])
        assert_x_y(1, [0, 1], dag.nodes["t1"], dag.nodes["t2"])
        assert_x_y(2, [0, 1], dag.nodes["s3"], dag.nodes["s4"])
        assert len(dag.edges) == 5
        assert_edge_exists("s1", "t1", dag)
        assert_edge_exists("s2", "t1", dag)
        assert_edge_exists("t1", "s3", dag)
        assert_edge_exists("s2", "t2", dag)
        assert_edge_exists("t2", "s4", dag)
