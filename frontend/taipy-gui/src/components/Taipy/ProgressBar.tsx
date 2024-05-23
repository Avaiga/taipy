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
import {
    Box,
    CircularProgress,
    CircularProgressProps,
    LinearProgress,
    LinearProgressProps,
    Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useDynamicProperty } from "../../utils/hooks";

interface ProgressBarProps {
    linear?: boolean; //by default - false
    showProgress?: boolean; //by default - false
    value?: number; //progress value
    defaultValue?: number; //default progress value
}

const Progress = (props: ProgressBarProps) => {
    const { linear, showProgress, value, defaultValue } = props;

    const [linearProgress, setLinearProgress] = useState(false);
    const [progressVisible, setProgressVisible] = useState(false);

    const val = useDynamicProperty(props.value, props.defaultValue, undefined);

    useEffect(() => {
        setLinearProgress((progress) => {
            return props.linear !== undefined ? props.linear : progress;
        });
    }, [props.linear, linear]);

    useEffect(() => {
        setProgressVisible((progress_visible) => {
            return props.showProgress !== undefined ? props.showProgress : progress_visible;
        });
    }, [props.showProgress, showProgress]);

    //circular progress element
    function CircularProgressWithLabel(props: CircularProgressProps & { value: number }) {
        return (
            <Box sx={{ position: "relative", display: "inline-flex" }}>
                <CircularProgress variant="determinate" {...props} />
                <Box
                    sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: "absolute",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <Typography variant="caption" component="div" color="text.secondary">
                        {`${Math.round(props.value)}%`}
                    </Typography>
                </Box>
            </Box>
        );
    }

    //linear progress element
    function LinearProgressWithLabel(props: LinearProgressProps & { value: number }) {
        return (
            <Box sx={{ display: "flex", alignItems: "center" }}>
                <Box sx={{ width: "100%", mr: 1 }}>
                    <LinearProgress variant="determinate" {...props} />
                </Box>
                <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">{`${Math.round(props.value)}%`}</Typography>
                </Box>
            </Box>
        );
    }

    if (progressVisible) {
        if (linearProgress) {
            return <LinearProgressWithLabel value={val} />;
        } else {
            return <CircularProgressWithLabel value={val} />;
        }
    } else {
        if (linearProgress) {
            return <LinearProgress />;
        } else {
            return <CircularProgress />;
        }
    }
};

export default Progress;
