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

import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import { useDynamicProperty } from "../../utils/hooks";

interface ProgressBarProps {
    linear?: boolean; //by default - false
    showValue?: boolean; //by default - false
    value?: number; //progress value
    defaultValue?: number; //default progress value
    render?: boolean;
    defaultRender?: boolean;
}

const Progress = (props: ProgressBarProps) => {
    const { linear, showValue } = props;

    const value = useDynamicProperty(props.value, props.defaultValue, undefined);
    const render = useDynamicProperty(props.render, props.defaultRender, undefined);

    if (!render) {
        return null;
    }

    return showValue && value !== undefined ? (
        linear ? (
            <Box sx={{ display: "flex", alignItems: "center" }}>
                <Box sx={{ width: "100%", mr: 1 }}>
                    <LinearProgress variant="determinate" value={value} />
                </Box>
                <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">{`${Math.round(value)}%`}</Typography>
                </Box>
            </Box>
        ) : (
            <Box sx={{ position: "relative", display: "inline-flex" }}>
                <CircularProgress variant="determinate" value={value} />
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
                        {`${Math.round(value)}%`}
                    </Typography>
                </Box>
            </Box>
        )
    ) : linear ? (
        <LinearProgress variant={value === undefined ? "indeterminate" : "determinate"} value={value} />
    ) : (
        <CircularProgress variant={value === undefined ? "indeterminate" : "determinate"} value={value} />
    );
};

export default Progress;
