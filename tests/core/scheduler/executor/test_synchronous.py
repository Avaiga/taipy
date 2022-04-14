# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest

from taipy.core._scheduler._executor._synchronous import _Synchronous


def mult(nb1, nb2):
    return nb1 * nb2


def mult_by_two(nb):
    return mult(2, nb)


def test_submit_one_argument():
    res = _Synchronous().submit(mult_by_two, 21)
    assert res.result() == 42


def test_submit_two_arguments():
    res = _Synchronous().submit(mult, 21, 4)
    assert res.result() == 84


def test_submit_two_arguments_in_context_manager():
    with _Synchronous() as pool:
        res = pool.submit(mult, 21, 4)
        assert res.result() == 84


def test_submit_raised():
    res = _Synchronous().submit(mult_by_two, None)

    with pytest.raises(TypeError):
        res.result()
