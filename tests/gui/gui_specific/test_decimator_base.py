# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from unittest import mock

import numpy as np
import pandas as pd

from taipy.gui.data.decimator.base import Decimator


class _TestDecimator(Decimator):
    _CHART_MODES = ["markers", "lines"]

    def __init__(
        self,
        threshold: t.Optional[int] = None,
        zoom: t.Optional[bool] = True,
        mask: t.Optional[t.List[bool]] = None,
        raise_on_decimate: bool = False,
    ):
        super().__init__(threshold=threshold, zoom=zoom)
        self.mask = mask
        self.raise_on_decimate = raise_on_decimate
        self.last_points: t.Any = None
        self.last_payload: t.Any = None

    def _decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        if self.raise_on_decimate:
            raise RuntimeError("boom")
        self.last_points = data
        self.last_payload = payload
        if self.mask is None:
            return np.array([True] * len(data))
        return np.array(self.mask[: len(data)])


def _build_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": [0, 1, 2, 3, 4],
            "y": [10, 20, 30, 40, 50],
            "z": [1, 2, 3, 4, 5],
            "extra": ["a", "b", "c", "d", "e"],
        }
    )


def test_is_applicable_with_warning_and_threshold_branches():
    decimator = _TestDecimator(threshold=None)

    with mock.patch("taipy.gui.data.decimator.base._warn") as warn_mock:
        assert decimator._is_applicable([1, 2, 3], nb_rows_max=2, chart_mode="unsupported") is True
        warn_mock.assert_called_once()

    assert decimator._is_applicable([1, 2, 3], nb_rows_max=3, chart_mode="markers") is False

    threshold_decimator = _TestDecimator(threshold=2)
    assert threshold_decimator._is_applicable([1, 2, 3], nb_rows_max=1, chart_mode="markers") is True
    assert threshold_decimator._is_applicable([1, 2], nb_rows_max=1, chart_mode="markers") is False


def test_df_relayout_returns_original_df_for_unsupported_chart_mode():
    decimator = _TestDecimator()
    dataframe = _build_dataframe()

    with mock.patch("taipy.gui.data.decimator.base._warn") as warn_mock:
        result_df, is_copied = decimator._df_relayout(
            dataframe, "x", "y", "bar", x0=0, x1=4, y0=10, y1=50, is_copied=False
        )

    warn_mock.assert_called_once()
    assert result_df is dataframe
    assert is_copied is False


def test_df_relayout_filters_markers_and_drops_temp_index_column():
    decimator = _TestDecimator()
    dataframe = _build_dataframe()

    result_df, is_copied = decimator._df_relayout(
        dataframe, None, "y", "markers", x0=1, x1=4, y0=15, y1=45, is_copied=False
    )

    assert is_copied is True
    assert list(result_df["y"]) == [30, 40]
    assert "tAiPy_index_0" not in result_df.columns
    assert "tAiPy_index_0" not in dataframe.columns


def test_df_relayout_ignores_y_axis_in_lines_mode():
    decimator = _TestDecimator()
    dataframe = _build_dataframe()

    result_df, _ = decimator._df_relayout(
        dataframe, "x", "y", "lines", x0=1, x1=4, y0=35, y1=36, is_copied=False
    )

    assert list(result_df["x"]) == [2, 3]


def test_df_apply_decimator_uses_generated_index_column_when_x_is_missing():
    decimator = _TestDecimator(mask=[True, False, True, False, False])
    dataframe = _build_dataframe()

    result_df, is_copied = decimator._df_apply_decimator(
        dataframe, None, "y", "", payload={"width": 100}, is_copied=False
    )

    assert is_copied is False
    assert list(result_df["y"]) == [10, 30]
    assert decimator.last_points.shape == (5, 2)
    assert list(decimator.last_points[:, 0]) == [0, 1, 2, 3, 4]


def test_on_decimate_df_applies_decimator_and_filters_columns():
    decimator = _TestDecimator(threshold=None, mask=[True, True, False, False, False])
    dataframe = _build_dataframe()
    instance_payload = {"decimator": "d1", "xAxis": "x", "yAxis": "y", "zAxis": "", "chartMode": "markers"}
    payload = {"width": 2}

    result_df, is_applied, is_copied = decimator._on_decimate_df(
        dataframe, instance_payload, payload, is_copied=False, filter_unused_columns=True
    )

    assert is_applied is True
    assert is_copied is False
    assert list(result_df.columns) == ["x", "y"]
    assert len(result_df) == 2


def test_on_decimate_df_warns_when_apply_decimator_raises():
    decimator = _TestDecimator(threshold=None, raise_on_decimate=True)
    dataframe = _build_dataframe()
    instance_payload = {"decimator": "d1", "xAxis": "x", "yAxis": "y", "zAxis": "", "chartMode": "markers"}
    payload = {"width": 2}

    with mock.patch("taipy.gui.data.decimator.base._warn") as warn_mock:
        result_df, is_applied, _ = decimator._on_decimate_df(dataframe, instance_payload, payload)

    assert is_applied is False
    assert list(result_df.columns) == ["x", "y"]
    warn_mock.assert_called_once()


def test_on_decimate_uses_user_defined_function_and_fallback_on_error():
    decimator = _TestDecimator()
    dataframe = _build_dataframe()
    instance_payload = {"decimator": "d1", "xAxis": "x", "yAxis": "y", "zAxis": "", "chartMode": "markers"}
    payload = {"width": 999}

    decimator._Decimator__user_defined_on_decimate = lambda *args: ("ok", True, False)  # type: ignore[attr-defined]
    assert decimator._on_decimate(dataframe, instance_payload, payload) == ("ok", True, False)

    def _raise(*args):
        raise RuntimeError("on_decimate error")

    decimator._Decimator__user_defined_on_decimate = _raise  # type: ignore[attr-defined]
    with mock.patch("taipy.gui.data.decimator.base._warn") as warn_mock:
        result_df, is_applied, _ = decimator._on_decimate(dataframe, instance_payload, payload)

    assert is_applied is False
    assert list(result_df.columns) == ["x", "y"]
    warn_mock.assert_called_once()


def test_apply_decimator_uses_user_defined_function_and_fallback_on_error():
    decimator = _TestDecimator(mask=[True, False, False, False, False])
    dataframe = _build_dataframe()

    decimator._Decimator__user_defined_apply_decimator = (  # type: ignore[attr-defined]
        lambda *args: (dataframe.head(1), True)
    )
    result_df, is_copied = decimator._apply_decimator(dataframe, "x", "y", "", {}, False)
    assert len(result_df) == 1
    assert is_copied is True

    def _raise(*args):
        raise RuntimeError("apply_decimator error")

    decimator._Decimator__user_defined_apply_decimator = _raise  # type: ignore[attr-defined]
    with mock.patch("taipy.gui.data.decimator.base._warn") as warn_mock:
        result_df, is_copied = decimator._apply_decimator(dataframe, "x", "y", "", {}, False)

    assert len(result_df) == 1
    assert is_copied is False
    warn_mock.assert_called_once()
