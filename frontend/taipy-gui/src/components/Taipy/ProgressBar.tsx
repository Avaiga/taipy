/*
 * Copyright 2021-2024 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React from "react";
import { Box, CircularProgress, LinearProgress } from "@mui/material";
import { useEffect, useState } from "react";

interface ProgressBarProps {
    linear?: boolean; //by default - false
    showProgress?: boolean; //by default - false
    progressBarCount?: number; //by default - 1
}

const Progress = (props: ProgressBarProps) => {
    const { linear, showProgress, progressBarCount } = props;

    const [linearProgress, setLinearProgress] = useState(false);
    const [progressVisible, setProgressVisible] = useState(false);
    const [progressCount, setProgressCount] = useState(1);

    useEffect(() => {
        setLinearProgress((progress) => {
            if (props.linear !== undefined) return props.linear;
            return progress;
        });
    }, [props.linear, linear]);

    useEffect(() => {
        setProgressVisible((progress_visible) => {
            if (props.showProgress !== undefined) return props.showProgress;
            return progress_visible;
        });
    }, [props.showProgress, showProgress]);

    useEffect(() => {
        setProgressCount((progress_count) => {
            if (props.progressBarCount !== undefined) return props.progressBarCount;
            return progress_count;
        });
    }, [props.progressBarCount, progressBarCount]);

    for (let i = 0; i <= progressCount; i++) {
        if (!progressVisible) {
            if (linearProgress)
                return (
                    <Box sx={{ width: "100%" }}>
                        <LinearProgress />
                    </Box>
                );
            return (
                <Box sx={{ display: "flex" }}>
                    <CircularProgress />
                </Box>
            );
        } //else {}
    }
};

export default Progress;
