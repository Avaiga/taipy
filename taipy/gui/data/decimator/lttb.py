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

import typing as t

import numpy as np

from ..utils import Decimator


class LTTB(Decimator):
    """A decimator using the LTTB algorithm.

    The LTTB algorithm is an high performance algorithm that significantly reduces the number of
    data points. It can work very well with time-series data to show trends using by using only
    a few data points.

    This class can only be used with line charts.
    """

    _CHART_MODES = ["lines+markers"]

    def __init__(self, n_out: int, threshold: t.Optional[int] = None, zoom: t.Optional[bool] = True) -> None:
        """Initialize a new `LTTB`.

        Arguments:
            n_out (int): The maximum number of points that will be displayed after decimation.
            threshold (Optional[int]): The minimum amount of data points before the
                decimation is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
        """
        super().__init__(threshold, zoom)
        self._n_out = n_out

    @staticmethod
    def _areas_of_triangles(a, bs, c):
        bs_minus_a = bs - a
        a_minus_bs = a - bs
        return 0.5 * abs((a[0] - c[0]) * (bs_minus_a[:, 1]) - (a_minus_bs[:, 0]) * (c[1] - a[1]))

    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        n_out = self._n_out
        if n_out >= data.shape[0]:
            return np.full(len(data), True)

        if n_out < 3:
            raise ValueError("Can only down-sample to a minimum of 3 points")

        # Split data into bins
        n_bins = n_out - 2
        data_bins = np.array_split(data[1:-1], n_bins)

        prev_a = data[0]
        start_pos = 0

        # Prepare output mask array
        # First and last points are the same as in the input.
        out_mask = np.full(len(data), False)
        out_mask[0] = True
        out_mask[len(data) - 1] = True

        # Largest Triangle Three Buckets (LTTB):
        # In each bin, find the point that makes the largest triangle
        # with the point saved in the previous bin
        # and the centroid of the points in the next bin.
        for i in range(len(data_bins)):
            this_bin = data_bins[i]
            next_bin = data_bins[i + 1] if i < n_bins - 1 else data[-1:]
            a = prev_a
            bs = this_bin
            c = next_bin.mean(axis=0)

            areas = LTTB._areas_of_triangles(a, bs, c)
            bs_pos = np.argmax(areas)
            prev_a = bs[bs_pos]
            out_mask[start_pos + bs_pos] = True
            start_pos += len(this_bin)

        return out_mask
