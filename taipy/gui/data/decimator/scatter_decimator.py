# Copyright 2021-2024 Avaiga Private Limited
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

import numpy as np

from ..utils import Decimator


class ScatterDecimator(Decimator):
    """A decimator designed for scatter charts.

    This algorithm fits the data points into a grid. If multiple points are in the same grid
    cell, depending on the chart configuration, some points are removed to reduce the number
    points being displayed.

    This class can only be used with scatter charts.
    """

    _CHART_MODES = ["markers"]

    def __init__(
        self,
        binning_ratio: t.Optional[float] = None,
        max_overlap_points: t.Optional[int] = None,
        threshold: t.Optional[int] = None,
        zoom: t.Optional[bool] = True,
    ):
        """Initialize a new `ScatterDecimator`.

        Arguments:
            binning_ratio (Optional[float]): the size of the data grid for the algorithm.
                The higher the value, the smaller the grid size.
            max_overlap_points (Optional(int)): the maximum number of points for a single cell
                within the data grid within the algorithm. This dictates how dense a single
                grid cell can be.
            threshold (Optional[int]): The minimum amount of data points before the
                decimation is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
        """
        super().__init__(threshold, zoom)
        binning_ratio = binning_ratio if binning_ratio is not None else 1
        self._binning_ratio = binning_ratio if binning_ratio > 0 else 1
        self._max_overlap_points = max_overlap_points if max_overlap_points is not None else 3

    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        n_rows = data.shape[0]
        mask = np.empty(n_rows, dtype=bool)
        width = payload.get("width", None)
        height = payload.get("height", None)
        if width is None or height is None:
            mask.fill(True)
            return mask
        mask.fill(False)
        grid_x, grid_y = round(width / self._binning_ratio), round(height / self._binning_ratio)
        x_col, y_col = data[:, 0], data[:, 1]
        min_x: float = np.amin(x_col)
        max_x: float = np.amax(x_col)
        min_y: float = np.amin(y_col)
        max_y: float = np.amax(y_col)
        min_max_x_diff, min_max_y_diff = max_x - min_x, max_y - min_y
        x_grid_map = np.rint((x_col - min_x) * grid_x / min_max_x_diff).astype(int)
        y_grid_map = np.rint((y_col - min_y) * grid_y / min_max_y_diff).astype(int)
        z_grid_map = None
        grid_shape = (grid_x + 1, grid_y + 1)
        if len(data[0]) == 3:
            grid_z = grid_x
            grid_shape = (grid_x + 1, grid_y + 1, grid_z + 1)  # type: ignore
            z_col = data[:, 2]
            min_z: float = np.amin(z_col)
            max_z: float = np.amax(z_col)
            min_max_z_diff = max_z - min_z
            z_grid_map = np.rint((z_col - min_z) * grid_z / min_max_z_diff).astype(int)
        grid = np.empty(grid_shape, dtype=int)
        grid.fill(0)
        if z_grid_map is not None:
            for i in np.arange(n_rows):
                if grid[x_grid_map[i], y_grid_map[i], z_grid_map[i]] < self._max_overlap_points:
                    grid[x_grid_map[i], y_grid_map[i], z_grid_map[i]] += 1
                    mask[i] = True
        else:
            for i in np.arange(n_rows):
                if grid[x_grid_map[i], y_grid_map[i]] < self._max_overlap_points:
                    grid[x_grid_map[i], y_grid_map[i]] += 1
                    mask[i] = True
        return mask
