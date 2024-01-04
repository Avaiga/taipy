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


class MinMaxDecimator(Decimator):
    """A decimator using the MinMax algorithm.

    The MinMax algorithm is an efficient algorithm that preserves the peaks within the data. It
    can work very well with noisy signal data where data peeks need to be highlighted.

    This class can only be used with line charts.
    """

    _CHART_MODES = ["lines+markers", "lines", "markers"]

    def __init__(self, n_out: int, threshold: t.Optional[int] = None, zoom: t.Optional[bool] = True):
        """Initialize a new `MinMaxDecimator`.

        Arguments:
            n_out (int): The maximum number of points that will be displayed after decimation.
            threshold (Optional[int]): The minimum amount of data points before the
                decimation is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
        """
        super().__init__(threshold, zoom)
        self._n_out = n_out // 2

    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        if self._n_out >= data.shape[0]:
            return np.full(len(data), False)
        # Create a boolean mask
        x = data[:, 0]
        y = data[:, 1]
        num_bins = self._n_out
        pts_per_bin = x.size // num_bins
        # Create temp to hold the reshaped & slightly cropped y
        y_temp = y[: num_bins * pts_per_bin].reshape((num_bins, pts_per_bin))
        # use argmax/min to get column locations
        cc_max = np.argmax(y_temp, axis=1)
        cc_min = np.argmin(y_temp, axis=1)
        rr = np.arange(0, num_bins)
        # compute the flat index to where these are
        flat_max = cc_max + rr * pts_per_bin
        flat_min = cc_min + rr * pts_per_bin
        mm_mask = np.full((x.size,), False)
        mm_mask[flat_max] = True
        mm_mask[flat_min] = True
        return mm_mask
