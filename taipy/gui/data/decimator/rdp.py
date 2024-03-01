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


class RDP(Decimator):
    """A decimator using the RDP algorithm.

    The RDP algorithm reduces a shape made of line segments into a similar shape with
    less points. This algorithm should be used if the final visual representation is
    prioritized over the performance of the application.

    This class can only be used with line charts.
    """

    _CHART_MODES = ["lines+markers", "lines", "markers"]

    def __init__(
        self,
        epsilon: t.Optional[int] = None,
        n_out: t.Optional[int] = None,
        threshold: t.Optional[int] = None,
        zoom: t.Optional[bool] = True,
    ):
        """Initialize a new `RDP`.

        Arguments:
            epsilon (Optional[int]): The epsilon value for the RDP algorithm. If this value
                is being used, the *n_out* argument is ignored.
            n_out (Optional(int)): The maximum number of points that are displayed after
                decimation. This value is ignored if the epsilon value is used.<br/>
                This process is not very efficient so consider using `LTTB` or `MinMaxDecimator`
                if the provided data has more than 100.000 data points.
            threshold (Optional[int]): The minimum amount of data points before the
                decimation is applied.
            zoom (Optional[bool]): set to True to reapply the decimation
                when zoom or re-layout events are triggered.
        """
        super().__init__(threshold, zoom)
        self._epsilon = epsilon
        self._n_out = n_out

    @staticmethod
    def dsquared_line_points(P1, P2, points):
        """
        Calculate only squared distance, only needed for comparison
        """
        xdiff = P2[0] - P1[0]
        ydiff = P2[1] - P1[1]
        nom = (ydiff * points[:, 0] - xdiff * points[:, 1] + P2[0] * P1[1] - P2[1] * P1[0]) ** 2
        denom = ydiff**2 + xdiff**2
        return np.divide(nom, denom)

    @staticmethod
    def __rdp_epsilon(data, epsilon: int):
        # initiate mask array
        # same amount of points
        mask = np.empty(data.shape[0], dtype=bool)

        # Assume all points are valid and falsify those which are found
        mask.fill(True)

        # The stack to select start and end index
        stack: t.List[t.Tuple[int, int]] = [(0, data.shape[0] - 1)]  # type: ignore

        while stack:
            # Pop the last item
            (start, end) = stack.pop()

            # nothing to calculate if no points in between
            if end - start <= 1:
                continue
            # Calculate distance to points
            P1 = data[start]
            P2 = data[end]
            points = data[start + 1 : end]
            dsq = RDP.dsquared_line_points(P1, P2, points)

            mask_eps = dsq > epsilon**2

            if mask_eps.any():
                # max point outside eps
                # Include index that was sliced out
                # Also include the start index to get absolute index
                # And not relative
                mid = np.argmax(dsq) + 1 + start
                stack.append((start, mid))  # type: ignore
                stack.append((mid, end))  # type: ignore
            else:
                # Points in between are redundant
                mask[start + 1 : end] = False
        return mask

    @staticmethod
    def __rdp_points(M, n_out):
        M_len = M.shape[0]

        if M_len <= n_out:
            mask = np.empty(M_len, dtype=bool)
            mask.fill(True)
            return mask
        weights = np.empty(M_len)
        # weights.fill(0)
        weights[0] = float("inf")
        weights[M_len - 1] = float("inf")

        stack = [(0, M_len - 1)]

        while stack:
            (start, end) = stack.pop()
            if end - start <= 1:
                continue
            dsq = RDP.dsquared_line_points(M[start], M[end], M[start + 1 : end])
            max_dist_index = np.argmax(dsq) + start + 1
            weights[max_dist_index] = np.amax(dsq)
            stack.append((start, max_dist_index))
            stack.append((max_dist_index, end))
        maxTolerance = np.sort(weights)[M_len - n_out]

        return weights >= maxTolerance

    def decimate(self, data: np.ndarray, payload: t.Dict[str, t.Any]) -> np.ndarray:
        if self._epsilon:
            return RDP.__rdp_epsilon(data, self._epsilon)
        elif self._n_out:
            return RDP.__rdp_points(data, self._n_out)
        raise RuntimeError("RDP Decimator failed to run. Fill in either 'epsilon' or 'n_out' value")
